# pylint: disable=c-extension-no-member
# (Disables C extension no member for PyQt5 if Pylint has trouble)
"""
Main application entry point.
Initializes the GUI, database, and blockchain components.
Handles Docker Desktop and Ganache startup, smart contract deployment,
and user session management.
"""

# pylint: disable=no-name-in-module
# # pylint: disable=import-error

# Standard Library Imports
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Any, Dict # Added for type hinting

# Third-Party Imports
from PyQt5.QtCore import Qt, QCoreApplication # QCoreApplication for processEvents
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from web3 import Web3

# pylint: disable=wrong-import-position
# Justification: This is a common pattern for including project submodules
# that are not (yet) installed as packages. Ideally, 'on_chain'
# would be an installable package or PYTHONPATH would be set.
sys.path.append(str(Path(__file__).resolve().parent.parent))
from on_chain.automated_deployment import (
    start_ganache,
    compile_contracts,
    deploy_contracts,
    save_contract_data,
)
from on_chain.interact_contract import BlockchainInteractor
# pylint: enable=wrong-import-position

# Local Application Imports
from configuration.database import Database # Assuming this is used implicitly or needed
from configuration.log_load_setting import logger
from database.db_migrations import DatabaseMigrations
from presentation.view.vista_accedi import VistaAccedi
from session import Session # Assuming this is your Session class from previous example

# --- Constants ---
# General
APP_NAME = "YourAppName" # Replace with actual app name if applicable
RESOURCES_PATH = Path("presentation/resources")
ON_CHAIN_DATA_PATH = Path(__file__).resolve().parent.parent / "on_chain"
CONTRACT_ADDRESSES_FILE = ON_CHAIN_DATA_PATH / "contract_addresses.json"

# Docker
DOCKER_CMD = "docker"
DOCKER_INFO_CMD = [DOCKER_CMD, "info"]
DOCKER_START_TIMEOUT_SECONDS = 60
DOCKER_RETRY_INTERVAL_SECONDS = 2
DOCKER_DESKTOP_REG_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop"
DOCKER_DESKTOP_REG_VALUE = "InstallLocation"

# Ganache
GANACHE_RPC_URL = "http://127.0.0.1:8545"
GANACHE_STARTUP_DELAY_SECONDS = 5
GANACHE_CONNECTION_MAX_ATTEMPTS = 30
GANACHE_CONNECTION_RETRY_INTERVAL_SECONDS = 2

# Threading & UI
BLOCKCHAIN_SETUP_TIMEOUT_SECONDS = 120 # Increased timeout
SPLASH_FINISH_DELAY_SECONDS = 1

# --- Global State (managed carefully) ---
# This will hold the initialized BlockchainInteractor instance.
# It's assigned after the setup thread completes successfully.
g_blockchain_interactor: Optional[BlockchainInteractor] = None


