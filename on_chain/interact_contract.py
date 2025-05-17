# interact_contract.py - Uses ethers.js bridge to call functions on the blockchain.

import json
import os
import time
import subprocess
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

class BlockchainInteractor:
    def __init__(self):
        # Connection to Hardhat node
        self.node_url = "http://127.0.0.1:8545"
        max_attempts = 10
        for i in range(max_attempts):
            try:
                response = requests.post(
                    self.node_url,
                    json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                    timeout=2
                )
                if response.status_code == 200:
                    print("Connected to Hardhat node")
                    break
            except:
                if i == max_attempts - 1:
                    raise Exception("Failed to connect to Hardhat node")
                print(f"Waiting for Hardhat node... ({i+1}/{max_attempts})")
                time.sleep(1)

        # Load contract addresses and ABIs
        contract_data_path = Path(__file__).parent / "contract_addresses.json"
        with open(contract_data_path, 'r') as f:
            self.contract_data = json.load(f)
        
        # Create ethers.js bridge script if it doesn't exist
        self.bridge_path = Path(__file__).parent / "ethers_bridge.js"
        if not self.bridge_path.exists():
            self._create_ethers_bridge()
        
        # Get default account
        self.default_account = self._call_bridge("getDefaultAccount", [])
        print(f"Using default account: {self.default_account}")

    def _create_ethers_bridge(self):
        """Create the ethers.js bridge script"""
        bridge_code = """
        const { ethers } = require('ethers');
        const fs = require('fs');
        const path = require('path');

        // Read contract data
        const contractDataPath = path.join(__dirname, 'contract_addresses.json');
        const contractData = JSON.parse(fs.readFileSync(contractDataPath, 'utf8'));

        // Connect to provider
        const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');

        // Get wallet from provider
        async function getWallet() {
            const accounts = await provider.listAccounts();
            return accounts[0];
        }

        // Get contract instance
        function getContract(contractName) {
            const contractInfo = contractData.contracts[contractName];
            return new ethers.Contract(
                contractInfo.address,
                contractInfo.abi,
                provider
            );
        }

        // Get contract with signer
        async function getSignedContract(contractName) {
            const wallet = await getWallet();
            const signer = await provider.getSigner(wallet);
            const contractInfo = contractData.contracts[contractName];
            return new ethers.Contract(
                contractInfo.address,
                contractInfo.abi,
                signer
            );
        }

        // Bridge functions
        async function getDefaultAccount() {
            const wallet = await getWallet();
            return wallet;
        }

        async function registerUser(name, email, role) {
            try {
                const contract = await getSignedContract('UserRegistry');
                const tx = await contract.registerUser(name, email, role);
                const receipt = await tx.wait();
                return receipt.status === 1;
            } catch (error) {
                console.error('Error registering user:', error);
                return false;
            }
        }

        async function getUser(address) {
            try {
                const contract = getContract('UserRegistry');
                const isRegistered = await contract.isUserRegistered(address);
                if (!isRegistered) return {};
                
                const user = await contract.getUser(address);
                return {
                    name: user[0],
                    email: user[1],
                    role: user[2],
                    isActive: user[3],
                    registrationDate: user[4].toString()
                };
            } catch (error) {
                console.error('Error getting user:', error);
                return {};
            }
        }

        async function createProduct(name, description, category, unit, metadata) {
            try {
                const contract = await getSignedContract('ProductRegistry');
                const tx = await contract.createProduct(name, description, category, unit, metadata || '');
                const receipt = await tx.wait();
                
                // Find the ProductCreated event to get the product ID
                const event = receipt.logs
                    .map(log => {
                        try {
                            return contract.interface.parseLog(log);
                        } catch (e) {
                            return null;
                        }
                    })
                    .filter(event => event && event.name === 'ProductCreated')[0];
                
                return event ? parseInt(event.args.productId) : 0;
            } catch (error) {
                console.error('Error creating product:', error);
                return 0;
            }
        }

        async function getProduct(productId) {
            try {
                const contract = getContract('ProductRegistry');
                const product = await contract.getProduct(productId);
                return {
                    id: parseInt(product[0]),
                    name: product[1],
                    description: product[2],
                    category: product[3],
                    unit: product[4],
                    producer: product[5],
                    createdAt: product[6].toString(),
                    isActive: product[7],
                    metadata: product[8]
                };
            } catch (error) {
                console.error('Error getting product:', error);
                return {};
            }
        }

        // Handle command line arguments
        async function main() {
            const args = process.argv.slice(2);
            const functionName = args[0];
            const functionArgs = JSON.parse(args[1] || '[]');
            
            if (typeof global[functionName] === 'function') {
                try {
                    const result = await global[functionName](...functionArgs);
                    console.log(JSON.stringify(result));
                } catch (error) {
                    console.error('Error executing function:', error);
                    process.exit(1);
                }
            } else {
                console.error(`Function ${functionName} not found`);
                process.exit(1);
            }
        }

        // Export functions to global scope
        global.getDefaultAccount = getDefaultAccount;
        global.registerUser = registerUser;
        global.getUser = getUser;
        global.createProduct = createProduct;
        global.getProduct = getProduct;

        main();
        """
        with open(self.bridge_path, 'w') as f:
            f.write(bridge_code)
    
    def _call_bridge(self, function_name: str, args: List[Any]) -> Any:
        """Call the ethers.js bridge with the given function and arguments"""
        try:
            # Convert arguments to JSON string
            args_json = json.dumps(args)
            
            # Call the bridge script with Node.js
            result = subprocess.run(
                ["node", str(self.bridge_path), function_name, args_json],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent)
            )
            
            if result.returncode != 0:
                print(f"Error calling bridge: {result.stderr}")
                return None
            
            # Parse the JSON result
            return json.loads(result.stdout)
            
        except Exception as e:
            print(f"Error in bridge call: {e}")
            return None
    
    def register_user(self, name: str, email: str, role: str) -> bool:
        """Register a new user in the system"""
        try:
            result = self._call_bridge("registerUser", [name, email, role])
            return bool(result)
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    def get_user(self, address: str) -> Dict[str, Any]:
        """Get user information"""
        try:
            result = self._call_bridge("getUser", [address])
            return result if result else {}
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {}

    def create_product(self, name: str, description: str, category: str, unit: str, metadata: str = "") -> int:
        """Create a new product in the system"""
        try:
            result = self._call_bridge("createProduct", [name, description, category, unit, metadata])
            return int(result) if result is not None else 0
        except Exception as e:
            print(f"Error creating product: {e}")
            return 0

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get product information"""
        try:
            result = self._call_bridge("getProduct", [product_id])
            return result if result else {}
        except Exception as e:
            print(f"Error getting product: {e}")
            return {}

def main():
    # Example usage
    try:
        interactor = BlockchainInteractor()
        
        # Register a new user
        success = interactor.register_user(
            name="John Doe",
            email="john.doe@example.com",
            role="PRODUCER"
        )
        print(f"User registration {'successful' if success else 'failed'}")
        
        if success:
            # Verify user information
            user_info = interactor.get_user(interactor.default_account)
            print(f"User info: {user_info}")
        
        # Register a new product
        product_id = interactor.create_product(
            name="Organic Apple",
            description="Fresh organic apples from local farms",
            category="Fruit",
            unit="kg"
        )
        
        if product_id > 0:
            print(f"Product created with ID: {product_id}")
            # Verify product information
            product_info = interactor.get_product(product_id)
            print(f"Product info: {product_info}")
        else:
            print("Product creation failed")
        
    except Exception as e:
        print(f"Error in main: {e}")
        
    print("\nNote: Make sure the Hardhat node is running before using this script.")
    print("You can start it with 'python start_blockchain.py'")

if __name__ == "__main__":
    main()