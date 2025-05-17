# Standard Library Imports
import sys
import time
import os
import threading
import subprocess
import requests
from pathlib import Path
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from configuration.log_load_setting import logger

# Import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from on_chain.interact_contract import BlockchainInteractor

# Global variables
blockchain_interactor = None
HARDHAT_NODE_URL = "http://127.0.0.1:8545"
PROJECT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ON_CHAIN_DIR = PROJECT_DIR / "on_chain"

# Constants for logging
LOG_PREFIX_HARDHAT = "[HARDHAT] "
LOG_PREFIX_ETHERS = "[ETHERS.JS] "


def start_hardhat_node():
    """Start the Hardhat node in a separate process."""
    try:
        logger.info(f"{LOG_PREFIX_HARDHAT}Starting Hardhat node...")
        # Use shell=True on Windows to avoid console window popup
        shell_param = True if sys.platform == 'win32' else False
        
        # Start the Hardhat node
        node_process = subprocess.Popen(
            "npx hardhat node",
            shell=shell_param,
            cwd=str(ON_CHAIN_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node process started")
        return node_process
    except Exception as e:
        logger.error(f"{LOG_PREFIX_HARDHAT}Error starting Hardhat node: {e}")
        return None


def wait_for_hardhat(max_attempts=30, delay=1):
    """Wait for Hardhat node to be available."""
    logger.info(f"{LOG_PREFIX_HARDHAT}Waiting for Hardhat node to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.post(
                HARDHAT_NODE_URL,
                json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                timeout=2
            )
            
            if response.status_code == 200:
                logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node is ready (attempt {attempt + 1}/{max_attempts})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Waiting for Hardhat node... ({attempt + 1}/{max_attempts})")
        time.sleep(delay)
    
    logger.error(f"{LOG_PREFIX_HARDHAT}Hardhat node did not start after {max_attempts} attempts")
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
            self.update_splash_message("Starting Hardhat blockchain environment...")
            self.hardhat_process = start_hardhat_node()
            if not self.hardhat_process:
                raise Exception("Failed to start Hardhat node")

            self.update_splash_message("Waiting for Hardhat node to be ready...")
            if not wait_for_hardhat(max_attempts=30):
                raise Exception("Failed to connect to Hardhat node")

            self.update_splash_message("Deploying smart contracts with ethers.js...")
            if self._deploy_contracts():
                self.update_splash_message("Initializing blockchain interactor with ethers.js...")
                blockchain_interactor = BlockchainInteractor()
                self.success = True
                logger.info(f"{LOG_PREFIX_ETHERS}Blockchain interactor initialized successfully")
            else:
                raise Exception(self.error_message)

        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Blockchain setup error: {e}")
            self.success = False

    def _deploy_contracts(self) -> bool:
        """Deploy contracts using Hardhat script."""
        try:
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

            # Deploy contracts using Hardhat script
            self.update_splash_message("Deploying contracts with Hardhat and ethers.js...")
            result = subprocess.run(
                "npx hardhat run scripts/deploy.js --network localhost",
                shell=True,
                cwd=str(ON_CHAIN_DIR),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.error_message = f"Contract deployment failed: {result.stderr}"
                logger.error(f"{LOG_PREFIX_ETHERS}{self.error_message}")
                return False
                
            logger.info(f"{LOG_PREFIX_ETHERS}Contracts deployed successfully")
            # Log the output but filter out any Docker/Ganache references
            for line in result.stdout.splitlines():
                if not any(term in line.lower() for term in ["docker", "ganache"]):
                    logger.info(f"{LOG_PREFIX_ETHERS}{line}")

            return True
                
        except Exception as e:
            self.error_message = f"Error deploying contracts: {e}"
            logger.error(self.error_message)
            return False

        return True
