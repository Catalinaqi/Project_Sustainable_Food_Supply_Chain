"""
Database migration utility.

This script applies SQL migration files found in a 'migrations' subdirectory
to a SQLite database. It keeps track of applied migrations in a dedicated
'migrations' table to prevent re-applying them.
"""

import logging
import sqlite3
from pathlib import Path # For robust path manipulation
from typing import Set # For type hinting

# --- Constants ---
MIGRATIONS_DIRECTORY_NAME = "migrations"
MIGRATIONS_METADATA_TABLE_NAME = "schema_migrations" # More conventional name

# --- Configure Basic Logging (if not already configured globally) ---
# This allows the script to log errors even if run standalone before
# a more comprehensive logging setup is in place by the main application.
# If your application already configures logging globally, this might be redundant
# or could be made conditional.
# pylint: disable=invalid-name
# 'logger' is a conventional name for a module-level logger instance.
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
# pylint: enable=invalid-name


# --- Custom Exceptions ---
class MigrationError(Exception):
    """Base exception for errors during the migration process."""

class MigrationFileError(MigrationError):
    """Exception for errors related to reading or accessing migration files."""


def _get_applied_migrations(cursor: sqlite3.Cursor) -> Set[str]:
    """
    Retrieves the set of already applied migration filenames from the database.

    Args:
        cursor: The database cursor.

    Returns:
        A set of filenames of migrations that have been applied.
    """
    try:
        cursor.execute(f"SELECT filename FROM {MIGRATIONS_METADATA_TABLE_NAME}")
        return {row[0] for row in cursor.fetchall()}
    except sqlite3.Error as e:
        logger.error("Failed to query applied migrations: %s", e, exc_info=True)
        raise MigrationError(f"Could not retrieve applied migrations: {e}") from e


