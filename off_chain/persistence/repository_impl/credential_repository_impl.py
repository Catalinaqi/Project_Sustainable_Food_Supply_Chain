from abc import ABC
import re
import sqlite3
from off_chain.domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError
from off_chain.domain.exception.database_exceptions import UniqueConstraintError
from off_chain.domain.repository.credential_repository import CredentialRepository
from off_chain.configuration.db_manager_setting import DatabaseManagerSetting
from off_chain.configuration.log_load_setting import logger

"""
class "CredentialRepositoryImpl(CredentialRepository, ABC)"
    Defines the "CredentialRepositoryImpl" class, which inherits from CredentialRepository 
    and ABC (Abstract Base Class).
    ABC indicates that the class can contain abstract methods and is part of a design pattern
    "Repository" based on abstract classes.
"""


class CredentialRepositoryImpl(CredentialRepository, ABC):
    """
    Is a class variable "_instance2, which is initially None.
    This variable is used to store the only instance of the class "CredentialRepositoryImpl"
    (Singleton pattern)
    """

    # Class variable that stores the single instance
    _instance = None

    """""
    The __new__ method is a special method of Python classes that runs before __init__ and is responsible for creating 
    a new instance of the class. Normally, __new__ is only used to control instantiation, using the Singleton pattern.
    ----------------------------------------------------------------------------------------------
    __new__:    It is a class method, so it receives 'cls' instead of 'self'.
    cls:        Represents the class itself (CredentialRepositoryImpl in this case), not an instance.
    _instance:  Is a class variable that stores the single instance of CredentialRepositoryImpl.
                The first time the class is created, _instance is None, so the code inside the if is.
    super(CredentialRepositoryImpl, cls).__new__(cls): 
                Calls __new__ of the superclass (ABC or any other base class).
                This creates a new instance of the class and stores it in _instance.
                If the class already has an instance (_instance is not None), this line is not executed, 
                ensuring that there is only a single instance.
    DatabaseManagerSetting():
                Only executed the first time the instance is created.
                Initializes a 'db_manager_setting' attribute with an instance of 'DatabaseManagerSetting()'.
                If a new instance is attempted to be created in the future, this line will not be executed again. 
    logger.info:
                This message will only appear the first time the instance is created.                
    
    """""
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CredentialRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for CredentialRepositoryImpl.")
        return cls._instance

    def get_lista_credenziali(self) -> list:
        query = "SELECT * FROM credenziali"
        result = self.db_manager_setting.fetch_query(query)
        if not result:
            logger.warning("The credenziali table is empty or the query returned no results.")
        else:
            logger.info(f"Credenziali obtained in get_lista_credenziali: {result}")

        return result

    def get_azienda_by_id(self, id_: int) -> list:
        query = """
            SELECT * FROM Azienda WHERE Id_azienda = ?
            """
        return self.db_manager_setting.fetch_query(query, (id_,))

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
            # self.db_manager_setting.cur.execute("BEGIN TRANSACTION;")

            # Inserimento delle credenziali
            query_credenziali = """
                    INSERT INTO Credenziali (Username, Password, totp_secret)
                    VALUES (?, ?, ?);
                    """
            try:
                self.db_manager_setting.execute_query(query_credenziali, (username, password, secret_key))
            except sqlite3.IntegrityError:
                raise UniqueConstraintError("Errore: Username già esistente.")

            # Recupero dell'ID delle credenziali appena inserite
            id_credenziali = self.db_manager_setting.fetch_one("SELECT last_insert_rowid();")[0]
            if id_credenziali is None:
                raise Exception("Errore nel recupero dell'ID delle credenziali.")

            # Inserimento dell'azienda con l'ID delle credenziali
            query_azienda = """
                    INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
                    VALUES (?, ?, ?, ?);
                    """
            self.db_manager_setting.execute_query(query_azienda, (id_credenziali, tipo, username, indirizzo,))

            # Commit della transazione
            # self.conn.commit()

            return id_credenziali  # Può essere utile restituire l'ID

        except Exception as e:
            logger.error(f"Errore durante l'inserimento delle credenziali e dell'azienda: {str(e)}")
            # self.conn.rollback()  # Annulla le operazioni se c'è un errore
            raise e
