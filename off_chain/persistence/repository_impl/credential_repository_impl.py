from abc import ABC
import sqlite3
from typing import Union
from domain.exception.database_exceptions import UniqueConstraintError
from configuration.database import Database
from configuration.log_load_setting import logger
from persistence.query_builder import QueryBuilder
from model.credential_model import UserModel
from model.company_model import CompanyModel
from persistence.repository_impl.database_standard import aziende_enum

"""
class "CredentialRepositoryImpl(CredentialRepository, ABC)"
    Defines the "CredentialRepositoryImpl" class, which inherits from CredentialRepository 
    and ABC (Abstract Base Class).
    ABC indicates that the class can contain abstract methods and is part of a design pattern
    "Repository" based on abstract classes.
"""


class CredentialRepositoryImpl(ABC):
  
    def __init__(self):
        self.db = Database()
        self.query_builder = QueryBuilder()
        logger.info("BackEnd: Successfully initializing the instance for CredentialRepositoryImpl.")

    def get_user(self, user: str) -> Union[UserModel, None]:
        try:
            query,value = ( 
                self.query_builder.select("*").table("credenziali").where("Username", "=",user).get_query())
            return UserModel(*self.db.fetch_results(query,value)[0])
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali nel rep: {str(e)}")
            return None


    def get_lista_credenziali(self) -> list[UserModel]:
        try:

            query,value = ( 
                self.query_builder.select("*").table("credenziali").get_query())


            result = [UserModel(*x) for x in self.db.fetch_results(query,value) ]
            
            
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali nel rep: {str(e)}")
            return []
        
    
        if not result:
            logger.warning("The credenziali table is empty or the query returned no results.")
        else:
            logger.info(f"Credenziali obtained ")

        return result

    def get_azienda_by_id(self, id: int) -> CompanyModel:
        query, value = (
            self.query_builder.select("*").table("Azienda").where("Id_azienda","=",id).get_query()
        )

        try:
            result = self.db.fetch_results(query, value)
            return CompanyModel(*self.db.fetch_results(query, value)[0])
            
        except Exception as e:
            logger.info(f" Errore nel repository{e} ")
            return False


    def inserisci_credenziali_e_azienda(self, username: str , password : str, tipo: aziende_enum, indirizzo : str, secret_key):
        try:

            UserModel.validate_password(password)

            # Avvia la transazione
            #self.db.cur.execute("BEGIN TRANSACTION;")

            # Inserimento delle credenziali
            query_credenziali = """
                    INSERT INTO Credenziali (Username, Password, topt_secret)
                    VALUES (?, ?, ?);
                    """
            try:
                self.db.execute_query(query_credenziali, (username, password, secret_key))
            except sqlite3.IntegrityError:
                raise UniqueConstraintError("Errore: Username già esistente.")
            
            try:
                id_credenziali : int = self.db.cur.lastrowid
            except Exception as e:
                logger.error(f"Errore nel'ottenimento dell'id delle credenziali inserite")
                raise Exception("Errore nel recupero dell'ID delle credenziali.")


            # Inserimento dell'azienda con l'ID delle credenziali
            query_azienda = """
                    INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
                    VALUES (?, ?, ?, ?);
                    """
            self.db.execute_query(query_azienda, (id_credenziali, tipo, username, indirizzo,))

            # Commit della transazione
            #self.conn.commit()

            return id_credenziali  # Può essere utile restituire l'ID

        except Exception as e:
            logger.error(f"Errore durante l'inserimento delle credenziali e dell'azienda: {str(e)}")
            # self.conn.rollback()  # Annulla le operazioni se c'è un errore
            raise e
