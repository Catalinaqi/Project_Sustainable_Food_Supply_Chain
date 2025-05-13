import sys
import time
import os
import threading
import subprocess
import winreg
from pathlib import Path
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox

from configuration.log_load_setting import logger
from database.db_migrations import DatabaseMigrations
from configuration.database import Database
from session import Session
from presentation.view.vista_accedi import VistaAccedi

# Import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from on_chain.automated_deployment import start_ganache, compile_contracts, deploy_contracts, save_contract_data
from on_chain.interact_contract import BlockchainInteractor
from web3 import Web3

# Variabili globali
blockchain_interactor = None


def start_docker_desktop():
    """Start Docker Desktop if it's not running"""
    try:
        # Check if Docker is running
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        logger.info("Docker Desktop is already running")
        return True
    except subprocess.CalledProcessError:
        logger.info("Docker Desktop is not running, attempting to start it...")
        try:
            # Find Docker Desktop path from registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop") as key:
                install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
            
            docker_path = Path(install_location) / "Docker Desktop.exe"
            
            # Start Docker Desktop
            subprocess.Popen([str(docker_path)], close_fds=True)
            
            # Wait for Docker to be ready
            max_attempts = 30  # 30 * 2 seconds = 1 minute timeout
            for i in range(max_attempts):
                try:
                    subprocess.run(["docker", "info"], capture_output=True, check=True)
                    logger.info("Docker Desktop started successfully")
                    return True
                except subprocess.CalledProcessError:
                    if i < max_attempts - 1:
                        time.sleep(2)
                        continue
                    else:
                        raise Exception("Timeout waiting for Docker to start")
            
        except Exception as e:
            logger.error(f"Failed to start Docker Desktop: {e}")
            return False


class BlockchainSetupThread(threading.Thread):
    def __init__(self, splash_screen=None):
        super().__init__()
        self.splash_screen = splash_screen
        self.success = False
        self.error_message = None
        self.blockchain_interactor = None

    def update_splash_message(self, message):
        if self.splash_screen:
            self.splash_screen.showMessage(message, Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
            QApplication.processEvents()

    def run(self):
        global blockchain_interactor
        try:
            self.update_splash_message("Checking Docker Desktop status...")
            if not start_docker_desktop():
                raise Exception("Failed to start Docker Desktop")

            self.update_splash_message("Starting Ganache...")
            if not start_ganache():
                raise Exception("Failed to start Ganache")

            # Aggiungi un breve delay per dare tempo a Ganache di inizializzarsi completamente
            time.sleep(5)

            self.update_splash_message("Connecting to blockchain...")
            w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not wait_for_ganache(w3, max_attempts=30):  # Aumentato a 30 tentativi
                raise Exception("Failed to connect to Ganache")

            # Check if contracts are already deployed
            contract_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       "on_chain", "contract_addresses.json")
            
            if os.path.exists(contract_file):
                try:
                    with open(contract_file, 'r') as f:
                        contract_data = json.load(f)
                    # Verify that contracts are accessible
                    self.update_splash_message("Verifying existing contracts...")
                    blockchain_interactor = BlockchainInteractor()
                    self.success = True
                    return
                except Exception as e:
                    logger.warning(f"Could not use existing contracts: {e}")

            # If necessary, compile and deploy new contracts
            self.update_splash_message("Compiling smart contracts...")
            compiled_contracts = compile_contracts()
            
            self.update_splash_message("Deploying smart contracts...")
            deployed_contracts = deploy_contracts(w3, compiled_contracts)
            save_contract_data(deployed_contracts)

            self.update_splash_message("Initializing blockchain interface...")
            blockchain_interactor = BlockchainInteractor()
            
            self.success = True
            
        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Blockchain setup error: {e}")
            self.success = False


def wait_for_ganache(w3, max_attempts=30):  # Aumentato a 30 tentativi
    """Wait for Ganache to be ready and accepting connections"""
    logger.info("Waiting for Ganache to be ready...")
    for i in range(max_attempts):
        try:
            if w3.is_connected() and len(w3.eth.accounts) > 0:
                logger.info("Successfully connected to Ganache")
                return True
        except Exception as e:
            logger.debug(f"Attempt {i+1}/{max_attempts} to connect to Ganache: {e}")
        time.sleep(2)  # Aumentato a 2 secondi per tentativo
    return False


def setup_database():
    try:
        DatabaseMigrations.run_migrations()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)  # Stops the application if there is a critical error


if __name__ == "__main__":
    # Configure the database before starting the graphical interface
    setup_database()
    
    # Starting the PyQt application
    app = QApplication(sys.argv)
    logger.info("Frontend: Starting the PyQt application...")

    session = Session()
    logger.info(f"Start session on {session.start_app}")

    # Show Splash Screen
    splash = QSplashScreen(QPixmap("presentation/resources/logo_splash.png"), Qt.WindowStaysOnTopHint)
    splash.show()

    # Start blockchain setup in a separate thread
    blockchain_setup = BlockchainSetupThread(splash_screen=splash)
    blockchain_setup.start()
    
    # Wait for blockchain setup to complete with timeout
    blockchain_setup.join(timeout=60)  # Aumentato a 60 secondi timeout
    
    if not blockchain_setup.is_alive() and blockchain_setup.success:
        logger.info("Blockchain setup completed successfully")
    else:
        if blockchain_setup.is_alive():
            logger.error("Blockchain setup timed out")
            blockchain_setup.join()  # Aspetta comunque il completamento del thread
        logger.warning("Proceeding without blockchain functionality")
        if blockchain_setup.error_message:
            logger.error(f"Blockchain setup failed: {blockchain_setup.error_message}")

    time.sleep(1)

    # Create the main window
    window = VistaAccedi()
    window.show()
    
    # Hide splash screen
    splash.finish(window)
    
    # Start the application event loop
    sys.exit(app.exec_())
