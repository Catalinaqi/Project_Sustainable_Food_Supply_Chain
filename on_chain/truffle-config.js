/**
 * Configurazione di Truffle per il progetto Sustainable Food Supply Chain
 */

// Comentato temporaneamente per evitare l'errore dotenv
// require('dotenv').config();  // Carica le variabili d'ambiente da .env
// const HDWalletProvider = require('@truffle/hdwallet-provider');

// Ottieni il mnemonic e la chiave API di Infura dal file .env
const mnemonic = ''; // process.env.MNEMONIC || '';
const infuraKey = ''; // process.env.INFURA_API_KEY || '';

module.exports = {
  // Specificare le directory
  contracts_directory: './contracts',
  migrations_directory: './migrations',
  test_directory: './test',

  // Configurazione delle reti
  networks: {
    // Rete di sviluppo locale (predefinita)
    development: {
      host: "127.0.0.1",
      port: 7545,        // Porta predefinita per Ganache UI e CLI
      network_id: "*"    // Match qualsiasi network id
    },
    
    // Configurazione specifica per Ganache UI
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*",
      gas: 6721975       // Limite gas predefinito per Ganache
    },
    
    // Truffle develop
    develop: {
      host: "127.0.0.1", 
      port: 9545,
      network_id: "*"
    }
    
    /* Commentato per evitare errori
    // Sepolia testnet (sostituisce Goerli come testnet principale)
    sepolia: {
      provider: () => new HDWalletProvider(
        mnemonic, 
        `https://sepolia.infura.io/v3/${infuraKey}`
      ),
      network_id: 11155111,
      gas: 5500000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    },
    
    // Rete Goerli (testnet Ethereum)
    goerli: {
      provider: () => new HDWalletProvider(
        mnemonic, 
        `https://goerli.infura.io/v3/${infuraKey}`
      ),
      network_id: 5,
      gas: 5500000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    },
    
    // Mainnet Ethereum
    mainnet: {
      provider: () => new HDWalletProvider(
        mnemonic, 
        `https://mainnet.infura.io/v3/${infuraKey}`
      ),
      network_id: 1,
      gas: 5500000,
      gasPrice: 120000000000,  // 120 gwei
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: false  // Impostato a false per mainnet per evitare deploy accidentali
    },
    
    // Polygon (Matic) Mainnet
    polygon: {
      provider: () => new HDWalletProvider(
        mnemonic, 
        `https://polygon-mainnet.infura.io/v3/${infuraKey}`
      ),
      network_id: 137,
      gas: 5500000,
      gasPrice: 35000000000, // 35 gwei
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: false
    },
    
    // Mumbai (Testnet Polygon)
    mumbai: {
      provider: () => new HDWalletProvider(
        mnemonic, 
        `https://polygon-mumbai.infura.io/v3/${infuraKey}`
      ),
      network_id: 80001,
      gas: 5500000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    }
    */
  },

  // Configurazione del compilatore Solidity
  compilers: {
    solc: {
      version: "0.8.0",    // Versione corrispondente ai contratti
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        }
      }
    }
  }
  
  /* Commentato per evitare errori
  // Plugin di Etherscan per verificare i contratti
  plugins: ['truffle-plugin-verify'],
  
  // Configurazione API di Etherscan per la verifica dei contratti
  api_keys: {
    etherscan: process.env.ETHERSCAN_API_KEY,
    polygonscan: process.env.POLYGONSCAN_API_KEY
  }
  */
}; 