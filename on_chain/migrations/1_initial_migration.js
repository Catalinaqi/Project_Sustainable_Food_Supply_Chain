const CO2Token = artifacts.require("CO2Token");
const SupplyChain = artifacts.require("SupplyChain");
const ProductRegistry = artifacts.require("ProductRegistry");
const OperationRegistry = artifacts.require("OperationRegistry");
const UserRegistry = artifacts.require("UserRegistry");
const SustainabilityMetrics = artifacts.require("SustainabilityMetrics");
const QualityControl = artifacts.require("QualityControl");
const ProductRequest = artifacts.require("ProductRequest");
const fs = require('fs');
const path = require('path');

module.exports = function(deployer, network) {
  // Oggetto per memorizzare gli indirizzi
  let contractAddresses = {};
  
  // Leggi gli indirizzi esistenti se il file esiste
  const addressesPath = path.join(__dirname, '..', 'contract-addresses.json');
  if (fs.existsSync(addressesPath)) {
    const content = fs.readFileSync(addressesPath, 'utf8');
    try {
      contractAddresses = JSON.parse(content);
    } catch (e) {
      console.error('Errore nel parsing del file degli indirizzi:', e);
    }
  }

  // Deployo i contratti in ordine di dipendenza
  deployer.deploy(CO2Token)
    .then(instance => {
      contractAddresses['CO2Token'] = instance.address;
      return deployer.deploy(UserRegistry);
    })
    .then(instance => {
      contractAddresses['UserRegistry'] = instance.address;
      return deployer.deploy(ProductRegistry);
    })
    .then(instance => {
      contractAddresses['ProductRegistry'] = instance.address;
      return deployer.deploy(OperationRegistry);
    })
    .then(instance => {
      contractAddresses['OperationRegistry'] = instance.address;
      return deployer.deploy(SustainabilityMetrics);
    })
    .then(instance => {
      contractAddresses['SustainabilityMetrics'] = instance.address;
      return deployer.deploy(QualityControl);
    })
    .then(instance => {
      contractAddresses['QualityControl'] = instance.address;
      return deployer.deploy(ProductRequest);
    })
    .then(instance => {
      contractAddresses['ProductRequest'] = instance.address;
      return deployer.deploy(SupplyChain);
    })
    .then(instance => {
      contractAddresses['SupplyChain'] = instance.address;
      
      // Salva gli indirizzi in un file JSON
      fs.writeFileSync(
        addressesPath,
        JSON.stringify(contractAddresses, null, 2)
      );
      console.log('Indirizzi dei contratti salvati in:', addressesPath);
    });
}; 