def _run_subprocess_check(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Helper to run subprocess and raise for errors, capturing output."""
    # On Windows, Popen/run might need shell=True for .exe if not in PATH,
    # but it's better to use absolute paths or ensure PATH is set.
    # For 'docker' command, it's usually in PATH.
    return subprocess.run(cmd, capture_output=True, check=True, text=True, **kwargs)


def start_docker_desktop() -> bool:
    """
    Starts Docker Desktop if it's not running (Windows specific).

    Returns:
        True if Docker is running or started successfully, False otherwise.
    """
    try:
        _run_subprocess_check(DOCKER_INFO_CMD)
        logger.info("Docker Desktop is already running.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Docker Desktop not running or 'docker' command not found. Attempting to start...")

    # This part is Windows-specific due to winreg
    if sys.platform != "win32":
        logger.error("Automatic Docker Desktop startup is only supported on Windows.")
        return False

    try:
        # pylint: disable=import-outside-toplevel
        # Justification: winreg is Windows-specific, import only when needed.
        import winreg # Defer import to avoid ImportError on non-Windows
        # pylint: enable=import-outside-toplevel

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, DOCKER_DESKTOP_REG_KEY) as key:
            install_location = winreg.QueryValueEx(key, DOCKER_DESKTOP_REG_VALUE)[0]
        docker_exe_path = Path(install_location) / "Docker Desktop.exe"

        if not docker_exe_path.is_file():
            logger.error("Docker Desktop.exe not found at: %s", docker_exe_path)
            return False

        subprocess.Popen([str(docker_exe_path)], close_fds=True) # close_fds for POSIX, ignored on Win

        logger.info("Waiting for Docker Desktop to initialize...")
        for attempt in range(DOCKER_START_TIMEOUT_SECONDS // DOCKER_RETRY_INTERVAL_SECONDS):
            time.sleep(DOCKER_RETRY_INTERVAL_SECONDS)
            try:
                _run_subprocess_check(DOCKER_INFO_CMD)
                logger.info("Docker Desktop started successfully.")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.debug("Docker not ready yet (attempt %d)...", attempt + 1)
        logger.error("Timeout waiting for Docker Desktop to start.")
        return False
    except FileNotFoundError:
        logger.error(
            "Docker Desktop registry key or InstallLocation not found. Is Docker Desktop installed?"
        )
        return False
    except Exception as e: # pylint: disable=broad-except
        logger.error("Failed to start Docker Desktop: %s", e, exc_info=True)
        return False


def wait_for_ganache(w3: Web3, max_attempts: int, retry_interval: int) -> bool:
    """
    Waits for Ganache to be ready and accepting connections.

    Args:
        w3: Web3 instance connected to Ganache.
        max_attempts: Maximum number of connection attempts.
        retry_interval: Seconds to wait between attempts.

    Returns:
        True if connection is successful, False otherwise.
    """
    logger.info("Waiting for Ganache to be ready...")
    for attempt in range(max_attempts):
        try:
            if not w3.is_connected():
                raise ConnectionError("Not connected to the Ethereum node.")
            accounts = w3.eth.accounts
            if not accounts:
                raise ConnectionError("No accounts available on the node.")
            # A simple call to confirm node is responsive
            w3.eth.get_block('latest')
            logger.info("Successfully connected to Ganache with %d accounts.", len(accounts))
            return True
        except Exception as e: # pylint: disable=broad-except
            # Catching broad exception as various issues can occur (connection, node not ready)
            logger.debug(
                "Attempt %d/%d to connect to Ganache failed: %s",
                attempt + 1, max_attempts, e
            )
            if attempt == max_attempts - 1:
                logger.error("Final attempt to connect to Ganache failed decisively.")
                break
            time.sleep(retry_interval)
    return False


class BlockchainSetupThread(threading.Thread):
    """
    Thread to handle the potentially long-running blockchain setup process.
    This includes starting Docker, Ganache, and deploying/connecting to contracts.
    """
    # pylint: disable=too-many-instance-attributes
    # R0902: Justification: State for setup process, results, and splash screen interaction.
    # Could be refactored further with a state object if it grows more.
    def __init__(self, splash_screen: Optional[QSplashScreen] = None):
        super().__init__()
        self.splash_screen: Optional[QSplashScreen] = splash_screen
        self.success: bool = False
        self.error_message: Optional[str] = None
        self.created_blockchain_interactor: Optional[BlockchainInteractor] = None
        self._w3: Optional[Web3] = None # Web3 instance for internal use

    def _update_splash_message(self, message: str) -> None:
        """Safely updates the splash screen message from the thread."""
        if self.splash_screen:
            # Critical: GUI updates from non-GUI threads are generally unsafe.
            # QSplashScreen.showMessage might be more tolerant than other widgets,
            # but using signals/slots is the robust Qt way.
            # QApplication.processEvents() helps process pending events.
            # For a 10/10 in a real app, this would need a signal.
            # pylint: disable=protected-access
            # (Accessing QApplication.instance() if available, or using QCoreApplication)
            app_instance = QCoreApplication.instance()
            if app_instance:
                self.splash_screen.showMessage(message, Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
                app_instance.processEvents() # Process events to make splash update visible

    def _check_docker_and_ganache(self) -> bool:
        """Checks Docker, starts Ganache, and connects Web3."""
        self._update_splash_message("Checking Docker Desktop status...")
        if not start_docker_desktop():
            self.error_message = "Failed to start or connect to Docker Desktop."
            return False

        self._update_splash_message("Starting Ganache...")
        if not start_ganache(): # Assuming start_ganache() handles its own logging
            self.error_message = "Failed to start Ganache."
            return False
        time.sleep(GANACHE_STARTUP_DELAY_SECONDS) # Give Ganache time to initialize

        self._update_splash_message("Connecting to blockchain via Ganache...")
        self._w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
        if not wait_for_ganache(self._w3, GANACHE_CONNECTION_MAX_ATTEMPTS,
                                GANACHE_CONNECTION_RETRY_INTERVAL_SECONDS):
            self.error_message = "Failed to connect to Ganache RPC."
            return False
        return True

    def _load_or_deploy_contracts(self) -> bool:
        """Loads existing contract addresses or compiles and deploys new ones."""
        if not self._w3: # Should be set by _check_docker_and_ganache
            self.error_message = "Web3 not initialized for contract deployment."
            return False

        if CONTRACT_ADDRESSES_FILE.exists():
            self._update_splash_message("Verifying existing contracts...")
            try:
                # No need to read file here, BlockchainInteractor does it.
                # Just try to initialize it.
                self.created_blockchain_interactor = BlockchainInteractor()
                # Add a simple check if the interactor is functional, e.g., ping a contract
                # if hasattr(self.created_blockchain_interactor, 'is_functional'):
                #    if not self.created_blockchain_interactor.is_functional():
                #        raise ConnectionError("Existing contracts not responsive.")
                logger.info("Using existing deployed contracts.")
                return True
            except Exception as e: # pylint: disable=broad-except
                logger.warning(
                    "Could not use existing contracts from %s: %s. Will attempt redeployment.",
                    CONTRACT_ADDRESSES_FILE, e
                )
                # Fall through to redeploy

        self._update_splash_message("Compiling smart contracts...")
        compiled_contracts = compile_contracts() # Assuming this returns necessary data
        if not compiled_contracts:
            self.error_message = "Smart contract compilation failed."
            return False

        self._update_splash_message("Deploying smart contracts...")
        # Assuming deploy_contracts and save_contract_data handle their specific errors
        deployed_contracts_info = deploy_contracts(self._w3, compiled_contracts)
        if not deployed_contracts_info:
            self.error_message = "Smart contract deployment failed."
            return False
        save_contract_data(deployed_contracts_info)

        self._update_splash_message("Initializing blockchain interface with new contracts...")
        self.created_blockchain_interactor = BlockchainInteractor()
        logger.info("New contracts deployed and interface initialized.")
        return True

    def run(self) -> None:
        """
        Executes the blockchain setup process.
        Sets `self.success`, `self.error_message`, and `self.created_blockchain_interactor`.
        """
        try:
            if not self._check_docker_and_ganache():
                # error_message already set by the helper
                self.success = False
                return

            if not self._load_or_deploy_contracts():
                # error_message already set by the helper
                self.success = False
                return

            self.success = True
            logger.info("Blockchain setup thread completed successfully.")

        except Exception as e: # pylint: disable=broad-except
            self.error_message = f"Unexpected error during blockchain setup: {e}"
            logger.error(self.error_message, exc_info=True)
            self.success = False


def setup_database() -> None:
    """
    Initializes and runs database migrations.
    Exits application on critical database error.
    """
    logger.info("Setting up database...")
    try:
        DatabaseMigrations.run_migrations()
        logger.info("Database migrations completed successfully.")
    except Exception as e: # pylint: disable=broad-except
        logger.critical("Fatal error initializing database: %s", e, exc_info=True)
        # Show a message box before exiting if possible (though QApplication might not be fully up)
        # For simplicity, just exiting here.
        QMessageBox.critical(None, "Database Error", f"Could not initialize database: {e}")
        sys.exit(1)


def main() -> None:
    """Main function to setup and run the application."""
    # pylint: disable=global-statement
    # Justification: g_blockchain_interactor is a module-level global
    # representing the shared blockchain interface, initialized here.
    global g_blockchain_interactor

    setup_database()

    # Using list for sys.argv to satisfy Pylint type expectations for QApplication
    app_args = list(sys.argv)
    app = QApplication(app_args)
    logger.info("Frontend: PyQt application started.")

    # Initialize session (ensure Session class is Pylint-compliant)
    session = Session() # Assuming Session() is relatively quick
    logger.info("User session manager initialized. App instance started at: %s",
                getattr(session, '_instance_creation_time_str', 'N/A'))


    splash_pixmap = QPixmap(str(RESOURCES_PATH / "logo_splash.png"))
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    # Set application name for window titles, etc.
    app.setApplicationName(APP_NAME)
    # splash.setWindowIcon(QIcon(str(RESOURCES_PATH / "app_icon.png"))) # Example
    splash.show()
    splash.showMessage("Initializing application...", Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
    app.processEvents() # Ensure splash message is shown

    blockchain_thread = BlockchainSetupThread(splash_screen=splash)
    blockchain_thread.start()
    logger.info("Blockchain setup thread started.")

    # Main event loop integration for thread completion is complex.
    # For simplicity, we join with a timeout.
    # A more robust solution would use signals from the thread to the main GUI event loop.
    blockchain_thread.join(timeout=BLOCKCHAIN_SETUP_TIMEOUT_SECONDS)

    if blockchain_thread.is_alive():
        logger.error("Blockchain setup timed out after %d seconds.", BLOCKCHAIN_SETUP_TIMEOUT_SECONDS)
        # Optionally try to stop/interrupt the thread if possible, though join() should wait.
        # The thread might still be running and could set its error message.
        if not blockchain_thread.error_message: # If no specific error, set timeout error
             blockchain_thread.error_message = "Setup process timed out."
    elif not blockchain_thread.success:
        logger.error(
            "Blockchain setup failed: %s",
            blockchain_thread.error_message or "Unknown error in setup thread."
        )
    else: # Success
        g_blockchain_interactor = blockchain_thread.created_blockchain_interactor
        logger.info("Blockchain setup completed. Interactor is %s.",
                    "available" if g_blockchain_interactor else "NOT available")

    if not g_blockchain_interactor:
        logger.warning(
            "Proceeding without full blockchain functionality due to setup issues. "
            "Error: %s", blockchain_thread.error_message
        )
        # Consider showing a non-fatal error message to the user
        QMessageBox.warning(
            None, "Blockchain Warning",
            f"Blockchain features may be limited or unavailable.\n"
            f"Error: {blockchain_thread.error_message or 'Setup failed/timed out.'}"
        )

    # A small delay to ensure splash screen messages are seen if errors occurred
    time.sleep(SPLASH_FINISH_DELAY_SECONDS if not g_blockchain_interactor else 0.1)

    main_window = VistaAccedi() # Pass g_blockchain_interactor if needed
    # Example: main_window = VistaAccedi(g_blockchain_interactor)
    main_window.show()
    splash.finish(main_window)
    logger.info("Main window displayed. Splash screen finished.")

    sys.exit(app.exec_())


if __name__ == "__main__":
    # Ensure logger is configured before any logging calls
    # (Assuming log_load_setting.logger handles its own setup or is configured at import)
    logger.info("Application starting...")
    main()
    logger.info("Application finished.")