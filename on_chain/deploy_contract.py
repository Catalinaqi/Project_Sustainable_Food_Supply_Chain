# deploy_contract.py - Compila e deploya i contratti sulla blockchain
import json
import os
import subprocess
import solcx
from web3 import Web3

# Configura il provider Web3
PROVIDER_URL = "http://127.0.0.1:9545"  # Default per truffle develop
w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

def compile_contract(contract_file):
    """
    Compila un contratto Solidity e ritorna il bytecode e l'ABI
    """
    # Percorso completo del file contratto
    contract_path = os.path.join('contracts', contract_file)
    
    # Installa la versione di solc se necessario (solo la prima volta)
    try:
        solcx.install_solc('0.8.0')
    except Exception as e:
        print(f"Errore durante l'installazione di solc: {e}")
        
    # Imposta la versione di solc da usare
    solcx.set_solc_version('0.8.0')
    
    # Compila il contratto
    with open(contract_path, 'r') as file:
        contract_source = file.read()
    
    compiled_sol = solcx.compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.0'
    )
    
    # Estrai le informazioni del contratto
    contract_id, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    
    return bytecode, abi

def deploy_contract(bytecode, abi, *constructor_args):
    """
    Deploya un contratto sulla blockchain e ne ritorna l'indirizzo
    """
    # Ottieni un account da usare per il deployment
    account = w3.eth.accounts[0]
    
    # Crea l'istanza del contratto
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Costruisci e invia la transazione per il deployment
    # Nota: se il contratto ha argomenti nel costruttore, aggiungerli qui
    tx_hash = Contract.constructor(*constructor_args).transact({
        'from': account,
        'gas': 5000000  # Limite gas per il deployment
    })
    
    # Attendi il mining della transazione
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contratto deployato a: {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress

def deploy_all_contracts():
    """
    Deploya tutti i contratti e salva gli indirizzi
    """
    # Dizionario per memorizzare gli indirizzi
    addresses = {}
    
    # Ordine di deployment (lo stesso del file di migrazione)
    contracts = [
        'CO2Token.sol',
        'UserRegistry.sol',
        'ProductRegistry.sol',
        'OperationRegistry.sol',
        'SustainabilityMetrics.sol',
        'QualityControl.sol',
        'ProductRequest.sol',
        'SupplyChain.sol'
    ]
    
    # Esegui il deployment di ogni contratto
    for contract_file in contracts:
        contract_name = contract_file.split('.')[0]
        print(f"Compilazione di {contract_name}...")
        bytecode, abi = compile_contract(contract_file)
        
        print(f"Deployment di {contract_name}...")
        contract_address = deploy_contract(bytecode, abi)
        addresses[contract_name] = contract_address
        
        # Salva l'ABI in un file separato
        with open(f'{contract_name.lower()}_abi.json', 'w') as f:
            json.dump(abi, f, indent=2)
        
    # Salva tutti gli indirizzi nel file contract-addresses.json
    with open('contract-addresses.json', 'w') as f:
        json.dump(addresses, f, indent=2)
    
    print(f"Tutti i contratti deployati con successo. Indirizzi salvati in contract-addresses.json")

def deploy_with_truffle():
    """
    Alternativa: usa truffle per deployare i contratti
    """
    try:
        # Esegui il comando truffle migrate
        result = subprocess.run(
            ["truffle", "migrate", "--reset"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di truffle migrate: {e}")
        print(e.stderr)

if __name__ == "__main__":
    # Verifica la connessione
    if w3.is_connected():
        print(f"Connesso a {PROVIDER_URL}")
        
        # Scegli un metodo di deployment
        method = input("Seleziona il metodo di deployment (1: Python, 2: Truffle): ")
        
        if method == "1":
            deploy_all_contracts()
        elif method == "2":
            deploy_with_truffle()
        else:
            print("Scelta non valida")
    else:
        print(f"Impossibile connettersi a {PROVIDER_URL}")