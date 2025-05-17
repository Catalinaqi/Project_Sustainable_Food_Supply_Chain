#!/usr/bin/env python3
# start_blockchain.py - Helper script to start Hardhat node and deploy contracts

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_DIR = Path(__file__).parent
ON_CHAIN_DIR = PROJECT_DIR / "on_chain"

def check_node_modules():
    """Check if node_modules exists, if not install dependencies."""
    node_modules_path = ON_CHAIN_DIR / "node_modules"
    
    if not node_modules_path.exists():
        logger.info("Node modules not found. Installing dependencies...")
        try:
            subprocess.run(
                "npm install",
                shell=True,
                cwd=str(ON_CHAIN_DIR),
                check=True
            )
            logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            sys.exit(1)

def start_hardhat_node():
    """Start the Hardhat node in a separate process."""
    try:
        logger.info("Starting Hardhat node...")
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
        
        # Wait for node to be ready
        logger.info("Waiting for Hardhat node to be ready...")
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Check if the node is running by making a JSON-RPC request
                import requests
                response = requests.post(
                    "http://127.0.0.1:8545",
                    json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                    timeout=2
                )
                
                if response.status_code == 200:
                    logger.info(f"Hardhat node is ready (attempt {attempt + 1}/{max_attempts})")
                    return node_process
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Waiting for Hardhat node... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        # If we get here, the node didn't start properly
        logger.error("Failed to start Hardhat node after multiple attempts")
        if node_process:
            node_process.terminate()
        sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error starting Hardhat node: {e}")
        sys.exit(1)

def deploy_contracts():
    """Deploy contracts to the Hardhat node."""
    try:
        logger.info("Deploying contracts...")
        result = subprocess.run(
            "npx hardhat run scripts/deploy.js --network localhost",
            shell=True,
            cwd=str(ON_CHAIN_DIR),
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Contracts deployed successfully")
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Contract deployment failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error deploying contracts: {e}")
        return False

def start_blockchain():
    """Start the Hardhat node and deploy contracts."""
    try:
        # Start Hardhat node
        node_process = start_hardhat_node()
        
        # Deploy contracts
        if not deploy_contracts():
            if node_process:
                node_process.terminate()
            sys.exit(1)
        
        logger.info("Blockchain and contracts are ready!")
        logger.info("You can now interact with the contracts.")
        
        # Return the node process so it can be managed by the caller
        return node_process
        
    except Exception as e:
        logger.error(f"Error in blockchain startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_node_modules()
    start_blockchain()
