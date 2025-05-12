import sys
import time
import subprocess
import atexit
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox

from configuration.log_load_setting import logger
from database.db_migrations import DatabaseMigrations
from configuration.database import Database
from session import Session
from presentation.view.vista_accedi import VistaAccedi




import sys
from PyQt5.QtWidgets import QApplication
from persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl


def setup_database():

    try:
        DatabaseMigrations.run_migrations()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)  # Stops the application if there is a critical error


def check_ganache_running(port=7545):
    """Verifica se Ganache è in esecuzione sulla porta specificata"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


def start_blockchain(show_warnings=True):
    """
    Avvia l'ambiente blockchain in modo non bloccante
    
    Args:
        show_warnings: Se mostrare finestre di dialogo con avvisi in caso di errori
        
    Returns:
        subprocess.Popen o None: Il processo blockchain se avviato, None altrimenti
    """
    # Verifica se Ganache è già in esecuzione
    if check_ganache_running():
        logger.info("Ganache già in esecuzione sulla porta 7545")
        
        # Verifica se i contratti sono già stati deployati
        if os.path.exists("on_chain/contract-addresses.json"):
            logger.info("Ambiente blockchain già configurato")
            return None  # Non è necessario avviare nulla
    
    # Altrimenti tenta di avviare l'ambiente
    try:
        logger.info("Avvio dell'ambiente blockchain...")
        
        # Tenta di trovare il percorso assoluto di startup.py
        on_chain_dir = os.path.join(os.getcwd(), "on_chain")
        startup_path = os.path.join(on_chain_dir, "startup.py")
        
        if not os.path.exists(startup_path):
            error_msg = f"File startup.py non trovato in {on_chain_dir}"
            logger.error(error_msg)
            if show_warnings:
                QMessageBox.warning(None, "Blockchain Error", 
                                    f"Impossibile trovare lo script di avvio blockchain.\n"
                                    f"L'applicazione continuerà senza funzionalità blockchain.")
            return None
        
        # Avvia lo script in un processo separato
        process = subprocess.Popen(
            [sys.executable, startup_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Verifica avvio immediato
        time.sleep(1)
        if process.poll() is not None:
            # Il processo è terminato subito, c'è stato un errore
            stdout, stderr = process.communicate()
            error_msg = f"Errore avvio blockchain: {stderr}"
            logger.error(error_msg)
            
            if show_warnings:
                QMessageBox.warning(None, "Blockchain Warning", 
                                   "Impossibile avviare l'ambiente blockchain.\n"
                                   "L'applicazione continuerà, ma alcune funzionalità potrebbero non essere disponibili.\n\n"
                                   "Suggerimento: avvia manualmente Ganache e ripeti.")
            return None
        
        logger.info("Processo blockchain avviato con successo")
        return process
        
    except Exception as e:
        logger.error(f"Errore durante l'avvio dell'ambiente blockchain: {e}")
        
        if show_warnings:
            QMessageBox.warning(None, "Blockchain Error", 
                               "Errore nell'avvio dell'ambiente blockchain.\n"
                               "L'applicazione continuerà, ma alcune funzionalità potrebbero non essere disponibili.")
        return None


def cleanup_blockchain(process):
    """Termina il processo blockchain"""
    if process and process.poll() is None:  # Verifica che il processo sia ancora in esecuzione
        logger.info("Terminazione dell'ambiente blockchain...")
        process.terminate()
        try:
            process.wait(timeout=5)  # Attendi 5 secondi per la terminazione
            logger.info("Ambiente blockchain terminato")
        except subprocess.TimeoutExpired:
            logger.warning("Timeout nella terminazione del processo blockchain, forzando la chiusura")
            process.kill()


if __name__ == "__main__":
    # Configure the database before starting the graphical interface
    setup_database()
    
    # Starting the PyQt application
    app = QApplication(sys.argv)
    logger.info("Frontend: Starting the PyQt application...")

    session = Session()
    logger.info(f"Start session on {session.start_app}")

    # Show Splash Screen
    splash = QSplashScreen(QPixmap("presentation/resources/logo_splash.png"), Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()  # Processa gli eventi per mostrare lo splash screen

    # Mostra messaggio sullo splash
    splash.showMessage("Inizializzazione ambiente blockchain...", 
                     Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    app.processEvents()
    
    # All'avvio dell'applicazione, inizia il processo blockchain
    blockchain_process = start_blockchain(show_warnings=False)  # No popup durante il caricamento
    
    # Registra la funzione di pulizia da eseguire all'uscita
    if blockchain_process:
        atexit.register(cleanup_blockchain, blockchain_process)
        logger.info("Processo blockchain registrato per terminazione automatica")
    
    time.sleep(1)  # Breve pausa per dare tempo al processo blockchain di inizializzare

    # Inizializza il database
    db = Database()
    query = "SELECT * FROM Credenziali"
    logger.debug(f"DB credentials: {db.fetch_results(query)}")
    
    # Avvia la finestra principale
    finestra = VistaAccedi()
    finestra.show()
    splash.finish(finestra)
    
    # Mostra avviso se blockchain non disponibile
    if not blockchain_process and not check_ganache_running():
        QMessageBox.information(finestra, "Blockchain Info", 
                             "Ambiente blockchain non disponibile.\n"
                             "Alcune funzionalità potrebbero non essere disponibili.\n\n"
                             "Per utilizzare tutte le funzionalità, avvia Ganache manualmente.")

    # Avvia il ciclo degli eventi Qt
    sys.exit(app.exec())
