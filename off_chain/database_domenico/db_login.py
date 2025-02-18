import os
import re
import sqlite3


class PasswordTooShortError(Exception):
    """Eccezione per password con meno di 8 caratteri"""
    pass


class PasswordWeakError(Exception):
    """Eccezione per password che non soddisfa i criteri di sicurezza"""
    pass


class DatabaseError(Exception):
    pass


class UniqueConstraintError(DatabaseError):
    pass


class DatabaseLogin:
    def __init__(self):
        # Percorso assoluto nella cartella di progetto
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Risale di una cartella
        DB_PATH = os.path.join(BASE_DIR, 'database.db')

        # Connessione senza creare un nuovo file se non esiste
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database non trovato: {DB_PATH}")

        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

    def fetch_query(self, query, params=()):
        """Esegue una SELECT e restituisce i risultati"""
        try:
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Errore SQLite durante la SELECT: {e}")

    def execute_query(self, query, params=()):
        """Esegue una query di scrittura (INSERT, UPDATE, DELETE)"""
        try:
            self.cur.execute(query, params)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise UniqueConstraintError("Username già esistente") from e
        except sqlite3.Error as e:
            print("Errore SQLite:", e)
            raise DatabaseError("Errore nel database") from e

    def get_lista_credenziali(self):
        query = """
        SELECT * FROM Credenziali
        """
        return self.fetch_query(query)

    def get_azienda_by_id(self, id_):
        query = """
        SELECT * FROM Azienda WHERE Id_azienda = ?
        """
        return self.fetch_query(query, (id_,))

    def inserisci_credenziali_e_azienda(self, username, password, tipo, indirizzo, secret_key):
        try:
            # Controllo lunghezza password
            if len(password) < 8:
                raise PasswordTooShortError("La password deve contenere almeno 8 caratteri!")

            # Controllo complessità con regex
            if not re.search(r'[A-Z]', password):  # Almeno una lettera maiuscola
                raise PasswordWeakError("La password deve contenere almeno una lettera maiuscola.")
            if not re.search(r'[a-z]', password):  # Almeno una lettera minuscola
                raise PasswordWeakError("La password deve contenere almeno una lettera minuscola.")
            if not re.search(r'[0-9]', password):  # Almeno un numero
                raise PasswordWeakError("La password deve contenere almeno un numero.")
            if not re.search(r'\W', password):  # Almeno un carattere speciale
                raise PasswordWeakError("La password deve contenere almeno un carattere speciale (!, @, #, etc.).")

            # Avvia la transazione
            self.cur.execute("BEGIN TRANSACTION;")

            # Inserimento delle credenziali
            query_credenziali = """
            INSERT INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?);
            """
            try:
                self.cur.execute(query_credenziali, (username, password, secret_key))
            except sqlite3.IntegrityError:
                raise UniqueConstraintError("Errore: Username già esistente.")

            # Recupero dell'ID delle credenziali appena inserite
            id_credenziali = self.cur.lastrowid

            # Inserimento dell'azienda con l'ID delle credenziali
            query_azienda = """
            INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
            VALUES (?, ?, ?, ?);
            """
            self.cur.execute(query_azienda, (id_credenziali, tipo, username, indirizzo, ))

            # Commit della transazione
            self.conn.commit()

            return id_credenziali  # Può essere utile restituire l'ID

        except Exception as e:
            self.conn.rollback()  # Annulla le operazioni se c'è un errore
            raise e
