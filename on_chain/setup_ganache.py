#!/usr/bin/env python3
"""
Script per automatizzare l'avvio di Ganache, il deployment dei contratti e l'aggiornamento degli indirizzi.
"""
import os
import sys
import json
import time
import signal
import subprocess
import re
from pathlib import Path

# Configurazione
GANACHE_PORT = 7545
GANACHE_MNEMONIC = "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
CONTRACT_ADDRESSES_FILE = "contract-addresses.json"
CONTRACT_LIST = [
    "CO2Token", 
    "UserRegistry", 
    "ProductRegistry", 
    "OperationRegistry", 
    "SustainabilityMetrics", 
    "QualityControl", 
    "ProductRequest", 
    "SupplyChain"
]

def is_ganache_running(port=GANACHE_PORT):
    """Verifica se Ganache è già in esecuzione sulla porta specificata"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def start_ganache():
    """Avvia Ganache con una configurazione fissa"""
    print("Avvio di Ganache in corso...")
    
    # Opzioni di Ganache
    ganache_cmd = [
        "npx", "ganache-cli",
        "--port", str(GANACHE_PORT),
        "--mnemonic", GANACHE_MNEMONIC,
        "--accounts", "10",
        "--gasLimit", "8000000",
        "--defaultBalanceEther", "1000"
    ]
    
    # Avvia Ganache come processo separato
    process = subprocess.Popen(
        ganache_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Attendi che Ganache sia pronto
    for _ in range(30):  # timeout di 30 secondi
        if is_ganache_running(GANACHE_PORT):
            print(f"Ganache avviato con successo sulla porta {GANACHE_PORT}")
            return process
        time.sleep(1)
    
    print("Errore: Impossibile avviare Ganache")
    process.terminate()
    sys.exit(1)

def deploy_contracts():
    """Deploya i contratti usando Truffle"""
    print("Deployment dei contratti in corso...")
    
    # Configura l'ambiente per il deployment su Ganache
    os.environ["DEPLOY_NETWORK"] = "ganache"
    
    # Esegui truffle migrate
    result = subprocess.run(
        ["npx", "truffle", "migrate", "--reset", "--network", "ganache"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Errore durante il deployment dei contratti:")
        print(result.stderr)
        return None
    
    print("Deployment dei contratti completato con successo")
    return result.stdout

def extract_contract_addresses(output):
    """Estrae gli indirizzi dei contratti dall'output di Truffle"""
    print("Estrazione degli indirizzi dei contratti...")
    addresses = {}
    
    # Pattern per estrarre gli indirizzi (supporta diversi formati di output)
    patterns = [
        r"contract address:\s+([0-9a-fA-F]{40}|0x[0-9a-fA-F]{40})",  # Formato standard
        r"Deploying '(\w+)'[\s\S]+?contract address:\s+([0-9a-fA-F]{40}|0x[0-9a-fA-F]{40})"  # Formato con nome
    ]
    
    # Se non riusciamo a estrarre dall'output, prova a leggere i file build
    if not extract_from_output(output, addresses, patterns):
        extract_from_build_files(addresses)
    
    return addresses

def extract_from_output(output, addresses, patterns):
    """Estrae gli indirizzi dall'output usando regex"""
    if not output:
        return False
    
    # Cerca coppie nome-indirizzo
    for contract in CONTRACT_LIST:
        for line in output.split("\n"):
            if f"Deploying '{contract}'" in line or f"Replacing '{contract}'" in line:
                # Cerca l'indirizzo nelle righe successive
                match = re.search(r"contract address:\s+(0x[0-9a-fA-F]{40})", output[output.index(line):output.index(line) + 500])
                if match:
                    addresses[contract] = match.group(1)
    
    # Fallback: cerca tutti gli indirizzi se i contratti specifici non sono stati trovati
    if not addresses and patterns[0]:
        matches = re.findall(patterns[0], output)
        if len(matches) >= len(CONTRACT_LIST):
            for i, contract in enumerate(CONTRACT_LIST):
                if i < len(matches):
                    # Assicurati che l'indirizzo abbia il prefisso 0x
                    addr = matches[i]
                    addresses[contract] = f"0x{addr}" if not addr.startswith("0x") else addr
    
    return bool(addresses)

def extract_from_build_files(addresses):
    """Estrae gli indirizzi dai file JSON nella directory build/contracts"""
    build_dir = Path("build/contracts")
    if not build_dir.exists():
        print("Directory build/contracts non trovata")
        return False
    
    for contract in CONTRACT_LIST:
        json_file = build_dir / f"{contract}.json"
        if json_file.exists():
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    network_data = data.get("networks", {})
                    # Trova l'ultima rete deployata (di solito la chiave più alta)
                    if network_data:
                        latest_network = max(network_data.keys(), key=int)
                        address = network_data[latest_network].get("address")
                        if address:
                            addresses[contract] = address
            except Exception as e:
                print(f"Errore durante la lettura di {json_file}: {e}")
    
    return bool(addresses)

def update_addresses_file(addresses):
    """Aggiorna il file degli indirizzi dei contratti"""
    print("Aggiornamento del file degli indirizzi...")
    
    # Leggi il file esistente se presente
    existing_addresses = {}
    if os.path.exists(CONTRACT_ADDRESSES_FILE):
        with open(CONTRACT_ADDRESSES_FILE, "r") as f:
            try:
                existing_addresses = json.load(f)
            except json.JSONDecodeError:
                pass
    
    # Aggiorna con i nuovi indirizzi
    existing_addresses.update(addresses)
    
    # Salva il file aggiornato
    with open(CONTRACT_ADDRESSES_FILE, "w") as f:
        json.dump(existing_addresses, f, indent=2)
    
    print(f"File {CONTRACT_ADDRESSES_FILE} aggiornato con successo")

def main():
    """Funzione principale"""
    # Cambia la directory di lavoro nella cartella on_chain
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    ganache_process = None
    try:
        # Verifica se Ganache è già in esecuzione
        if is_ganache_running(GANACHE_PORT):
            print(f"Ganache è già in esecuzione sulla porta {GANACHE_PORT}")
        else:
            ganache_process = start_ganache()
        
        # Attendi un momento per assicurarci che Ganache sia pronto
        time.sleep(2)
        
        # Deploya i contratti
        output = deploy_contracts()
        
        # Estrai gli indirizzi dei contratti
        addresses = extract_contract_addresses(output)
        
        if addresses:
            # Aggiorna il file degli indirizzi
            update_addresses_file(addresses)
            print("\nSetup completato! Gli indirizzi dei contratti sono stati aggiornati.")
            
            # Stampa gli indirizzi
            print("\nIndirizzi dei contratti:")
            for contract, address in addresses.items():
                print(f"{contract}: {address}")
        else:
            print("Errore: Impossibile estrarre gli indirizzi dei contratti")
    
    except KeyboardInterrupt:
        print("\nInterruzione ricevuta, pulizia in corso...")
    
    finally:
        # Se abbiamo avviato Ganache, chiediamo se tenerlo in esecuzione
        if ganache_process:
            keep_running = input("\nMantenere Ganache in esecuzione? (s/n): ").lower() == 's'
            if not keep_running:
                print("Terminazione di Ganache...")
                ganache_process.terminate()
                ganache_process.wait()
                print("Ganache terminato.")
            else:
                print(f"Ganache rimane in esecuzione sulla porta {GANACHE_PORT}")
                print("IMPORTANTE: Per terminare manualmente Ganache in seguito, usa CTRL+C nel suo terminale.")

if __name__ == "__main__":
    main() 