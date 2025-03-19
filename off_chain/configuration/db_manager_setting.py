import sqlite3

from configuration.db_connection_setting import DatabaseConnectionSetting
from configuration.log_load_setting import logger


class DatabaseManagerSetting:
    """
    Handles direct interactions with the database.
    """

    """
    __init__(self): Class "DatabaseManagerSetting" constructor, executed automatically when 
                    new instance of the class "DatabaseManagerSetting" is created.
    self:           Represents the actuality instance of class "DatabaseManagerSetting"
    """

    def __init__(self):
        self.conn = DatabaseConnectionSetting.get_connection()
        logger.info("BackEnd: DatabaseManagerSetting: DatabaseManagerSetting constructor.")
        self.cursor = self.conn.cursor()

    def fetch_one(self, query, params=()):
        """
        Executes a SELECT query and returns a single result.
        """
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            result_tuple = tuple(result) if result else None  # Convertir Row a tupla
            logger.info(
                f"BackEnd: fetch_one: Info executing query: {query} with params: {params} | Results: {len(result_tuple)}")
            # conn.close()
            return result_tuple
        except Exception as e:
            raise Exception(f"Error executing SELECT query: {e}")

    def fetch_query(self, query, params=()):
        """
        Executes a SELECT query and returns multiple results.
        """
        try:
            results = self.cursor.execute(query, params)
            results_precise = [tuple(row) for row in results.fetchall()]
            logger.info(
                f"BackEnd: fetch_query: Info executing query: {query} with params: {params} | Results: {len(results_precise)}")
            # conn.close()
            return results_precise if results_precise else []
        except Exception as e:
            logger.error(f"Error executing SELECT query: {e}", exc_info=True, stack_info=True,
                         stacklevel=2, extra={'query': query, 'params': params})
            raise Exception(f"Error executing SELECT query: {e}")

    def execute_query(self, query, params=(), multiple=False):
        """
        Executes an INSERT, UPDATE, or DELETE query.
        Uses transactions to ensure atomicity.

        Parameters:
        - query: SQL query to execute.
        - params: Tuple or list of tuples (if multiple=True) for parameterized queries.
        - multiple: If True, executes multiple queries using executemany().
        """

        try:
            # conn = DatabaseConnectionSetting.get_connection()
            # cursor = conn.cursor()
            # Begin transaction
            self.cursor.execute("BEGIN TRANSACTION;")

            if multiple:
                logger.info(f"BackEnd: execute_query: Info executing query: {query} with params: {params}")
                self.cursor.executemany(query, params)  # Execute multiple queries
            else:
                logger.info(f"Info executing query(execute_query): {query} with params: {params}")
                self.cursor.execute(query, params)  # Execute single query

            self.conn.commit()  # Commit changes

        except sqlite3.IntegrityError as e:
            self.conn.rollback()  # Deshacer cambios en caso de violación de integridad
            logger.error(f"Database integrity error: {e}")
            raise Exception(f"Database integrity error: {e}")

        except sqlite3.OperationalError as e:
            self.conn.rollback()  # Deshacer cambios en caso de error de operación
            logger.error(f"Database operational error: {e}")
            raise Exception(f"Database operational error: {e}")

        except Exception as e:
            self.conn.rollback()  # Deshacer cambios en caso de error desconocido
            logger.error(f"Database unexpected error: {e}")
            raise Exception(f"Database unexpected error: {e}")

    def execute_transaction(self, queries):
        """
        Executes multiple SQL queries within a single transaction.

        Parameters:
        - queries: List of tuples containing (query, params).
        """

        try:
            # conn = DatabaseConnectionSetting.get_connection()
            # cursor = conn.cursor()

            # Begin transaction
            self.cursor.execute("BEGIN TRANSACTION;")

            for query, params in queries:
                logger.info(f"BackEnd: execute_transaction: Info executing query: {query} with params: {params}")
                self.cursor.execute(query, params)

            self.conn.commit()  # Commit all changes
        except Exception as e:
            self.conn.rollback()  # Rollback on error
            raise Exception(f"Transaction error: {e}")

    def execute_bd_migrations(self, queries):
        """
        Executes multiple SQL queries within a single transaction.

        Parameters:
        - queries: List of tuples containing (query, params).
        """
        try:
            # conn = DatabaseConnectionSetting.get_connection()
            # cursor = conn.cursor()

            # Begin transaction
            self.cursor.execute("BEGIN TRANSACTION;")

            for query, params in queries:
                # logger.info(f"BackEnd: execute_bd_migrations: Executing migration, the query executed was: {query}")

                self.cursor.execute(query, params)
            logger.info(f"BackEnd: execute_bd_migrations: Executing migration ...")
            self.conn.commit()  # Commit all changes
        except Exception as e:
            self.conn.rollback()  # Rollback on error
            raise Exception(f"Transaction error: {e}")
