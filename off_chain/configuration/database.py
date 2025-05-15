# pylint: disable=c-extension-no-member
# (If Pylint has issues with sqlite3 members, though usually not needed)
"""
Singleton database connection manager for SQLite.

Provides methods to execute queries, fetch results, and manage transactions
while ensuring a single, persistent connection to the database.
"""
import os
import sqlite3
from typing import Any, List, Tuple, Optional, Sequence # For type hinting

# Assuming these imports are correctly placed in your project structure
# and Pylint can find them. If not, you might need to adjust sys.path
# or use pylint: disable=import-error for these specific lines.
from off_chain.configuration.db_load_setting import DATABASE_PATH
from off_chain.configuration.log_load_setting import logger

# --- Constants ---
DATABASE_CONNECTION_TIMEOUT_SECONDS = 10
PRAGMA_FOREIGN_KEYS_ON = "PRAGMA foreign_keys = ON"
SQL_BEGIN_TRANSACTION = "BEGIN TRANSACTION;"


# --- Custom Exceptions (Optional but good practice) ---
class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues."""

class DatabaseQueryError(sqlite3.Error): # Inherit from sqlite3.Error for specificity
    """Custom exception for query execution errors."""

class DuplicateKeyError(DatabaseQueryError, sqlite3.IntegrityError):
    """Specific error for unique constraint violations."""


class Database:
    """
    Singleton class to manage a SQLite database connection.

    This class ensures that only one connection to the database is active
    throughout the application's lifecycle. It provides methods for
    executing queries, fetching data, and managing transactions.
    """
    _instance: Optional['Database'] = None
    _lock_initialized: bool = False # To ensure __init__ logic runs only once

    def __new__(cls, *args, **kwargs) -> 'Database':
        """
        Implements the Singleton pattern.
        Ensures only one instance of the Database class is created.
        """
        if cls._instance is None:
            logger.debug("Creating new Database instance.")
            cls._instance = super().__new__(cls)
            # Reset the _lock_initialized flag for the new instance
            # This ensures __init__ can run for this specific new instance
            cls._instance._lock_initialized = False
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the database connection.
        This method is called every time Database() is invoked,
        but the connection logic is guarded to run only once per instance.
        """
        if self._lock_initialized:
            logger.debug("Database connection already initialized for this instance.")
            return

        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

        try:
            logger.info("Attempting to connect to database at: %s", DATABASE_PATH)
            # The actual connection object
            self.conn = sqlite3.connect(DATABASE_PATH, timeout=DATABASE_CONNECTION_TIMEOUT_SECONDS)
            # Enable foreign key constraints for data integrity
            self.conn.execute(PRAGMA_FOREIGN_KEYS_ON)
            self.cursor = self.conn.cursor()
            logger.info(
                "Database connection successful. DB: %s, Path: %s",
                os.path.basename(DATABASE_PATH), DATABASE_PATH
            )
            self._lock_initialized = True # Mark as initialized for this instance
        except sqlite3.ProgrammingError as e:
            logger.error("Programming error during DB connection (e.g., closed database): %s", e, exc_info=True)
            raise DatabaseConnectionError(f"Cannot operate on a closed database: {e}") from e
        except sqlite3.DatabaseError as e: # Catches more specific errors like "file is not a database"
            logger.error("Database file error (e.g., encrypted or not a DB): %s", e, exc_info=True)
            raise DatabaseConnectionError(f"File is encrypted or is not a database: {e}") from e
        except Exception as e: # Catch-all for unexpected errors during connection
            logger.error("Unexpected error during database connection: %s", e, exc_info=True)
            raise DatabaseConnectionError(f"Unexpected error connecting to database: {e}") from e

    def _ensure_connection_active(self) -> None:
        """Checks if the database connection and cursor are active, raises if not."""
        if self.conn is None or self.cursor is None:
            logger.error("Database connection is not active or has been closed.")
            raise DatabaseConnectionError("Database connection is not active. Please re-initialize.")

    def execute_query(self, query: str, params: Sequence[Any] = ()) -> int:
        """
        Executes a modification query (INSERT, UPDATE, DELETE).

        Args:
            query: The SQL query string.
            params: A sequence of parameters to substitute into the query.

        Returns:
            The number of rows affected by the query.

        Raises:
            DatabaseConnectionError: If the database connection is not active.
            DuplicateKeyError: If a unique constraint is violated.
            DatabaseQueryError: For other SQL execution errors.
        """
        self._ensure_connection_active()
        # Type assertion for Pylint/MyPy if _ensure_connection_active isn't enough
        assert self.conn is not None and self.cursor is not None

        logger.debug("Executing query: %s with params: %s", query, params)
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            logger.info("Query executed successfully. Rows affected: %d", self.cursor.rowcount)
            return self.cursor.rowcount
        except sqlite3.IntegrityError as e:
            self.conn.rollback() # Rollback on integrity error
            if "UNIQUE constraint failed" in str(e):
                logger.warning("Duplicate key violation for query: %s, params: %s. Error: %s",
                               query, params, e)
                raise DuplicateKeyError(f"Duplicate key violation: {e}") from e
            logger.error("Integrity error during query: %s. Error: %s", query, e, exc_info=True)
            raise DatabaseQueryError(f"Database integrity error: {e}") from e
        except sqlite3.OperationalError as e:
            self.conn.rollback() # Rollback on operational error
            logger.error("Operational error during query: %s (Database locked? %s). Error: %s",
                         query, "locked" in str(e).lower(), e, exc_info=True)
            raise DatabaseQueryError(f"Database operational error: {e}") from e
        except sqlite3.Error as e: # Catch other specific sqlite3 errors
            self.conn.rollback()
            logger.error("Generic SQLite error during query: %s. Error: %s", query, e, exc_info=True)
            raise DatabaseQueryError(f"Generic database error: {e}") from e

    def fetch_all(self, query: str, params: Sequence[Any] = ()) -> List[Tuple[Any, ...]]:
        """
        Executes a SELECT query and returns all results.

        Args:
            query: The SQL query string.
            params: A sequence of parameters to substitute into the query.

        Returns:
            A list of tuples, where each tuple represents a row. Empty list if no results.

        Raises:
            DatabaseConnectionError: If the database connection is not active.
            DatabaseQueryError: For SQL execution errors.
        """
        self._ensure_connection_active()
        assert self.cursor is not None # For type checkers

        logger.debug("Fetching all results for query: %s with params: %s", query, params)
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            logger.info("Fetched %d rows for query: %s", len(results), query)
            return results
        except sqlite3.OperationalError as e:
            logger.error("Operational error during fetch_all: %s (Database locked? %s). Error: %s",
                         query, "locked" in str(e).lower(), e, exc_info=True)
            raise DatabaseQueryError(f"Database operational error during fetch: {e}") from e
        except sqlite3.Error as e:
            logger.error("Generic SQLite error during fetch_all: %s. Error: %s", query, e, exc_info=True)
            raise DatabaseQueryError(f"Generic database error during fetch: {e}") from e

    def fetch_one_row(self, query: str, params: Sequence[Any] = ()) -> Optional[Tuple[Any, ...]]:
        """
        Executes a SELECT query and returns the first row as a tuple.

        Args:
            query: The SQL query string.
            params: A sequence of parameters to substitute into the query.

        Returns:
            A tuple representing the first row, or None if no results.

        Raises:
            DatabaseConnectionError: If the database connection is not active.
            DatabaseQueryError: For SQL execution errors.
        """
        self._ensure_connection_active()
        assert self.cursor is not None

        logger.debug("Fetching one row for query: %s with params: %s", query, params)
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            logger.info("Fetched one row for query: %s. Result: %s",
                        query, "Found" if result else "Not found")
            return result
        except sqlite3.OperationalError as e:
            logger.error("Operational error during fetch_one_row: %s (Database locked? %s). Error: %s",
                         query, "locked" in str(e).lower(), e, exc_info=True)
            raise DatabaseQueryError(f"Database operational error during fetch: {e}") from e
        except sqlite3.Error as e:
            logger.error("Generic SQLite error during fetch_one_row: %s. Error: %s", query, e, exc_info=True)
            raise DatabaseQueryError(f"Generic database error during fetch: {e}") from e

    def fetch_scalar(self, query: str, params: Sequence[Any] = ()) -> Optional[Any]:
        """
        Executes a query and returns the first column of the first row (a scalar value).

        Args:
            query: The SQL query string.
            params: A sequence of parameters to substitute into the query.

        Returns:
            The scalar value, or None if no results or the cell is NULL.

        Raises:
            DatabaseConnectionError: If the database connection is not active.
            DatabaseQueryError: For SQL execution errors.
        """
        row = self.fetch_one_row(query, params)
        return row[0] if row else None

    def execute_transaction(self, queries_with_params: List[Tuple[str, Sequence[Any]]]) -> None:
        """
        Executes multiple SQL queries within a single transaction.
        Rolls back all changes if any query fails.

        Args:
            queries_with_params: A list of tuples, where each tuple contains
                                 (query_string, parameters_sequence).

        Raises:
            DatabaseConnectionError: If the database connection is not active.
            DatabaseQueryError: For SQL execution errors within the transaction.
        """
        self._ensure_connection_active()
        assert self.conn is not None and self.cursor is not None

        logger.info("Starting transaction with %d queries.", len(queries_with_params))
        try:
            # Explicitly begin transaction (though often implicit, good for clarity)
            # self.cursor.execute(SQL_BEGIN_TRANSACTION) # Optional, often handled by commit/rollback

            for query, params in queries_with_params:
                logger.debug("Transaction: Executing query: %s with params: %s", query, params)
                self.cursor.execute(query, params)

            self.conn.commit()
            logger.info("Transaction committed successfully.")
        except sqlite3.Error as e: # Catches all sqlite3 errors for rollback
            logger.error("Error during transaction, rolling back. Error: %s", e, exc_info=True)
            if self.conn: # Check if conn is still valid before rollback
                try:
                    self.conn.rollback()
                    logger.info("Transaction rolled back.")
                except sqlite3.Error as rb_err: # Error during rollback itself
                    logger.error("Error during transaction rollback: %s", rb_err, exc_info=True)
            raise DatabaseQueryError(f"Transaction failed and was rolled back: {e}") from e
        except Exception as e: # Catch non-SQLite errors, attempt rollback
            logger.error("Unexpected error during transaction, rolling back. Error: %s", e, exc_info=True)
            if self.conn:
                try:
                    self.conn.rollback()
                    logger.info("Transaction rolled back due to unexpected error.")
                except sqlite3.Error as rb_err:
                    logger.error("Error during transaction rollback after unexpected error: %s", rb_err, exc_info=True)
            raise DatabaseQueryError(f"Unexpected error in transaction, rolled back: {e}") from e


    def close(self) -> None:
        """
        Closes the database connection safely.
        Resets the singleton instance so a new connection can be made if needed.
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed successfully.")
            except sqlite3.Error as e: # More specific than Exception
                logger.error("Error closing database connection: %s", e, exc_info=True)
            finally:
                self.conn = None
                self.cursor = None
                # Reset the initialization lock for this specific (now closed) instance state.
                # If a new instance is requested, __init__ should re-run.
                self._lock_initialized = False
                # Crucially, to allow re-creation of a truly new connection
                # if Database() is called again after close(), we should nullify _instance.
                Database._instance = None
                logger.debug("Database singleton instance reset.")

    # Alias for close() for backward compatibility or preference
    close_connection = close

    def __enter__(self) -> 'Database':
        """Enter the runtime context related to this object."""
        # The connection is established in __init__ when the instance is created.
        # If using as a context manager for the lifetime of the app, this is fine.
        # If meant for short-lived contexts, the singleton pattern might conflict.
        # For this singleton, __enter__ just returns self.
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the runtime context and close the connection."""
        # This will close the singleton connection, which might be desired
        # at the end of a `with Database() as db:` block if the app is ending.
        self.close()

    def __del__(self) -> None:
        """
        Ensures the database connection is closed when the instance is garbage collected.
        This is a fallback mechanism. Explicitly calling `close()` is preferred.
        """
        logger.debug("Database instance __del__ called. Attempting to close connection if active.")
        # Check if _lock_initialized is True and conn exists,
        # to avoid errors if __init__ failed.
        if getattr(self, '_lock_initialized', False) and hasattr(self, 'conn') and self.conn:
            self.close()

