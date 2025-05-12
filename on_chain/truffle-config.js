/**
 * Configurazione di Truffle per il progetto Sustainable Food Supply Chain
 */

module.exports = {
  // Specificare le directory
  contracts_directory: './contracts',
  migrations_directory: './migrations',
  test_directory: './test',

  // Configurazione delle reti
  networks: {
    // Rete di sviluppo locale
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*" // Match qualsiasi network id
    },
    
    // Rete di test (esempio Goerli)
    goerli: {
      // provider: () => new HDWalletProvider(mnemonic, `https://goerli.infura.io/v3/${infuraKey}`),
      network_id: 5,       // Goerli's id
      confirmations: 2,    // # di conferme da attendere per i blocchi
      timeoutBlocks: 200,  // # di blocchi prima del timeout
      skipDryRun: true     // Skip dry run per test sulla rete
    },
    
    // Mainnet Ethereum
    mainnet: {
      // provider: () => new HDWalletProvider(mnemonic, `https://mainnet.infura.io/v3/${infuraKey}`),
      network_id: 1,
      gasPrice: 120000000000,  // 120 gwei
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    }
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
  },
  
  // Plugin (decommentare se necessario)
  // plugins: ["truffle-contract-size"]
}; 