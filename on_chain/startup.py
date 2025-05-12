#!/usr/bin/env python3
"""
Script di avvio principale per l'applicazione.
Questo script:
1. Verifica che Ganache sia in esecuzione
2. Controlla se i contratti sono deployati
3. Aggiorna gli indirizzi se necessario
4. Può essere utilizzato come entry point per l'applicazione
"""
import os
import sys
import json
import time
import socket
import subprocess
from pathlib import Path

# Configurazione
GANACHE_PORT = 7545
CONTRACT_ADDRESSES_FILE = "contract-addresses.json"

# Aggiungo messaggi iniziali per debug
print("===== STARTUP BLOCKCHAIN INIZIATO =====")
print(f"Directory corrente: {os.getcwd()}")

def is_ganache_running(port=GANACHE_PORT):
    """Verifica se Ganache è già in esecuzione sulla porta specificata"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def start_ganache_cli():
    """Avvia Ganache CLI con una configurazione predefinita"""
    print("Avvio di Ganache CLI in corso...")
    
    try:
        # Opzioni di Ganache
        ganache_cmd = [
            "ganache-cli",
            "--port", str(GANACHE_PORT),
            "--accounts", "10",
            "--gasLimit", "8000000",
            "--defaultBalanceEther", "1000"
        ]
        
        # Avvia Ganache come processo separato
        process = subprocess.Popen(
            ganache_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendi che Ganache sia pronto
        for _ in range(30):  # timeout di 30 secondi
            if is_ganache_running(GANACHE_PORT):
                print(f"Ganache CLI avviato con successo sulla porta {GANACHE_PORT}")
                return process
            time.sleep(1)
        
        # Se arriviamo qui, Ganache non è riuscito ad avviarsi
        stdout, stderr = process.communicate(timeout=1)
        print(f"Errore nell'avvio di Ganache: {stderr}")
        process.terminate()
        return None
    
    except Exception as e:
        print(f"Errore durante l'avvio di Ganache CLI: {e}")
        return None

def check_contract_addresses():
    """Verifica se il file degli indirizzi dei contratti esiste e contiene indirizzi validi"""
    if not os.path.exists(CONTRACT_ADDRESSES_FILE):
        print(f"File {CONTRACT_ADDRESSES_FILE} non trovato")
        return False
    
    try:
        with open(CONTRACT_ADDRESSES_FILE, 'r') as f:
            addresses = json.load(f)
            
        # Verifica che ci siano indirizzi validi
        for contract, address in addresses.items():
            if not address or not address.startswith('0x'):
                print(f"Indirizzo mancante o non valido per {contract}")
                return False
                
        return True
    except (json.JSONDecodeError, IOError) as e:
        print(f"Errore nella lettura del file {CONTRACT_ADDRESSES_FILE}: {e}")
        return False

def deploy_contracts_with_truffle():
    """Deploya i contratti usando Truffle"""
    print("Deployment dei contratti con Truffle in corso...")
    
    try:
        # Esegui truffle migrate
        result = subprocess.run(
            ["truffle", "migrate", "--reset", "--network", "development"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Errore nel deployment dei contratti: {result.stderr}")
            return False
            
        print("Deployment dei contratti completato con successo")
        return True
    except Exception as e:
        print(f"Errore nell'esecuzione di truffle migrate: {e}")
        return False

def main():
    """Funzione principale"""
    try:
        # Verifica se Ganache è in esecuzione
        if is_ganache_running(GANACHE_PORT):
            print(f"Ganache è già in esecuzione sulla porta {GANACHE_PORT}")
            ganache_process = None
        else:
            print("Ganache non è in esecuzione. Avvio in corso...")
            ganache_process = start_ganache_cli()
            if not ganache_process:
                print("Impossibile avviare Ganache. Uscita.")
                return 1
        
        # Verifica se i contratti sono già deployati
        if check_contract_addresses():
            print("Gli indirizzi dei contratti sono già presenti e validi.")
        else:
            print("Gli indirizzi dei contratti non sono presenti o non sono validi.")
            print("Esecuzione del deployment...")
            if not deploy_contracts_with_truffle():
                print("Errore nel deployment dei contratti. Uscita.")
                if ganache_process:
                    ganache_process.terminate()
                return 1
        
        print("\nAmbiente di sviluppo blockchain pronto!")
        print("La tua applicazione può ora utilizzare i contratti agli indirizzi specificati nel file contract-addresses.json")
        
        # Se abbiamo avviato Ganache, teniamolo in esecuzione
        if ganache_process:
            print("\nMantenimento di Ganache in esecuzione. Premi CTRL+C per terminare.")
            try:
                # Loop infinito per mantenere lo script in esecuzione
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nInterruzione ricevuta, terminazione in corso...")
            finally:
                print("Terminazione di Ganache...")
                ganache_process.terminate()
                try:
                    ganache_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ganache_process.kill()
                print("Ganache terminato.")
        
        return 0
    
    except Exception as e:
        print(f"Errore imprevisto: {e}")
        return 1

if __name__ == "__main__":
    print("Avvio startup.py...")
    sys.exit(main())
    print("Completato startup.py.") 