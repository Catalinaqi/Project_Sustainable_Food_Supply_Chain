# interact_contract.py - Utilizza contract_abi.json per chiamare funzioni sulla blockchain
import json
import os
from web3 import Web3

# Opzioni di connessione disponibili
PROVIDERS = {
    "truffle": "http://127.0.0.1:9545",  # Default per truffle develop
    "ganache": "http://127.0.0.1:7545",  # Default per Ganache GUI
    "ganache-cli": "http://127.0.0.1:8545"  # Default per ganache-cli
}

def select_provider():
    """
    Permette all'utente di selezionare un provider
    """
    print("Seleziona un provider:")
    print("1. Truffle Develop (porta 9545)")
    print("2. Ganache GUI (porta 7545)")
    print("3. Ganache CLI (porta 8545)")
    print("4. Inserisci un URL personalizzato")
    
    choice = input("Scelta [1]: ") or "1"
    
    if choice == "1":
        return PROVIDERS["truffle"]
    elif choice == "2":
        return PROVIDERS["ganache"]
    elif choice == "3":
        return PROVIDERS["ganache-cli"]
    elif choice == "4":
        return input("Inserisci l'URL del provider: ")
    else:
        print("Scelta non valida, uso il provider Truffle predefinito")
        return PROVIDERS["truffle"]

# Configura il provider Web3
PROVIDER_URL = select_provider()
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
        # Usa il primo account disponibile
        default_account = w3.eth.accounts[0]
        w3.eth.default_account = default_account
        print(f"Account di default: {default_account}")
        
        # Esegui l'esempio di interazione
        interact_with_co2_token()
    else:
        print(f"Impossibile connettersi a {PROVIDER_URL}")
        print("Assicurati di aver avviato il nodo Ethereum corretto:")
        print("- Per Truffle: cd on_chain && truffle develop")
        print("- Per Ganache GUI: avvia l'applicazione Ganache")
        print("- Per Ganache CLI: npx ganache-cli")