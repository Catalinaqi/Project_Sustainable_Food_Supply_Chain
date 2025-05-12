# interact_contract.py - Utilizza contract_abi.json per chiamare funzioni sulla blockchain
import json
import os
from web3 import Web3
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

# Opzioni di connessione disponibili
PROVIDERS = {
    "truffle": "http://127.0.0.1:9545",  # Default per truffle develop
    "ganache": "http://127.0.0.1:7545",  # Default per Ganache GUI
    "ganache-cli": "http://127.0.0.1:8545",  # Default per ganache-cli
    "sepolia": f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}",
    "goerli": f"https://goerli.infura.io/v3/{os.getenv('INFURA_API_KEY')}",
    "mainnet": f"https://mainnet.infura.io/v3/{os.getenv('INFURA_API_KEY')}",
    "polygon": f"https://polygon-mainnet.infura.io/v3/{os.getenv('INFURA_API_KEY')}",
    "mumbai": f"https://polygon-mumbai.infura.io/v3/{os.getenv('INFURA_API_KEY')}"
}

def select_provider():
    """
    Permette all'utente di selezionare un provider
    """
    print("Seleziona un provider:")
    print("1. Truffle Develop (porta 9545)")
    print("2. Ganache GUI (porta 7545)")
    print("3. Ganache CLI (porta 8545)")
    print("4. Sepolia Testnet [Ethereum]")
    print("5. Goerli Testnet [Ethereum]")
    print("6. Ethereum Mainnet")
    print("7. Polygon Mainnet")
    print("8. Mumbai Testnet [Polygon]")
    print("9. Inserisci un URL personalizzato")
    
    choice = input("Scelta [1]: ") or "1"
    
    if choice == "1":
        return PROVIDERS["truffle"], False
    elif choice == "2":
        return PROVIDERS["ganache"], False
    elif choice == "3":
        return PROVIDERS["ganache-cli"], False
    elif choice == "4":
        return PROVIDERS["sepolia"], True
    elif choice == "5":
        return PROVIDERS["goerli"], True
    elif choice == "6":
        return PROVIDERS["mainnet"], True
    elif choice == "7":
        return PROVIDERS["polygon"], True
    elif choice == "8":
        return PROVIDERS["mumbai"], True
    elif choice == "9":
        return input("Inserisci l'URL del provider: "), False
    else:
        print("Scelta non valida, uso il provider Truffle predefinito")
        return PROVIDERS["truffle"], False

# Configura il provider Web3
PROVIDER_URL, is_public_network = select_provider()

# Se è una rete pubblica, configura il provider con un account
if is_public_network:
    from web3.middleware import geth_poa_middleware
    from eth_account import Account
    
    # Ottieni la chiave privata dall'ambiente (non condividere mai in codice!)
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("ATTENZIONE: Chiave privata non trovata nel file .env")
        private_key = input("Inserisci la chiave privata (senza 0x): ")
        private_key = "0x" + private_key if not private_key.startswith("0x") else private_key

    # Crea il provider Web3
    w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
    
    # Aggiungi middleware per reti PoA come Goerli/Sepolia
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Aggiungi l'account alla Web3
    account = Account.from_key(private_key)
    w3.eth.default_account = account.address
    print(f"Account: {account.address}")
else:
    # Per reti locali, usa il provider standard
    w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

def load_contract(contract_name):
    """
    Carica un contratto usando il suo nome
    """
    # Leggi l'indirizzo del contratto dal file JSON
    with open('contract-addresses.json', 'r') as f:
        addresses = json.load(f)
        
    contract_address = addresses.get(contract_name)
    if not contract_address:
        raise ValueError(f"Indirizzo del contratto {contract_name} non trovato.")
    
    # Leggi l'ABI del contratto da un file build o da un file separato
    contract_build_path = os.path.join('build', 'contracts', f'{contract_name}.json')
    if os.path.exists(contract_build_path):
        with open(contract_build_path, 'r') as f:
            build_data = json.load(f)
            abi = build_data['abi']
    else:
        # Se il file build non esiste, prova a leggere da un file ABI separato
        with open(f'{contract_name.lower()}_abi.json', 'r') as f:
            abi = json.load(f)
    
    # Crea e restituisci l'istanza del contratto
    return w3.eth.contract(address=contract_address, abi=abi)

def interact_with_co2_token():
    """
    Esempio di interazione con il contratto CO2Token
    """
    # Carica il contratto
    co2_token = load_contract('CO2Token')
    
    # Verifica se siamo su una rete pubblica o locale
    if is_public_network:
        # Usa l'account configurato
        account = w3.eth.default_account
        
        # Lettura dei dati (non richiede gas)
        try:
            token_name = co2_token.functions.name().call()
            print(f"Nome del token: {token_name}")
            
            balance = co2_token.functions.balanceOf(account).call()
            print(f"Saldo dell'account {account}: {balance}")
            
            # Chiedi all'utente se vuole eseguire una transazione
            execute_tx = input("Vuoi eseguire una transazione? (y/n): ").lower() == 'y'
            if execute_tx:
                # Costruisci la transazione
                tx = co2_token.functions.rewardCompensatoryAction(1000).build_transaction({
                    'from': account,
                    'gas': 200000,
                    'gasPrice': w3.eth.gas_price,
                    'nonce': w3.eth.get_transaction_count(account),
                })
                
                # Firma la transazione
                signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                
                # Invia la transazione
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"Transazione inviata: {tx_hash.hex()}")
                
                # Attendi la conferma
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Transazione completata: {receipt.transactionHash.hex()}")
                
                # Verifica il nuovo saldo
                new_balance = co2_token.functions.balanceOf(account).call()
                print(f"Nuovo saldo: {new_balance}")
        except Exception as e:
            print(f"Errore durante l'interazione con il contratto: {str(e)}")
    else:
        # Per reti locali, usa il metodo più semplice
        # Ottieni un account da usare per le transazioni
        account = w3.eth.accounts[0]
        
        # Ottieni il nome del token
        token_name = co2_token.functions.name().call()
        print(f"Nome del token: {token_name}")
        
        # Ottieni il saldo di un account
        balance = co2_token.functions.balanceOf(account).call()
        print(f"Saldo dell'account {account}: {balance}")
        
        # Esempio di transazione: ricompensare un'azione compensativa
        tx_hash = co2_token.functions.rewardCompensatoryAction(1000).transact({
            'from': account,
            'gas': 200000
        })
        
        # Attendi la conferma della transazione
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transazione completata: {receipt.transactionHash.hex()}")
        
        # Verifica il nuovo saldo
        new_balance = co2_token.functions.balanceOf(account).call()
        print(f"Nuovo saldo: {new_balance}")

if __name__ == "__main__":
    # Verifica la connessione
    if w3.is_connected():
        print(f"Connesso a {PROVIDER_URL}")
        
        # Esegui l'esempio di interazione
        interact_with_co2_token()
    else:
        print(f"Impossibile connettersi a {PROVIDER_URL}")
        print("Assicurati di aver avviato il nodo Ethereum corretto:")
        print("- Per Truffle: cd on_chain && truffle develop")
        print("- Per Ganache GUI: avvia l'applicazione Ganache")
        print("- Per Ganache CLI: npx ganache-cli")
        print("- Per reti pubbliche: controlla la tua chiave API di Infura nel file .env")