def _ensure_migrations_table_exists(cursor: sqlite3.Cursor) -> None:
    """
    Creates the migrations metadata table if it doesn't already exist.

    Args:
        cursor: The database cursor.
    """
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {MIGRATIONS_METADATA_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("'%s' table ensured to exist.", MIGRATIONS_METADATA_TABLE_NAME)
    except sqlite3.Error as e:
        logger.error("Failed to create '%s' table: %s", MIGRATIONS_METADATA_TABLE_NAME, e, exc_info=True)
        raise MigrationError(f"Could not create migrations metadata table: {e}") from e


def _record_migration_applied(cursor: sqlite3.Cursor, filename: str) -> None:
    """
    Records a migration as applied in the migrations metadata table.

    Args:
        cursor: The database cursor.
        filename: The filename of the migration that was applied.
    """
    try:
        cursor.execute(f"INSERT INTO {MIGRATIONS_METADATA_TABLE_NAME} (filename) VALUES (?)", (filename,))
        logger.info("Recorded migration '%s' as applied.", filename)
    except sqlite3.Error as e:
        logger.error("Failed to record migration '%s': %s", filename, e, exc_info=True)
        # This is a critical error, as the migration was applied but not recorded.
        # The database might be in an inconsistent state regarding metadata.
        raise MigrationError(
            f"Failed to record applied migration '{filename}'. Manual check required: {e}"
        ) from e


def run_all_migrations(database_path: Path) -> None:
    """
    Applies all pending SQL migration scripts from the 'migrations' directory
    to the specified SQLite database.

    Migration files should be named in a way that sorting them alphabetically
    results in the correct application order (e.g., '001_create_users.sql',
    '002_add_posts_table.sql').

    Args:
        database_path: The Path object pointing to the SQLite database file.

    Raises:
        MigrationError: If any part of the migration process fails.
        FileNotFoundError: If the migrations directory does not exist.
    """
    logger.info("Starting database migration process for database: %s", database_path)

    migrations_dir = Path(__file__).resolve().parent / MIGRATIONS_DIRECTORY_NAME
    if not migrations_dir.is_dir():
        logger.error("Migrations directory not found at: %s", migrations_dir)
        raise FileNotFoundError(f"Migrations directory '{migrations_dir}' does not exist.")

    conn: sqlite3.Connection = None # Initialize to None for finally block
    try:
        # Ensure the directory for the database file exists
        database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(database_path, timeout=10.0) # Added timeout
        cursor = conn.cursor()

        # Ensure foreign key support is enabled for the connection (good practice)
        cursor.execute("PRAGMA foreign_keys = ON;")

        _ensure_migrations_table_exists(cursor)
        applied_migrations = _get_applied_migrations(cursor)

        # Get all .sql files from migrations directory, sorted alphabetically
        try:
            migration_files = sorted([
                f.name for f in migrations_dir.iterdir() if f.is_file() and f.suffix == '.sql'
            ])
        except OSError as e:
            logger.error("Could not list files in migrations directory '%s': %s", migrations_dir, e, exc_info=True)
            raise MigrationFileError(f"Error accessing migrations directory: {e}") from e


        if not migration_files:
            logger.info("No migration files found in '%s'.", migrations_dir)
            return

        pending_migrations = [mf for mf in migration_files if mf not in applied_migrations]

        if not pending_migrations:
            logger.info("Database schema is up to date. No new migrations to apply.")
            return

        logger.info("Found %d pending migration(s) to apply.", len(pending_migrations))

        for filename in pending_migrations:
            logger.info("Applying migration: %s", filename)
            migration_file_path = migrations_dir / filename
            try:
                with open(migration_file_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                if not sql_script.strip():
                    logger.warning("Migration file '%s' is empty. Skipping.", filename)
                    # Optionally, record empty migrations as applied if that's the desired behavior
                    # _record_migration_applied(cursor, filename)
                    # conn.commit()
                    continue

                cursor.executescript(sql_script) # Executes one or more SQL statements
                _record_migration_applied(cursor, filename)
                conn.commit() # Commit after each successful migration file
                logger.info("Successfully applied and recorded migration: %s", filename)

            except FileNotFoundError: # Should not happen if iterdir worked, but defensive
                logger.error("Migration file '%s' not found during application.", migration_file_path, exc_info=True)
                raise MigrationFileError(f"Migration file not found: {migration_file_path}") from None
            except IOError as e:
                logger.error("Error reading migration file '%s': %s", migration_file_path, e, exc_info=True)
                raise MigrationFileError(f"IOError reading migration file '{migration_file_path}': {e}") from e
            except sqlite3.Error as e:
                logger.error("Error applying SQL from migration '%s': %s", filename, e, exc_info=True)
                conn.rollback() # Rollback changes from the failed script
                raise MigrationError(f"SQL error in migration '{filename}': {e}") from e
            # No broad except Exception here, let specific ones propagate or be caught by outer try

        logger.info("All pending migrations applied successfully.")

    except sqlite3.Error as e: # Catch connection errors or other SQLite errors not caught inside loop
        logger.error("A database error occurred during the migration process: %s", e, exc_info=True)
        if conn:
            try:
                conn.rollback() # Attempt rollback if connection exists
            except sqlite3.Error as rb_err:
                logger.error("Failed to rollback database transaction: %s", rb_err, exc_info=True)
        raise MigrationError(f"Database error during migrations: {e}") from e
    except MigrationError: # Re-raise custom migration errors
        raise
    except Exception as e: # Catch any other unexpected errors
        logger.critical("An unexpected critical error occurred during migrations: %s", e, exc_info=True)
        if conn:
            try:
                conn.rollback()
            except sqlite3.Error as rb_err:
                logger.error("Failed to rollback database transaction after unexpected error: %s", rb_err, exc_info=True)
        raise MigrationError(f"Unexpected critical error during migrations: {e}") from e
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Database connection closed.")
            except sqlite3.Error as e:
                logger.error("Error closing database connection: %s", e, exc_info=True)


if __name__ == "__main__":
    # Determine the default database path relative to this script
    # e.g., if this script is in 'project/db_utils/', db is 'project/data/sfs_chain_database.db'
    _default_db_file_name = "sfs_chain_database.db"
    _default_db_path = Path(__file__).resolve().parent.parent / "data" / _default_db_file_name
    # Adjust the relative path (e.g., .parent.parent / "data") as needed for your project structure.
    # If the DB is in the same directory as this script, it would be:
    # _default_db_path = Path(__file__).resolve().parent / _default_db_file_name

    logger.info("--- Running Standalone Database Migrator ---")
    logger.info("Default database path: %s", _default_db_path)

    # For testing, ensure a 'migrations' directory exists next to this script.
    # Example:
    # your_project/
    #   db_utils/
    #     this_migration_script.py
    #     migrations/
    #       001_initial_schema.sql
    #       002_add_users_table.sql
    #   data/
    #     sfs_chain_database.db (will be created/updated)

    migrations_test_dir = Path(__file__).resolve().parent / MIGRATIONS_DIRECTORY_NAME
    if not migrations_test_dir.is_dir():
        logger.warning(
            "Test 'migrations' directory not found at '%s'. Creating for test.",
            migrations_test_dir
        )
        migrations_test_dir.mkdir(exist_ok=True)
        # Create a dummy migration file for testing if none exist
        dummy_migration_file = migrations_test_dir / "000_dummy_test_migration.sql"
        if not list(migrations_test_dir.glob("*.sql")): # if no sql files exist
            try:
                with open(dummy_migration_file, "w", encoding="utf-8") as f_dummy:
                    f_dummy.write("-- This is a dummy migration for testing purposes.\n")
                    f_dummy.write("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT);\n")
                logger.info("Created dummy migration file: %s", dummy_migration_file)
            except IOError as e:
                logger.error("Could not create dummy migration file for testing: %s", e)

    try:
        run_all_migrations(_default_db_path)
        logger.info("Standalone migration run completed.")
        # Run again to test "schema is up to date"
        logger.info("Running migrations again (should detect schema is up to date)...")
        run_all_migrations(_default_db_path)

    except MigrationError as e_mig:
        logger.error("Migration process failed: %s", e_mig)
    except Exception as e_main: # pylint: disable=broad-except
        logger.error("An unexpected error occurred in the main execution block: %s", e_main, exc_info=True)
    finally:
        # Clean up dummy migration file if created
        if 'dummy_migration_file' in locals() and dummy_migration_file.exists():
            try:
                dummy_migration_file.unlink()
                logger.info("Cleaned up dummy migration file: %s", dummy_migration_file)
            except OSError as e_unlink:
                logger.warning("Could not remove dummy migration file '%s': %s", dummy_migration_file, e_unlink)

    logger.info("--- Standalone Database Migrator Finished ---")