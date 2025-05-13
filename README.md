# Sustainable Food Supply Chain Project

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
  - Audit.sol for compliance verification

## Prerequisites
### Off-Chain Components
- Python 3.13+
- Node.js 18+ (for dashboard frontend)
- Docker 24+

### On-Chain Components
- Ethereum client (Geth or Parity)
- MetaMask wallet for development
- Hardhat 2.12+ for contract testing
- 0.5 ETH testnet funds (for deployment)

## Installation
### Development Setup
1. Clone repository:
```bash
git clone https://github.com/Catalinaqi/Project_Sustainable_Food_Supply_Chain.git
cd Project_Sustainable_Food_Supply_Chain
```
2. Install dependencies:
```bash
poetry install
npm install
```
3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your:
# - Infura API key
# - Wallet private key
# - Database credentials
```
4. Start services:
```bash
# Start blockchain node
docker-compose up -d geth
# Deploy contracts
poetry run python scripts/deploy_contracts.py
# Start application
poetry run sfc
```

## Running the Application
### Development Mode
1. Start local Ethereum node:
```bash
poetry run python -m scripts.start_node
```
2. Deploy contracts:
```bash
poetry run python scripts/deploy_contracts.py
```
3. Run application:
```bash
poetry run sfc
```

### Production Deployment
1. Build containers:
```bash
docker-compose build
```
2. Configure production .env:
```bash
nano .env.production
```
3. Start services:
```bash
docker-compose --env-file .env.production up -d
```
4. Verify deployment:
```bash
docker-compose logs -f
```

## Configuration
Edit `.env` file to configure:
- Database connection
- Blockchain network settings
- Application secrets

## Contributing
Pull requests are welcome. Please follow the existing code style and include tests.

## License
[MIT](LICENSE)
