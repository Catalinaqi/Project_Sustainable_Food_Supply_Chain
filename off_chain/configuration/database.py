import sqlite3
from configuration.db_load_setting import DATABASE_PATH
from configuration.log_load_setting import logger
import os

class Database:
    _instance = None  # Singleton per la connessione al database

    def __new__(cls):
        """Implementa il pattern Singleton per mantenere una singola connessione al database."""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            try:
                conn = sqlite3.connect(DATABASE_PATH)  # Connessione al database
                cls._instance.conn = conn  # Memorizza la connessione nell'istanza
                cls._instance.cur = conn.cursor()  # Cursore
                logger.info(f"BackEnd: get_connection: Name database is: {os.path.basename(DATABASE_PATH)}")
                logger.info(f"BackEnd: get_connection: Path for the database is: {DATABASE_PATH}")
            except sqlite3.ProgrammingError as e:
                logger.error(f"Cannot operate on a closed database: {e}")
                raise Exception(f"Cannot operate on a closed database: {e}")
            except sqlite3.DatabaseError as e:
                logger.error(f"File is encrypted or is not a database: {e}")
                raise Exception(f"File is encrypted or is not a database: {e}")
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                raise Exception(f"Unexpected Error: {e}")

        return cls._instance

    def execute_query(self, query, params=()):
        """Esegue una query di modifica (INSERT, UPDATE, DELETE) con gestione errori."""
        if not hasattr(self, "conn") or self.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            print(f"Provo ad eseguire {query} con par {params}")
            self.cur.execute(query, params)
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("Errore: Violazione di vincolo di unicità.")
        except sqlite3.OperationalError as e:
            print(f"Errore SQL: {e}")
        except sqlite3.Error as e:
            print(f"Errore generico nel database: {e}")

    def fetch_results(cls, query, params=()):
        """Esegue una query di selezione e restituisce i risultati."""
        if not hasattr(cls, "conn") or cls.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            cls._instance.cur.execute(query, params)
            return cls._instance.cur.fetchall()
        except sqlite3.Error as e:
            print(f"Errore nella query: {e}")
            return None
        
    def fetch_one(self, query, params=()):
        if not hasattr(self, "conn") or self.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            self.cur.execute(query, params)
            result = self.cur.fetchone()
            return result[0] if result else None  # Restituisce il valore o None se non ci sono risultati
        except sqlite3.Error as e:
            print(f"Errore nella query: {e}")
            return None


    def execute_transaction(self, queries):
        """
        Esegue più query SQL all'interno di una singola transazione.

        Parameters:
        - queries: Lista di tuple contenenti (query, params).
        """
        if not hasattr(self, "conn") or self.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")

        try:
            self.cur.execute("BEGIN TRANSACTION;")

            for query, params in queries:
                logger.info(f"BackEnd: execute_transaction: Info executing query: {query} with params: {params}")
                self.cur.execute(query, params)

            self.conn.commit()  # Commit di tutte le modifiche
        except Exception as e:
            self.conn.rollback()  # Rollback in caso di errore
            raise Exception(f"Transaction error: {e}")

    def close_connection(self):
        """Chiude la connessione al database in modo sicuro."""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
            Database._instance = None  # Resetta il Singleton
            logger.info("BackEnd: Closing database .....")

    def __del__(self):
        """Chiusura sicura della connessione quando l'istanza viene distrutta."""
        self.close_connection()
