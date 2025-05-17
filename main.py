#!/usr/bin/env python3
# clean_start.py - Clean startup script for Hardhat-based blockchain environment

import os
import sys
import time
import signal
import logging
import threading
import subprocess
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_DIR = Path(__file__).parent
ON_CHAIN_DIR = PROJECT_DIR / "on_chain"
OFF_CHAIN_DIR = PROJECT_DIR / "off_chain"
LOG_PREFIX_HARDHAT = "[HARDHAT] "
LOG_PREFIX_ETHERS = "[ETHERS.JS] "

# Global variables
hardhat_process = None

def signal_handler(sig, frame):
    """Handle termination signals to gracefully shut down the application."""
    logger.info(f"{LOG_PREFIX_HARDHAT}Received termination signal. Shutting down...")
    
    # Stop Hardhat node if it's running
    if hardhat_process:
        logger.info(f"{LOG_PREFIX_HARDHAT}Stopping Hardhat node...")
        if sys.platform == 'win32':
            subprocess.run(f"taskkill /F /PID {hardhat_process.pid} /T", shell=True)
        else:
            os.killpg(os.getpgid(hardhat_process.pid), signal.SIGTERM)
        logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node stopped")
    
    sys.exit(0)

def check_node_modules():
    """Check if node_modules exists, if not install dependencies."""
    node_modules_path = ON_CHAIN_DIR / "node_modules"
    
    if not node_modules_path.exists():
        logger.info(f"{LOG_PREFIX_HARDHAT}Node modules not found. Installing dependencies...")
        try:
            subprocess.run(
                "npm install",
                shell=True,
                cwd=str(ON_CHAIN_DIR),
                check=True
            )
            logger.info(f"{LOG_PREFIX_HARDHAT}Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"{LOG_PREFIX_HARDHAT}Failed to install dependencies: {e}")
            sys.exit(1)

def start_hardhat_node():
    """Start the Hardhat node in a separate process."""
    global hardhat_process
    
    try:
        logger.info(f"{LOG_PREFIX_HARDHAT}Starting Hardhat node...")
        # Use shell=True on Windows to avoid console window popup
        shell_param = True if sys.platform == 'win32' else False
        
        # Start the Hardhat node
        hardhat_process = subprocess.Popen(
            "npx hardhat node",
            shell=shell_param,
            cwd=str(ON_CHAIN_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node process started with PID: {hardhat_process.pid}")
        
        # Wait for the node to be ready
        if not wait_for_hardhat_node():
            logger.error(f"{LOG_PREFIX_HARDHAT}Failed to start Hardhat node")
            return False
            
        logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node is ready")
        return True
        
    except Exception as e:
        logger.error(f"{LOG_PREFIX_HARDHAT}Error starting Hardhat node: {e}")
        return False

def wait_for_hardhat_node(max_attempts=30, delay=1):
    """Wait for Hardhat node to be available."""
    import requests
    
    logger.info(f"{LOG_PREFIX_HARDHAT}Waiting for Hardhat node to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.post(
                "http://127.0.0.1:8545",
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

def deploy_contracts():
    """Deploy contracts using Hardhat."""
    try:
        logger.info(f"{LOG_PREFIX_ETHERS}Deploying contracts with Hardhat...")
        
        # Run the Hardhat deployment script
        result = subprocess.run(
            "npx hardhat run scripts/deploy.js --network localhost",
            shell=True if sys.platform == 'win32' else False,
            cwd=str(ON_CHAIN_DIR),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"{LOG_PREFIX_ETHERS}Contract deployment failed: {result.stderr}")
            return False
        
        # Log the output
        for line in result.stdout.splitlines():
            logger.info(f"{LOG_PREFIX_ETHERS}{line}")
        
        logger.info(f"{LOG_PREFIX_ETHERS}Contracts deployed successfully")
        return True
    
    except Exception as e:
        logger.error(f"{LOG_PREFIX_ETHERS}Error deploying contracts: {e}")
        return False

def setup_database():
    """Configure the database before starting the graphical interface."""
    sys.path.append(str(OFF_CHAIN_DIR))
    from database.db_migrations import DatabaseMigrations
    
    try:
        logger.info("Initializing database...")
        DatabaseMigrations.run_migrations()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)  # Stops the application if there is a critical error

def start_application():
    """Start the main application with GUI."""
    try:
        logger.info("Starting the main application...")
        
        # Add off_chain directory to path
        sys.path.append(str(OFF_CHAIN_DIR))
        
        # Import required modules
        from session import Session
        from gui_manager import setup_gui
        
        # Create a session
        session = Session()
        
        # Setup GUI and get application instance
        app, window = setup_gui(session)
        
        logger.info("Application GUI initialized, starting event loop")
        
        # Start the application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        return False
    
    return True

def main():
    """Main entry point."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Configure the database before starting the blockchain
        setup_database()
        
        # Check and install Node.js dependencies if needed
        check_node_modules()
        
        # Start Hardhat node
        if not start_hardhat_node():
            logger.error(f"{LOG_PREFIX_HARDHAT}Failed to start Hardhat node")
            return False
        
        # Deploy contracts
        if not deploy_contracts():
            logger.error(f"{LOG_PREFIX_ETHERS}Failed to deploy contracts")
            return False
        
        # Start the application with GUI
        start_application()
        
        return True
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return False
    finally:
        # Stop Hardhat node if it's running
        if hardhat_process:
            logger.info(f"{LOG_PREFIX_HARDHAT}Stopping Hardhat node...")
            if sys.platform == 'win32':
                subprocess.run(f"taskkill /F /PID {hardhat_process.pid} /T", shell=True)
            else:
                os.killpg(os.getpgid(hardhat_process.pid), signal.SIGTERM)
            logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node stopped")

if __name__ == "__main__":
    main()
