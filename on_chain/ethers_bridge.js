
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
        