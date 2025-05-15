"""
Configuration loader for database settings from a YAML file.

This module defines a class and utility functions to load database
configuration details, primarily the database file path, from 'db_setting.yaml'.
It ensures correct path resolution for the application.
"""

import os
from pathlib import Path # For more robust path manipulation
from typing import Dict, Any # For type hinting

import yaml # PyYAML library for YAML parsing

# Assuming this import is correct for your project structure.
# If Pylint complains, ensure 'off_chain' is in PYTHONPATH or use a relative import
# if appropriate, or disable the specific import error with a comment.
from off_chain.configuration.log_load_setting import logger

# --- Constants ---
# The name of the YAML configuration file.
DB_CONFIG_FILENAME = "db_setting.yaml"

# Determine the directory of the current script.
# This is often used as a base for locating other files.
_CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent

# Define the absolute path to the database settings YAML file.
# It's assumed to be in the same directory as this script.
_DATABASE_CONFIG_FILE_PATH: Path = _CURRENT_SCRIPT_DIR / DB_CONFIG_FILENAME

# --- Custom Exceptions (Optional but good for clarity) ---
class ConfigFileNotFoundError(FileNotFoundError):
    """Custom exception for when the configuration file is not found."""

class ConfigFileError(Exception):
    """Custom exception for errors during configuration file loading or parsing."""


class DatabaseYamlConfigLoader:
    """
    Handles loading database configurations from a YAML file.
    Provides a static method to load the configuration.
    """

    # Pylint R0903: too-few-public-methods (1/1)
    # This class only has one public method, which is fine for a dedicated loader.
    # If Pylint flags this, you can disable it with a comment or reconsider
    # if this functionality could be a simple module-level function.
    # For now, keeping it as a class for organizational clarity.
    # pylint: disable=too-few-public-methods

    @staticmethod
    def load_settings(config_file_path: Path = _DATABASE_CONFIG_FILE_PATH) -> Dict[str, Any]:
        """
        Reads and loads a YAML configuration file into a dictionary.

        Args:
            config_file_path: The absolute path to the YAML configuration file.
                              Defaults to the path defined at the module level.

        Returns:
            A dictionary containing the loaded configuration.

        Raises:
            ConfigFileNotFoundError: If the configuration file does not exist.
            ConfigFileError: If there's an error reading or parsing the YAML file.
        """
        logger.debug("Attempting to load configuration from: %s", config_file_path)
        if not config_file_path.is_file():
            error_msg = f"Configuration file not found: {config_file_path}"
            logger.error(error_msg)
            raise ConfigFileNotFoundError(error_msg)

        try:
            with open(config_file_path, "r", encoding="utf-8") as file_stream:
                config_data = yaml.safe_load(file_stream)
            if not isinstance(config_data, dict):
                # safe_load can return non-dict types (e.g. a list if YAML is just a list)
                # For configuration, we usually expect a dictionary.
                error_msg = (
                    f"Configuration file did not load as a dictionary: {config_file_path}. "
                    f"Actual type: {type(config_data)}"
                )
                logger.error(error_msg)
                raise ConfigFileError(error_msg)
            logger.info("Successfully loaded configuration from: %s", config_file_path)
            return config_data
        except yaml.YAMLError as e:
            error_msg = f"Error parsing YAML configuration file '{config_file_path}': {e}"
            logger.error(error_msg, exc_info=True) # Log traceback for YAML errors
            raise ConfigFileError(error_msg) from e
        except IOError as e: # Catch file reading errors (e.g., permissions)
            error_msg = f"Error reading configuration file '{config_file_path}': {e}"
            logger.error(error_msg, exc_info=True)
            raise ConfigFileError(error_msg) from e
        except Exception as e: # Catch any other unexpected errors
            error_msg = f"An unexpected error occurred while loading configuration from " \
                        f"'{config_file_path}': {e}"
            logger.error(error_msg, exc_info=True)
            raise ConfigFileError(error_msg) from e


# --- Module-Level Configuration Loading ---
# This section loads the configuration when the module is imported.

# pylint: disable=invalid-name
# Justification: 'loaded_database_config' and 'DATABASE_PATH' are module-level
# constants derived from configuration, and uppercase is conventional for such constants.
# Pylint might flag them if it expects lowercase for module-level variables not
# strictly matching its constant pattern (e.g. if it's a complex object).

