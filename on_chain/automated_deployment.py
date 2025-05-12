import subprocess
import json
import time
import os
from web3 import Web3
from solcx import compile_standard, install_solc
import sys

def start_ganache():
    """Connect to running Ganache instance"""
    try:
        # Wait for Ganache to be ready
        max_attempts = 10
        for i in range(max_attempts):
            try:
                w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
                if w3.is_connected():
                    print("Connected to Ganache")
                    return True
            except:
                print(f"Waiting for Ganache... ({i+1}/{max_attempts})")
                time.sleep(1)
        
        print("Ganache started successfully")
        time.sleep(5)  # Give Ganache time to initialize
        return True
    except Exception as e:
        print(f"Error starting Ganache: {e}")
        sys.exit(1)

def compile_contracts():
    """Compile all Solidity contracts"""
    contract_sources = {}
    contracts_dir = os.path.join(os.path.dirname(__file__), "contracts")
    
    # Install specific Solidity version
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
        }
    }, solc_version="0.8.0")
    
    return compiled_contracts

def deploy_contracts(w3, compiled_contracts):
    """Deploy all contracts and return their addresses"""
    deployed_contracts = {}
    account = w3.eth.accounts[0]  # Use the first account as deployer
    
    for contract_file in compiled_contracts["contracts"].keys():
        for contract_name in compiled_contracts["contracts"][contract_file].keys():
            print(f"Deploying {contract_name}...")
            
            contract_data = compiled_contracts["contracts"][contract_file][contract_name]
            Contract = w3.eth.contract(
                abi=contract_data["abi"],
                bytecode=contract_data["evm"]["bytecode"]["object"]
            )
            
            # Deploy contract
            tx_hash = Contract.constructor().transact({"from": account})
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            deployed_contracts[contract_name] = {
                "address": tx_receipt.contractAddress,
                "abi": contract_data["abi"]
            }
            
            print(f"{contract_name} deployed at: {tx_receipt.contractAddress}")
    
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
        # Start Ganache
        start_ganache()
        
        # Connect to Ganache
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        if not w3.is_connected():
            raise Exception("Failed to connect to Ganache")
        
        # Compile contracts
        print("Compiling contracts...")
        compiled_contracts = compile_contracts()
        
        # Deploy contracts
        print("Deploying contracts...")
        deployed_contracts = deploy_contracts(w3, compiled_contracts)
        
        # Save contract data
        save_contract_data(deployed_contracts)
        
    except Exception as e:
        print(f"Error during deployment: {e}")
    finally:
        # Stop and remove Ganache container
        try:
            subprocess.run(["docker", "stop", "ganache-cli"], check=True)
            subprocess.run(["docker", "rm", "ganache-cli"], check=True)
            print("Ganache container stopped and removed")
        except Exception as e:
            print(f"Error stopping Ganache container: {e}")

if __name__ == "__main__":
    main()
