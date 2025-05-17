// scripts/deploy.js
// Deploys all contracts for the Sustainable Food Supply Chain project

const { ethers } = require("hardhat");

async function main() {
  console.log("Starting deployment process...");
  
  // Get the signers (accounts)
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying contracts with the account: ${deployer.address}`);

  // Deploy UserRegistry
  console.log("Deploying UserRegistry...");
  const UserRegistry = await ethers.getContractFactory("UserRegistry");
  const userRegistry = await UserRegistry.deploy();
  await userRegistry.deploymentTransaction().wait();
  console.log(`UserRegistry deployed to: ${await userRegistry.getAddress()}`);

  // Deploy ProductRegistry
  console.log("Deploying ProductRegistry...");
  const ProductRegistry = await ethers.getContractFactory("ProductRegistry");
  const productRegistry = await ProductRegistry.deploy();
  await productRegistry.deploymentTransaction().wait();
  console.log(`ProductRegistry deployed to: ${await productRegistry.getAddress()}`);

  // Deploy OperationRegistry
  console.log("Deploying OperationRegistry...");
  const OperationRegistry = await ethers.getContractFactory("OperationRegistry");
  const operationRegistry = await OperationRegistry.deploy();
  await operationRegistry.deploymentTransaction().wait();
  console.log(`OperationRegistry deployed to: ${await operationRegistry.getAddress()}`);

  // Deploy QualityControl
  console.log("Deploying QualityControl...");
  const QualityControl = await ethers.getContractFactory("QualityControl");
  const qualityControl = await QualityControl.deploy();
  await qualityControl.deploymentTransaction().wait();
  console.log(`QualityControl deployed to: ${await qualityControl.getAddress()}`);

  // Deploy SustainabilityMetrics
  console.log("Deploying SustainabilityMetrics...");
  const SustainabilityMetrics = await ethers.getContractFactory("SustainabilityMetrics");
  const sustainabilityMetrics = await SustainabilityMetrics.deploy();
  await sustainabilityMetrics.deploymentTransaction().wait();
  console.log(`SustainabilityMetrics deployed to: ${await sustainabilityMetrics.getAddress()}`);

  // Deploy CO2Token
  console.log("Deploying CO2Token...");
  const CO2Token = await ethers.getContractFactory("CO2Token");
  const co2Token = await CO2Token.deploy();
  await co2Token.deploymentTransaction().wait();
  const co2TokenAddress = await co2Token.getAddress();
  console.log(`CO2Token deployed to: ${co2TokenAddress}`);

  // Deploy ProductRequest
  console.log("Deploying ProductRequest...");
  const ProductRequest = await ethers.getContractFactory("ProductRequest");
  const productRequest = await ProductRequest.deploy();
  await productRequest.deploymentTransaction().wait();
  console.log(`ProductRequest deployed to: ${await productRequest.getAddress()}`);

  // Deploy SupplyChainCO2
  console.log("Deploying SupplyChainCO2...");
  const SupplyChainCO2 = await ethers.getContractFactory("SupplyChainCO2");
  const supplyChainCO2 = await SupplyChainCO2.deploy();
  await supplyChainCO2.deploymentTransaction().wait();
  console.log(`SupplyChainCO2 deployed to: ${await supplyChainCO2.getAddress()}`);

  // Deploy SupplyChain (main contract)
  console.log("Deploying SupplyChain...");
  const SupplyChain = await ethers.getContractFactory("SupplyChain");
  const supplyChain = await SupplyChain.deploy();
  await supplyChain.deploymentTransaction().wait();
  console.log(`SupplyChain deployed to: ${await supplyChain.getAddress()}`);
  
  // Initialize SupplyChain with contract addresses
  console.log("Initializing SupplyChain...");
  const initTx = await supplyChain.initialize(
    await userRegistry.getAddress(),
    await productRequest.getAddress(),
    await operationRegistry.getAddress()
  );
  await initTx.wait();
  console.log("SupplyChain initialized successfully");

  // Save contract addresses and ABIs to a JSON file
  const fs = require("fs");
  const path = require("path");
  
  // Get all the contract addresses
  const contracts = {
    contracts: {
      UserRegistry: {
        address: await userRegistry.getAddress(),
        abi: UserRegistry.interface.format('json')
      },
      ProductRegistry: {
        address: await productRegistry.getAddress(),
        abi: ProductRegistry.interface.format('json')
      },
      OperationRegistry: {
        address: await operationRegistry.getAddress(),
        abi: OperationRegistry.interface.format('json')
      },
      QualityControl: {
        address: await qualityControl.getAddress(),
        abi: QualityControl.interface.format('json')
      },
      SustainabilityMetrics: {
        address: await sustainabilityMetrics.getAddress(),
        abi: SustainabilityMetrics.interface.format('json')
      },
      CO2Token: {
        address: await co2Token.getAddress(),
        abi: CO2Token.interface.format('json')
      },
      ProductRequest: {
        address: await productRequest.getAddress(),
        abi: ProductRequest.interface.format('json')
      },
      SupplyChainCO2: {
        address: await supplyChainCO2.getAddress(),
        abi: SupplyChainCO2.interface.format('json')
      },
      SupplyChain: {
        address: await supplyChain.getAddress(),
        abi: SupplyChain.interface.format('json')
      }
    }
  };

  const contractAddressesPath = path.join(__dirname, "..", "contract_addresses.json");
  fs.writeFileSync(contractAddressesPath, JSON.stringify(contracts, null, 2));
  console.log(`Contract addresses and ABIs saved to ${contractAddressesPath}`);

  console.log("Deployment completed successfully!");
}

// Execute the deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error during deployment:", error);
    process.exit(1);
  });
