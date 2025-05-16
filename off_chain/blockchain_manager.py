# Standard Library Imports
import sys
import time
import os
import threading
import subprocess
import winreg
from pathlib import Path
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from configuration.log_load_setting import logger

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
        self._w3 = None

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
            self._w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not wait_for_ganache(self._w3, max_attempts=30):
                raise Exception("Failed to connect to Ganache")

            if self._load_or_deploy_contracts():
                blockchain_interactor = self.created_blockchain_interactor
                self.success = True
            else:
                raise Exception(self.error_message)

        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Blockchain setup error: {e}")
            self.success = False

    def _load_or_deploy_contracts(self) -> bool:
        """Deploys new contracts every time and backs up existing ones."""
        if not self._w3:
            self.error_message = "Web3 not initialized for contract deployment."
            return False

        contract_file = Path(__file__).resolve().parent.parent / "on_chain" / "contract_addresses.json"

        # Backup existing contract addresses if they exist
        if contract_file.exists():
            self.update_splash_message("Backing up existing contract addresses...")
            backup_timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = contract_file.with_name(f"contract_addresses_backup_{backup_timestamp}.json")
            try:
                import shutil
                shutil.copy2(contract_file, backup_file)
                logger.info(f"Backed up contract addresses to {backup_file}")
            except Exception as e:
                logger.warning(f"Failed to backup contract addresses: {e}")

        self.update_splash_message("Compiling smart contracts...")
        compiled_contracts = compile_contracts()
        if not compiled_contracts:
            self.error_message = "Smart contract compilation failed."
            return False

        self.update_splash_message("Deploying smart contracts...")
        deployed_contracts = deploy_contracts(self._w3, compiled_contracts)
        if not deployed_contracts:
            self.error_message = "Smart contract deployment failed."
            return False

        save_contract_data(deployed_contracts)

        self.update_splash_message("Initializing blockchain interface with new contracts...")
        self.created_blockchain_interactor = BlockchainInteractor()
        logger.info("New contracts deployed and interface initialized.")
        return True


def wait_for_ganache(w3, max_attempts=30):
    """Wait for Ganache to be ready and accepting connections"""
    logger.info("Waiting for Ganache to be ready...")
    for i in range(max_attempts):
        try:
            # First check basic connection
            if not w3.is_connected():
                raise Exception("Not connected to node")
            
            # Then check if accounts are available
            accounts = w3.eth.accounts
            if not accounts or len(accounts) == 0:
                raise Exception("No accounts available")
                
            # Finally check if we can make a basic call
            block = w3.eth.get_block('latest')
            if not block:
                raise Exception("Cannot get latest block")
                
            logger.info(f"Successfully connected to Ganache with {len(accounts)} accounts")
            return True
            
        except Exception as e:
            if i == max_attempts - 1:
                logger.error(f"Final attempt to connect to Ganache failed: {str(e)}")
            else:
                logger.debug(f"Attempt {i+1}/{max_attempts} to connect to Ganache failed: {str(e)}")
            time.sleep(2)
    return False
