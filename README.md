# Overview and technical steps for deploying the application

<<<<<<< Updated upstream
=======
## Overview
This project implements a blockchain-based solution for tracking sustainable food supply chains. It consists of:
- Off-chain components for user interfaces and business logic
- On-chain smart contracts for immutable record keeping

## Features
- **Traceability System**: Track food products from farm to table with QR code scanning
- **CO2 Token Economy**: Blockchain-based tokens reward sustainable practices
- **Authentication**: Multi-factor auth for supply chain participants (farmers, distributors, retailers)
- **Dashboard**: Real-time monitoring of sustainability metrics (carbon footprint, water usage)
- **Smart Contracts**:
  - ERC-20 CO2 tokens for sustainability incentives
  - SupplyChain.sol for immutable product records
  - QualityControl.sol for quality verification
  - SustainabilityMetrics.sol for environmental impact tracking

## Prerequisites
### Off-Chain Components
- Python 3.13+
- Poetry
- PyQt5
- Node.js 18+ (for blockchain interaction and dashboard frontend)

### On-Chain Components
- Hardhat for local Ethereum development
- ethers.js for blockchain interaction
- OpenZeppelin contracts for standard implementations
- MetaMask wallet for development (optional)
- 0.5 ETH testnet funds (for deployment to public networks)

## Installation
### Development Setup
1. Clone repository:
```bash
git clone https://github.com/Catalinaqi/Project_Sustainable_Food_Supply_Chain.git
cd Project_Sustainable_Food_Supply_Chain
```

2. Install dependencies:
```bash
poetry install  # For Python dependencies
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your:
# - Infura API key (if deploying to a testnet)
# - Database credentials
```

4. Set up Hardhat environment:

**On Windows:**
```powershell
.\setup_hardhat.ps1
```

**On Linux/macOS:**
```bash
chmod +x setup_hardhat.sh
./setup_hardhat.sh
```

## Running the Application
### Development Mode
1. Start local Hardhat node and deploy contracts:
```bash
python start_blockchain.py
```

2. In a new terminal, run the application:
```bash
poetry run sfc
```

### Hardhat Console
You can interact with the blockchain directly using the Hardhat console:
```bash
cd on_chain
npx hardhat console --network localhost
```

Example console commands:
```javascript
// Get accounts
const accounts = await ethers.getSigners();
console.log(accounts[0].address);

// Get UserRegistry contract
const UserRegistry = await ethers.getContractFactory("UserRegistry");
const userRegistry = await UserRegistry.attach("CONTRACT_ADDRESS");

// Call contract methods
const isRegistered = await userRegistry.isUserRegistered(accounts[0].address);
console.log(isRegistered);
```

### Production Deployment
For production deployment to a public network (like Ethereum Mainnet or a testnet):

1. Configure your network in `on_chain/hardhat.config.js`

2. Deploy to the desired network:
```bash
cd on_chain
npx hardhat run scripts/deploy.js --network <network-name>
```

## Configuration
Edit `.env` file to configure:
- Database connection
- Blockchain network settings (for testnet/mainnet deployments)
- Application secrets

## Project Structure
- `on_chain/` - Smart contracts and blockchain interaction
  - `contracts/` - Solidity smart contracts
  - `scripts/` - Deployment and interaction scripts
  - `hardhat.config.js` - Hardhat configuration
- `off_chain/` - Python application code
- `start_blockchain.py` - Helper script to start Hardhat node and deploy contracts
- `setup_hardhat.ps1` / `setup_hardhat.sh` - Setup scripts for Windows and Linux/macOS

## Contributing
Pull requests are welcome. Please follow the existing code style and include tests.

## License
[MIT](LICENSE)
>>>>>>> Stashed changes
