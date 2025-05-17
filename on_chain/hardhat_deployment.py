#!/usr/bin/env python3
# hardhat_deployment.py - Manages Hardhat node and contract deployment

import os
import json
import time
import signal
import subprocess
import sys
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_DIR = Path(__file__).parent
HARDHAT_NODE_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESSES_FILE = PROJECT_DIR / "contract_addresses.json"

class HardhatManager:
    def __init__(self):
        self.node_process = None
        self.is_node_running = False
    
    def start_node(self):
        """Start a Hardhat node in a separate process."""
        try:
            logger.info("Starting Hardhat node...")
            # Use shell=True on Windows to avoid console window popup
            shell_param = True if sys.platform == 'win32' else False
            
            self.node_process = subprocess.Popen(
                "npx hardhat node",
                shell=shell_param,
                cwd=str(PROJECT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for node to start
            self._wait_for_node()
            
            if self.is_node_running:
                logger.info("Hardhat node started successfully")
                return True
            else:
                logger.error("Failed to start Hardhat node")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Hardhat node: {e}")
            return False
    
    def _wait_for_node(self, max_attempts=10, delay=1):
        """Wait for Hardhat node to be available."""
        logger.info("Waiting for Hardhat node to be ready...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    HARDHAT_NODE_URL,
                    json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                    timeout=2
                )
                
                if response.status_code == 200:
                    self.is_node_running = True
                    logger.info(f"Hardhat node is ready (attempt {attempt + 1}/{max_attempts})")
                    return
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Waiting for Hardhat node... ({attempt + 1}/{max_attempts})")
            time.sleep(delay)
        
        logger.error(f"Hardhat node did not start after {max_attempts} attempts")
    
    def deploy_contracts(self):
        """Deploy contracts using Hardhat script."""
        if not self.is_node_running:
            logger.error("Cannot deploy contracts: Hardhat node is not running")
            return False
        
        try:
            logger.info("Deploying contracts...")
            deploy_process = subprocess.run(
                "npx hardhat run scripts/deploy.js --network localhost",
                shell=True,
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True
            )
            
            if deploy_process.returncode == 0:
                logger.info("Contracts deployed successfully")
                logger.info(deploy_process.stdout)
                return True
            else:
                logger.error(f"Contract deployment failed: {deploy_process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying contracts: {e}")
            return False
    
    def stop_node(self):
        """Stop the Hardhat node process."""
        if self.node_process:
            logger.info("Stopping Hardhat node...")
            
            # Different process termination based on platform
            if sys.platform == 'win32':
                subprocess.run(f"taskkill /F /PID {self.node_process.pid} /T", shell=True)
            else:
                os.killpg(os.getpgid(self.node_process.pid), signal.SIGTERM)
            
            self.node_process = None
            self.is_node_running = False
            logger.info("Hardhat node stopped")
    
    def get_contract_data(self):
        """Read deployed contract data from file."""
        try:
            if not CONTRACT_ADDRESSES_FILE.exists():
                logger.error(f"Contract addresses file not found: {CONTRACT_ADDRESSES_FILE}")
                return None
            
            with open(CONTRACT_ADDRESSES_FILE, 'r') as f:
                contract_data = json.load(f)
            
            return contract_data
            
        except Exception as e:
            logger.error(f"Error reading contract data: {e}")
            return None

def main():
    """Main function to start node and deploy contracts."""
    hardhat = HardhatManager()
    
    try:
        # Start Hardhat node
        if not hardhat.start_node():
            return
        
        # Deploy contracts
        if not hardhat.deploy_contracts():
            return
        
        # Get contract data
        contract_data = hardhat.get_contract_data()
        if contract_data:
            logger.info(f"Contracts deployed and data saved to {CONTRACT_ADDRESSES_FILE}")
        
        # Keep node running until user interrupts
        logger.info("Hardhat node is running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        hardhat.stop_node()
        logger.info("Exiting...")

if __name__ == "__main__":
    main()
