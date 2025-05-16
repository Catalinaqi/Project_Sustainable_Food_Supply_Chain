import subprocess
import json
import time
import os
from web3 import Web3
from solcx import compile_standard, install_solc
import sys

# Import logger from off_chain configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from off_chain.configuration.log_load_setting import logger

def start_ganache():
    """Connect to running Ganache instance using Docker Compose"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Stop any existing containers and remove them
        logger.info("Stopping any existing containers...")
        try:
            subprocess.run(["docker", "compose", "down"], cwd=project_root, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error stopping containers: {e.stderr}")
            # Continue anyway as the containers might not exist
        
        # Start the containers with Docker Compose
        logger.info("Starting containers with Docker Compose...")
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to start containers: {result.stderr}")
            # Try to get more information about the failure
            try:
                logs = subprocess.run(
                    ["docker", "compose", "logs"],
                    cwd=project_root,
                    capture_output=True,
                    text=True
                )
                logger.error(f"Container logs: {logs.stdout}")
            except Exception as log_e:
                logger.error(f"Failed to get container logs: {str(log_e)}")
            return False
        
        logger.info("Docker Compose services started successfully")
        
        # Add delay to allow Ganache to fully initialize
        logger.info("Waiting for Ganache to initialize...")
        time.sleep(5)
        
        # Verify connection
        max_attempts = 30
        for i in range(max_attempts):
            try:
                w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
                if w3.is_connected():
                    accounts = w3.eth.accounts
                    logger.info(f"Successfully connected to Ganache. {len(accounts)} accounts available.")
                    return True
            except Exception as e:
                if i == max_attempts - 1:
                    logger.error(f"Failed to connect to Ganache after {max_attempts} attempts: {str(e)}")
                    return False
                logger.debug(f"Connection attempt {i+1}/{max_attempts} failed, retrying...")
                time.sleep(1)
        
        return False
    except Exception as e:
        logger.error(f"Error in start_ganache: {str(e)}")
        return False

def compile_contracts():
    """Compile all Solidity contracts"""
    contract_sources = {}
    contracts_dir = os.path.join(os.path.dirname(__file__), "contracts")
      # Install specific Solidity version required by contracts
    install_solc("0.8.0")
    
    # Read all Solidity contracts
    for file in os.listdir(contracts_dir):
        if file.endswith(".sol"):
            with open(os.path.join(contracts_dir, file), "r") as f:
                contract_sources[file] = {"content": f.read()}
    
    # Compile contracts
    compiled_contracts = compile_standard({
        "language": "Solidity",
        "sources": contract_sources,
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }    }, solc_version="0.8.0")
    
    return compiled_contracts

def deploy_contracts(w3, compiled_contracts):
    """Deploy all contracts and return their addresses"""
    deployed_contracts = {}
    account = w3.eth.accounts[0]  # Use the first account as deployer
    
    # Get the current gas limit from the latest block
    block = w3.eth.get_block('latest')
    block_gas_limit = block.gasLimit
    
    # Set a high gas limit for contract deployment (80% of block gas limit)
    # This ensures we have enough gas for large contracts
    deployment_gas_limit = int(block_gas_limit * 0.8)
    logger.info(f"Using gas limit of {deployment_gas_limit} for contract deployment")
    
    for contract_file in compiled_contracts["contracts"].keys():
        for contract_name in compiled_contracts["contracts"][contract_file].keys():
            print(f"Deploying {contract_name}...")
            
            contract_data = compiled_contracts["contracts"][contract_file][contract_name]
            Contract = w3.eth.contract(
                abi=contract_data["abi"],
                bytecode=contract_data["evm"]["bytecode"]["object"]
            )
            
            try:
                # Deploy contract with higher gas limit
                tx_hash = Contract.constructor().transact({
                    "from": account,
                    "gas": deployment_gas_limit
                })
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                deployed_contracts[contract_name] = {
                    "address": tx_receipt.contractAddress,
                    "abi": contract_data["abi"]
                }
                
                print(f"{contract_name} deployed at: {tx_receipt.contractAddress}")
                logger.info(f"{contract_name} deployed successfully at {tx_receipt.contractAddress}")
            except Exception as e:
                logger.error(f"Failed to deploy {contract_name}: {str(e)}")
                # Try with even higher gas limit as a fallback
                try:
                    logger.info(f"Retrying deployment of {contract_name} with maximum gas limit")
                    tx_hash = Contract.constructor().transact({
                        "from": account,
                        "gas": block_gas_limit  # Use full block gas limit
                    })
                    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    deployed_contracts[contract_name] = {
                        "address": tx_receipt.contractAddress,
                        "abi": contract_data["abi"]
                    }
                    
                    print(f"{contract_name} deployed at: {tx_receipt.contractAddress} (with max gas)")
                    logger.info(f"{contract_name} deployed successfully with max gas at {tx_receipt.contractAddress}")
                except Exception as retry_e:
                    logger.error(f"Failed to deploy {contract_name} even with max gas: {str(retry_e)}")
                    # Continue with other contracts
    
    return deployed_contracts

def save_contract_data(deployed_contracts):
    """Save contract addresses and ABIs to JSON file"""
    output_path = os.path.join(os.path.dirname(__file__), "contract_addresses.json")
    contract_data = {
        "contracts": deployed_contracts,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "network": "ganache"
    }
    
    with open(output_path, "w") as f:
        json.dump(contract_data, f, indent=4)
    
    print(f"Contract addresses and ABIs saved to {output_path}")

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        # Start Ganache and other services
        logger.info("Starting blockchain services...")
        if not start_ganache():
            raise Exception("Failed to start and connect to Ganache")
        
        # Connect to Ganache
        logger.info("Connecting to Ganache...")
        max_attempts = 30
        w3 = None
        for i in range(max_attempts):
            try:
                w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
                if w3.is_connected():
                    break
            except Exception as e:
                if i == max_attempts - 1:
                    raise Exception(f"Failed to connect to Ganache: {str(e)}")
                time.sleep(1)
        
        # Compile contracts
        logger.info("Compiling contracts...")
        compiled_contracts = compile_contracts()
        
        # Deploy contracts
        logger.info("Deploying contracts...")
        deployed_contracts = deploy_contracts(w3, compiled_contracts)
        
        # Save contract data
        logger.info("Saving contract data...")
        save_contract_data(deployed_contracts)
        
        logger.info("Deployment completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error during deployment: {str(e)}")
        return False
    
    finally:
        # Stop containers in case of error
        try:
            subprocess.run(["docker", "compose", "down"], cwd=project_root, check=True)
            logger.info("Docker containers stopped")
        except Exception as e:
            logger.error(f"Error stopping containers: {str(e)}")
            try:
                # Try to force remove containers as a last resort
                subprocess.run(["docker", "compose", "rm", "-f"], cwd=project_root)
            except Exception as rm_e:
                logger.error(f"Error force removing containers: {str(rm_e)}")

if __name__ == "__main__":
    main()
