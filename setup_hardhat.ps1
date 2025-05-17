# setup_hardhat.ps1 - Setup script for Hardhat environment on Windows

# Check if Node.js is installed
try {
    $nodeVersion = node -v
    Write-Host "Node.js is installed: $nodeVersion"
}
catch {
    Write-Host "Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
}

# Navigate to on_chain directory
Set-Location -Path "$PSScriptRoot\on_chain"

# Install dependencies
Write-Host "Installing Hardhat and dependencies..."
npm install

# Compile contracts
Write-Host "Compiling smart contracts..."
npx hardhat compile

Write-Host "Setup completed successfully!"
Write-Host "To start the blockchain, run: python ..\start_blockchain.py"
