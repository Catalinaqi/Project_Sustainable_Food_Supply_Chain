from abc import ABC
import sqlite3
from typing import Union, List, Optional
from domain.exception.database_exceptions import UniqueConstraintError
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.exception.login_exceptions import HaveToWaitException, ToManyTryLogException
from persistence.query_builder import QueryBuilder
from model.credential_model import UserModel
from model.company_model import CompanyModel
from persistence.repository_impl.database_standard import aziende_enum
from session import Session


class CredentialRepositoryImpl(ABC):
    """
    Repository implementation for user credentials and company data management.
    """

    def __init__(self) -> None:
        self.db = Database()
        self.query_builder = QueryBuilder()
        logger.info("BackEnd: Successfully initialized CredentialRepositoryImpl instance.")

    def get_user(self, username: str) -> Optional[UserModel]:
        """
        Retrieve a user model by username.
        """
        try:
            query, values = (
                self.query_builder.select("*")
                .table("Credenziali")
                .where("Username", "=", username)
                .get_query()
            )
            results = self.db.fetch_results(query, values)
            if not results:
                logger.info(f"User '{username}' not found.")
                return None
            user = UserModel(*results[0])
            logger.info(f"Retrieved user: {username}")
            return user
        except Exception as error:
            logger.warning(f"Error retrieving credentials: {error}")
            return None

    def get_lista_credenziali(self) -> List[UserModel]:
        """
        Retrieve a list of all user credentials.
        """
        try:
            query, values = self.query_builder.select("*").table("Credenziali").get_query()
            results = self.db.fetch_results(query, values)
            if not results:
                logger.warning("The 'Credenziali' table is empty or returned no results.")
                return []
            users = [UserModel(*row) for row in results]
            logger.info(f"Retrieved {len(users)} credentials.")
            return users
        except Exception as error:
            logger.warning(f"Error retrieving credentials list: {error}")
            return []

    def get_azienda_by_id(self, azienda_id: int) -> Optional[CompanyModel]:
        """
        Retrieve a company model by company ID.
        """
        try:
            query, values = (
                self.query_builder.select("*")
                .table("Azienda")
                .where("Id_azienda", "=", azienda_id)
                .get_query()
            )
            results = self.db.fetch_results(query, values)
            if not results:
                logger.info(f"Company with ID {azienda_id} not found.")
                return None
            company = CompanyModel(*results[0])
            return company
        except Exception as error:
            logger.error(f"Error retrieving company by ID: {error}")
            return None

    def register(
        self,
        username: str,
        password: str,
        tipo: aziende_enum,
        indirizzo: str,
    ) -> int:
        """
        Register a new user and associated company atomically.
        Returns the new credential ID.
        Raises UniqueConstraintError if username already exists.
        """
        try:
            UserModel.validate_password(password)
            hashed_password = UserModel.hash_password(password)
            self.db.cur.execute("BEGIN TRANSACTION;")
            query_credenziali = (
                "INSERT INTO Credenziali (Username, Password) VALUES (?, ?);"
            )
            self.db.cur.execute(query_credenziali, (username, hashed_password))
            logger.info(f"Inserting credentials for new user '{username}'.")
            id_credenziali = self.db.cur.lastrowid
            query_azienda = (
                "INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo) "
                "VALUES (?, ?, ?, ?);"
            )
            self.db.cur.execute(query_azienda, (id_credenziali, tipo, username, indirizzo))
            logger.info(f"Inserting company info linked to user '{username}'.")
            self.db.conn.commit()
            return id_credenziali
        except sqlite3.IntegrityError:
            self.db.conn.rollback()
            logger.error("Registration error: Username already exists.")
            raise UniqueConstraintError("Username already exists.")
        except Exception as error:
            self.db.conn.rollback()
            logger.error(f"Registration error: {error}")
            raise

    def verifica_password(self, old_password: str, user_id: str) -> bool:
        """
        Verify if the provided old password matches the stored one for user_id.
        """
        try:
            if Session().current_user["id_azienda"] != user_id:
                raise PermissionError("User ID does not match session user.")

            query = "SELECT Password FROM Credenziali WHERE Id_credenziali = ?"
            db_password = self.db.fetch_one(query, (user_id,))
            if db_password is None:
                logger.warning(f"No password found for user ID {user_id}.")
                return False

            hashed_old = UserModel.hash_password(old_password)
            return hashed_old == db_password
        except Exception as error:
            logger.error(f"Error verifying password: {error}")
            raise Exception("Error verifying password") from error

    def cambia_password(self, new_password: str, user_id: str) -> None:
        """
        Change the password for the specified user_id after validation.
        """
        try:
            UserModel.validate_password(new_password)
            hashed_password = UserModel.hash_password(new_password)

            if Session().current_user["id_azienda"] != user_id:
                raise PermissionError("User ID does not match session user.")

            query = "UPDATE Credenziali SET Password = ? WHERE Id_credenziali = ?"
            self.db.execute_query(query, (hashed_password, user_id))
            logger.info(f"Password updated for user ID {user_id}.")
        except (HaveToWaitException, ToManyTryLogException):
            raise
        except Exception as error:
            logger.error(f"Error changing password: {error}")
            raise Exception(f"Error changing password: {error}") from error
