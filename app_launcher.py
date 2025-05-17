#!/usr/bin/env python3
# main.py - Main entry point for the Sustainable Food Supply Chain application

import os
import sys
import time
import signal
import logging
import threading
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import blockchain startup functions
from start_blockchain import check_node_modules, start_blockchain

# Constants
PROJECT_DIR = Path(__file__).parent
ON_CHAIN_DIR = PROJECT_DIR / "on_chain"
OFF_CHAIN_DIR = PROJECT_DIR / "off_chain"

# Global variables
hardhat_process = None
application_running = False

def signal_handler(sig, frame):
    """Handle termination signals to gracefully shut down the application."""
    global application_running
    logger.info("Received termination signal. Shutting down...")
    application_running = False
    
    # Stop Hardhat node if it's running
    if hardhat_process:
        logger.info("Stopping Hardhat node...")
        if sys.platform == 'win32':
            subprocess.run(f"taskkill /F /PID {hardhat_process.pid} /T", shell=True)
        else:
            os.killpg(os.getpgid(hardhat_process.pid), signal.SIGTERM)
        logger.info("Hardhat node stopped")
    
    sys.exit(0)

def start_application():
    """Start the main application."""
    global application_running
    
    try:
        # Here you would start your actual application
        # For example, if you have a Flask app in the off_chain directory:
        # subprocess.Popen([sys.executable, str(OFF_CHAIN_DIR / "app.py")], cwd=str(PROJECT_DIR))
        
        logger.info("Application started successfully!")
        application_running = True
        
        # Keep the main thread alive
        while application_running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)

def main():
    """Main entry point for the application."""
    global hardhat_process
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Check for Node.js dependencies
        check_node_modules()
        
        # Start Hardhat node and deploy contracts
        logger.info("Starting blockchain environment...")
        hardhat_process = start_blockchain()
        
        # Start the main application
        start_application()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        if hardhat_process:
            hardhat_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