# Example usage (optional, for testing)
if __name__ == "__main__":
    # Configure logger for standalone testing
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger.info("--- Running Database Class Self-Test ---")

    # Test Singleton
    db1 = Database()
    db2 = Database()
    logger.info("db1 is db2: %s (Expected: True)", db1 is db2)

    try:
        # Test basic query execution
        # Create a dummy table for testing
        db1.execute_query("DROP TABLE IF EXISTS test_items")
        db1.execute_query("CREATE TABLE test_items (id INTEGER PRIMARY KEY, name TEXT UNIQUE, value REAL)")
        logger.info("Test table created.")

        # Insert data
        insert_count1 = db1.execute_query("INSERT INTO test_items (name, value) VALUES (?, ?)", ("item1", 10.5))
        logger.info("Inserted item1, rows affected: %d", insert_count1)
        insert_count2 = db1.execute_query("INSERT INTO test_items (name, value) VALUES (?, ?)", ("item2", 20.0))
        logger.info("Inserted item2, rows affected: %d", insert_count2)

        # Test duplicate key
        try:
            db1.execute_query("INSERT INTO test_items (name, value) VALUES (?, ?)", ("item1", 30.0))
        except DuplicateKeyError as e:
            logger.info("Correctly caught DuplicateKeyError: %s", e)

        # Fetch all
        all_items = db1.fetch_all("SELECT id, name, value FROM test_items ORDER BY id")
        logger.info("Fetched all items: %s", all_items)
        assert len(all_items) == 2
        assert all_items[0][1] == "item1"

        # Fetch one row
        one_item_row = db1.fetch_one_row("SELECT name FROM test_items WHERE id = ?", (1,))
        logger.info("Fetched one item row: %s", one_item_row)
        assert one_item_row is not None and one_item_row[0] == "item1"

        # Fetch scalar
        item_name = db1.fetch_scalar("SELECT name FROM test_items WHERE id = ?", (2,))
        logger.info("Fetched scalar (item name): %s", item_name)
        assert item_name == "item2"
        null_scalar = db1.fetch_scalar("SELECT name FROM test_items WHERE id = ?", (99,))
        logger.info("Fetched scalar (non-existent): %s (Expected: None)", null_scalar)
        assert null_scalar is None

        # Test transaction success
        logger.info("Testing successful transaction...")
        transaction_queries_success = [
            ("INSERT INTO test_items (name, value) VALUES (?, ?)", ("item_tx_1", 100.0)),
            ("INSERT INTO test_items (name, value) VALUES (?, ?)", ("item_tx_2", 200.0)),
            ("UPDATE test_items SET value = ? WHERE name = ?", (11.0, "item1"))
        ]
        db1.execute_transaction(transaction_queries_success)
        tx_test_item1 = db1.fetch_scalar("SELECT value FROM test_items WHERE name = ?", ("item1",))
        assert tx_test_item1 == 11.0
        logger.info("Successful transaction verified.")

        # Test transaction failure (rollback)
        logger.info("Testing transaction rollback...")
        original_item2_value = db1.fetch_scalar("SELECT value FROM test_items WHERE name = ?", ("item2",))
        transaction_queries_fail = [
            ("UPDATE test_items SET value = ? WHERE name = ?", (999.0, "item2")), # This will succeed
            ("INSERT INTO test_items (name, value) VALUES (?, ?)", ("item_tx_1", 300.0)) # This will fail (duplicate)
        ]
        try:
            db1.execute_transaction(transaction_queries_fail)
        except DatabaseQueryError as e: # Should catch DuplicateKeyError wrapped in DatabaseQueryError
            logger.info("Correctly caught DatabaseQueryError for failed transaction: %s", e)
        item2_value_after_failed_tx = db1.fetch_scalar("SELECT value FROM test_items WHERE name = ?", ("item2",))
        assert item2_value_after_failed_tx == original_item2_value # Check rollback
        logger.info("Transaction rollback verified. Item2 value: %s (Original: %s)",
                    item2_value_after_failed_tx, original_item2_value)

    except Exception as e: # pylint: disable=broad-except
        logger.error("An error occurred during self-test: %s", e, exc_info=True)
    finally:
        logger.info("--- Closing DB connection for self-test ---")
        if 'db1' in locals() and db1:
            db1.close()

        # Verify instance is reset after close
        db3 = Database() # Should be a new instance, re-connecting
        logger.info("db1 is db3 after db1.close(): %s (Expected: False if db1 existed, True if db1 was None)",
                    db1 is db3 if 'db1' in locals() else "db1 not defined")
        if db3.conn: # Check if the new instance connected
            logger.info("New instance db3 connected successfully.")
            db3.close()
        else:
            logger.error("New instance db3 FAILED to connect after previous close.")

    logger.info("--- Database Class Self-Test Finished ---")