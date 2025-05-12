# Sistema Blockchain per Supply Chain Sostenibile

Questo progetto contiene gli smart contracts e gli strumenti per gestire una supply chain alimentare sostenibile su blockchain.

## Requisiti

- Node.js e npm
- Python 3.7+
- Truffle (`npm install -g truffle`)
- Ganache (scegli uno dei seguenti metodi):
  - Ganache UI: [Download Ganache](https://trufflesuite.com/ganache/)
  - Ganache CLI: `npm install -g ganache-cli`

## Installazione

1. Installa le dipendenze Node.js:

```bash
cd on_chain
npm install
```

2. Installa le dipendenze Python:

```bash
pip install -r requirements.txt
```

3. Configura Ganache:

   - **Opzione 1: Ganache UI**
     - Avvia l'applicazione Ganache UI
     - Crea un nuovo workspace (o usa quello di default)
     - Configura la porta su 7545 (impostazione predefinita)
     - Nel tab "Server", assicurati che l'indirizzo sia impostato su `127.0.0.1:7545`

   - **Opzione 2: Ganache CLI**
     - Esegui il comando:
     ```bash
     ganache-cli --port 7545 --accounts 10 --gasLimit 8000000 --defaultBalanceEther 1000
     ```

4. Compila e deploya i contratti:

```bash
truffle compile
truffle migrate --reset
```

5. Verifica che gli indirizzi siano stati salvati nel file `contract-addresses.json`. Se il file non esiste o è vuoto, esegui lo script di migrazione Truffle.

## Smart Contracts

I contratti includono:

- `CO2Token`: Token per tracciare e incentivare la riduzione di CO2
- `UserRegistry`: Registro degli utenti della supply chain
- `ProductRegistry`: Registro dei prodotti
- `OperationRegistry`: Registro delle operazioni
- `SustainabilityMetrics`: Metriche di sostenibilità
- `QualityControl`: Controllo qualità
- `ProductRequest`: Richieste di prodotti
- `SupplyChain`: Contratto principale che coordina l'intero sistema

## Configurazione Blockchain

### Sviluppo Locale

Per sviluppo locale, puoi utilizzare tre approcci:

1. **Avvio manuale (raccomandato per iniziare)**:
   - Avvia Ganache UI o Ganache CLI
   - Apri un terminale e esegui:
   ```bash
   cd on_chain
   truffle migrate --reset
   ```

2. **Utilizzando l'applicazione principale**:
   - Avvia l'applicazione off-chain:
   ```bash
   cd off_chain
   python sfs_off_chain_app.py
   ```
   - L'applicazione tenterà di avviare automaticamente l'ambiente blockchain

3. **Truffle Develop**:
   ```bash
   cd on_chain
   truffle develop
   migrate --reset
   ```

### Testnet o Mainnet

Per deployare su una rete pubblica:

1. Copia `.env-template` in `.env` e inserisci le tue chiavi:

```bash
cp .env-template .env
```

2. Modifica il file `.env` con:
   - Chiave API Infura
   - Mnemonic o chiave privata del wallet
   - (Opzionale) Chiavi API per Etherscan/Polygonscan

3. Esegui il deploy sulla rete desiderata:

```bash
# Per Sepolia (testnet consigliata)
npm run deploy:sepolia

# Per altre reti
npm run deploy:goerli
npm run deploy:mumbai
npm run deploy:polygon
npm run deploy:mainnet
```

## Risoluzione dei problemi

### Ganache non si avvia

Se lo script automatico non riesce ad avviare Ganache, prova questi passaggi:

1. Verifica che Ganache sia installato correttamente:
   ```bash
   ganache-cli --version
   ```

2. Se Ganache CLI non è installato, installalo:
   ```bash
   npm install -g ganache-cli
   ```

3. Se preferisci, usa la versione UI di Ganache:
   - Scarica da [Ganache UI](https://trufflesuite.com/ganache/)
   - Avvia l'applicazione
   - Imposta la porta su 7545

4. Se tutto il resto fallisce, avvia manualmente Ganache e poi esegui:
   ```bash
   cd on_chain
   truffle migrate --reset
   ```

### Errori di connessione

Se riscontri errori di connessione:

1. Verifica che Ganache sia in esecuzione sulla porta 7545
2. Verifica la configurazione di rete in `truffle-config.js`
3. Controlla i log per messaggi di errore specifici

## Interagire con i Contratti

Puoi interagire con i contratti usando lo script Python:

```bash
python interact_contract.py
```

Lo script ti chiederà di selezionare la rete a cui connetterti.

## Integrazione con la tua Applicazione

Per integrare la blockchain nella tua applicazione:

1. All'avvio dell'app, esegui lo script `startup.py`
2. Importa le funzioni da `interact_contract.py` nel tuo codice principale
3. Usa la funzione `load_contract()` per caricare i contratti

Esempio:

```python
from interact_contract import load_contract, w3

# Carica il contratto
co2_token = load_contract('CO2Token')

# Interagisci con il contratto
balance = co2_token.functions.balanceOf(address).call()
```

## Utility Incluse

- `setup_ganache.py`: Gestisce l'avvio di Ganache e il deployment dei contratti
- `startup.py`: Script di avvio completo per l'integrazione nell'applicazione
- `interact_contract.py`: Funzioni per interagire con i contratti
- `deploy_contract.py`: Utility per deployare i contratti manualmente 