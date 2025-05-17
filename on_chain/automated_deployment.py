import subprocess
import json
import time
import os
import requests
import sys

# Import logger from off_chain configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from off_chain.configuration.log_load_setting import logger

# Constants
HARDHAT_NODE_URL = "http://127.0.0.1:8545"
LOG_PREFIX_HARDHAT = "[HARDHAT] "

def start_hardhat_node():
    """Start the Hardhat node and wait for it to be ready"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        on_chain_dir = os.path.join(project_root, "on_chain")
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Starting Hardhat node...")
        
        # Use shell=True on Windows to avoid console window popup
        shell_param = True if sys.platform == 'win32' else False
        
        # Start the Hardhat node
        node_process = subprocess.Popen(
            "npx hardhat node",
            shell=shell_param,
            cwd=on_chain_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Hardhat node process started")
        
        # Wait for the node to be ready
        if not wait_for_hardhat_node():
            logger.error(f"{LOG_PREFIX_HARDHAT}Failed to start Hardhat node")
            return False
            
        logger.info(f"{LOG_PREFIX_HARDHAT}Connected to Hardhat node successfully")
        return True
        
    except Exception as e:
        logger.error(f"{LOG_PREFIX_HARDHAT}Error starting Hardhat node: {str(e)}")
        return False


def wait_for_hardhat_node(max_attempts=30, delay=1):
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

def deploy_contracts_with_hardhat():
    """Deploy contracts using Hardhat"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        on_chain_dir = os.path.join(project_root, "on_chain")
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Deploying contracts with Hardhat...")
        
        # Run the Hardhat deployment script
        result = subprocess.run(
            "npx hardhat run scripts/deploy.js --network localhost",
            shell=True if sys.platform == 'win32' else False,
            cwd=on_chain_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            error_message = f"Contract deployment failed: {result.stderr}"
            logger.error(f"{LOG_PREFIX_HARDHAT}{error_message}")
            return False
        
        # Log the output but filter out any Docker/Ganache references
        for line in result.stdout.splitlines():
            if not any(term in line.lower() for term in ["docker", "ganache"]):
                logger.info(f"{LOG_PREFIX_HARDHAT}{line}")
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Contracts deployed successfully")
        return True
    
    except Exception as e:
        logger.error(f"{LOG_PREFIX_HARDHAT}Error deploying contracts: {str(e)}")
        return False

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
    try:
        # Start Hardhat node
        logger.info(f"{LOG_PREFIX_HARDHAT}Starting Hardhat blockchain environment...")
        if not start_hardhat_node():
            raise Exception("Failed to start and connect to Hardhat node")
        
        # Deploy contracts using Hardhat
        logger.info(f"{LOG_PREFIX_HARDHAT}Deploying contracts with Hardhat...")
        if not deploy_contracts_with_hardhat():
            raise Exception("Failed to deploy contracts with Hardhat")
        
        logger.info(f"{LOG_PREFIX_HARDHAT}Deployment completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"{LOG_PREFIX_HARDHAT}Error during deployment: {str(e)}")
        return False

if __name__ == "__main__":
    main()
