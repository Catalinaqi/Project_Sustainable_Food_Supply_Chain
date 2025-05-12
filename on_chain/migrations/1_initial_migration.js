const CO2Token = artifacts.require("CO2Token");
const SupplyChain = artifacts.require("SupplyChain");
const ProductRegistry = artifacts.require("ProductRegistry");
const OperationRegistry = artifacts.require("OperationRegistry");
const UserRegistry = artifacts.require("UserRegistry");
const SustainabilityMetrics = artifacts.require("SustainabilityMetrics");
const QualityControl = artifacts.require("QualityControl");
const ProductRequest = artifacts.require("ProductRequest");

module.exports = function(deployer) {
  // Deployo i contratti in ordine di dipendenza
  deployer.deploy(CO2Token)
    .then(() => deployer.deploy(UserRegistry))
    .then(() => deployer.deploy(ProductRegistry))
    .then(() => deployer.deploy(OperationRegistry))
    .then(() => deployer.deploy(SustainabilityMetrics))
    .then(() => deployer.deploy(QualityControl))
    .then(() => deployer.deploy(ProductRequest))
    .then(() => deployer.deploy(SupplyChain));
}; 