try:
    logger.info("Loading database configuration settings...")
    # Load general database configuration from the YAML file.
    loaded_database_config: Dict[str, Any] = DatabaseYamlConfigLoader.load_settings()

    # --- Construct the Database Path ---
    # Expecting a structure like:
    # database:
    #   path_database: "your_db_name.sqlite3"

    if not (isinstance(loaded_database_config.get("database"), dict) and
            isinstance(loaded_database_config["database"].get("path_database"), str)):
        err_msg = (
            "Invalid configuration structure in 'db_setting.yaml'. "
            "Expected 'database.path_database' string."
        )
        logger.critical(err_msg) # Critical as this path is essential
        raise ConfigFileError(err_msg)

    db_relative_path_str: str = loaded_database_config["database"]["path_database"]

    # The base directory for the database files is expected to be '../database/'
    # relative to the directory of THIS configuration script (_CURRENT_SCRIPT_DIR).
    # _CURRENT_SCRIPT_DIR -> e.g., /path/to/project/off_chain/configuration/
    # PARENT_OF_SCRIPT_DIR -> e.g., /path/to/project/off_chain/
    # GRANDPARENT_OF_SCRIPT_DIR -> e.g., /path/to/project/
    # Then, we target 'database/' directory, which would be relative to GRANDPARENT if
    # 'database' is at the project root.
    # Or, if 'database' is inside 'off_chain', then it's relative to PARENT_OF_SCRIPT_DIR.

    # Assuming "database" folder is at the same level as "off_chain" folder
    # e.g. project_root/off_chain/configuration (this file)
    #      project_root/database/ (target)
    # So, from _CURRENT_SCRIPT_DIR (off_chain/configuration), go up two levels
    # to project_root, then into 'database'.
    _PROJECT_ROOT_DIR = _CURRENT_SCRIPT_DIR.parent.parent
    _DATABASE_BASE_DIR = _PROJECT_ROOT_DIR / "database"

    # Construct the absolute path to the database file.
    DATABASE_PATH: Path = (_DATABASE_BASE_DIR / db_relative_path_str).resolve()

    logger.info("Resolved absolute database path: %s", DATABASE_PATH)

    # Optional: Check if the resolved database directory exists,
    # but not necessarily the file itself, as it might be created by the application.
    if not DATABASE_PATH.parent.is_dir():
        logger.warning(
            "The parent directory for the database ('%s') does not exist. "
            "It might be created by the application later.",
            DATABASE_PATH.parent
        )
    # The actual existence check of DATABASE_PATH itself should be done
    # by the Database connection class when it tries to connect/create it.

except (ConfigFileNotFoundError, ConfigFileError) as e:
    logger.critical(
        "Failed to load essential database configuration: %s. Application may not run correctly.",
        e, exc_info=True
    )
    # Depending on application requirements, you might re-raise or set DATABASE_PATH to None,
    # forcing other parts of the app to handle the missing config.
    # For now, let it propagate if critical.
    DATABASE_PATH = None # Or raise a more specific "AppConfigError"
    # raise RuntimeError(f"Critical configuration error: {e}") from e
    # If DATABASE_PATH must exist for the app to start, re-raising is better.

# pylint: enable=invalid-name

if __name__ == "__main__":
    # This block allows testing the configuration loading independently.
    # Create a dummy logger for testing if the main logger isn't set up.
    import logging
    if not logger.hasHandlers(): # Check if logger has handlers (simplistic check)
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)


    logger.info("--- Running YAML Config Loader Self-Test ---")
    logger.info("Default DB Config File Path: %s", _DATABASE_CONFIG_FILE_PATH)

    # To test, you'd need a dummy 'db_setting.yaml' in the same directory
    # as this script. Example content for 'db_setting.yaml':
    #
    # database:
    #   path_database: "my_app_data.sqlite3"
    # other_settings:
    #   feature_enabled: true

    # Create a dummy config file for testing
    dummy_config_content = """
database:
  path_database: "test_db.sqlite3"
test_setting: "hello world"
    """
    dummy_config_path = _CURRENT_SCRIPT_DIR / "temp_db_setting_for_test.yaml"
    try:
        with open(dummy_config_path, "w", encoding="utf-8") as f:
            f.write(dummy_config_content)

        # Test loading the dummy config
        cfg = DatabaseYamlConfigLoader.load_settings(dummy_config_path)
        logger.info("Loaded test configuration: %s", cfg)
        assert cfg["database"]["path_database"] == "test_db.sqlite3"
        assert cfg["test_setting"] == "hello world"
        logger.info("Test config loaded and assertions passed.")

        # Test module-level loaded DATABASE_PATH (if the dummy was named db_setting.yaml)
        # If we loaded a *different* file for the test, DATABASE_PATH global
        # would be based on the *actual* db_setting.yaml (or fail if it doesn't exist).
        # For a full test of the global DATABASE_PATH, you'd rename dummy_config_path
        # to _DATABASE_CONFIG_FILE_PATH temporarily or mock it.

        # Assuming the global DATABASE_PATH was set using the dummy file (if named correctly)
        if DATABASE_PATH: # Check if it was successfully set
            logger.info("Module-level DATABASE_PATH (if dummy was default name): %s", DATABASE_PATH)
            # Add assertions based on expected path
            # e.g. assert "test_db.sqlite3" in str(DATABASE_PATH)
        else:
            logger.warning("Module-level DATABASE_PATH was not set, possibly due to "
                           "using a non-default test file name or load failure.")


    except Exception as e: # pylint: disable=broad-except
        logger.error("Error during self-test: %s", e, exc_info=True)
    finally:
        if dummy_config_path.exists():
            os.remove(dummy_config_path)
            logger.info("Cleaned up temporary test config file.")

    logger.info("--- YAML Config Loader Self-Test Finished ---")