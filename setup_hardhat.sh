#!/bin/bash
# setup_hardhat.sh - Setup script for Hardhat environment on Linux/macOS

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "Node.js is installed: $(node -v)"

# Navigate to on_chain directory
cd "$(dirname "$0")/on_chain" || exit 1

# Install dependencies
echo "Installing Hardhat and dependencies..."
npm install

# Compile contracts
echo "Compiling smart contracts..."
npx hardhat compile

echo "Setup completed successfully!"
echo "To start the blockchain, run: python ../start_blockchain.py"

# Make the script executable
chmod +x "$(dirname "$0")/start_blockchain.py"
