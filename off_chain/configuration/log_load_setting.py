"""
Logging configuration manager for the application.

This module sets up Python's logging framework using settings from
a 'log_setting.yaml' file. It configures handlers for console output
and optional file logging, ensuring logs are formatted and managed
according to the specified configuration.
"""

import logging
import logging.config # For dictConfig
import os
from pathlib import Path # For robust path manipulation
from typing import Dict, Any, Optional # For type hinting

import yaml # PyYAML for parsing YAML configuration

# --- Constants ---

# Directory of the current script (e.g., .../off_chain/configuration/)
_CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent

# Path to the YAML file containing logging settings.
# Assumed to be in the same directory as this script.
_LOGGING_SETTINGS_YAML_FILE: Path = _CURRENT_SCRIPT_DIR / "log_setting.yaml"

# Base directory for log files.
# e.g., if _CURRENT_SCRIPT_DIR is .../off_chain/configuration/,
# then _LOG_FILES_BASE_DIR will be .../off_chain/log/
# Adjust .parent.parent if "log" is at the project root.
# Assuming "log" directory is at the same level as "off_chain" or "presentation"
# project_root/
#   off_chain/
#     configuration/  <- this script
#   log/              <- target log directory
_PROJECT_ROOT_DIR = _CURRENT_SCRIPT_DIR.parent.parent
_LOG_FILES_DIR: Path = _PROJECT_ROOT_DIR / "log"

# Default name for the application's log file.
_DEFAULT_APP_LOG_FILENAME = "app_main.log" # Changed from logOffChainApp.log for generality

# Full path to the application's primary log file.
_APP_LOG_FILE_PATH: Path = _LOG_FILES_DIR / _DEFAULT_APP_LOG_FILENAME

# Name of the logger to be used by the application.
_APP_LOGGER_NAME = "app_logger"


# --- Custom Exceptions ---
class LoggingConfigError(Exception):
    """Base exception for errors related to logging configuration."""

class LogSettingsFileNotFoundError(LoggingConfigError, FileNotFoundError):
    """Custom exception for when the log_setting.yaml file is not found."""

class InvalidLogSettingsError(LoggingConfigError, ValueError):
    """Custom exception for invalid content or structure in log_setting.yaml."""


def _ensure_log_directory_exists(log_dir_path: Path) -> None:
    """
    Ensures that the specified directory for log files exists.
    Creates it if it does not exist.

    Args:
        log_dir_path: The Path object representing the log directory.

    Raises:
        OSError: If the directory cannot be created.
    """
    try:
        log_dir_path.mkdir(parents=True, exist_ok=True)
        logging.debug("Log directory '%s' ensured to exist.", log_dir_path)
    except OSError as e:
        # Log this as a critical failure if the directory is essential
        logging.critical("Failed to create log directory at '%s': %s", log_dir_path, e, exc_info=True)
        raise # Re-raise the OSError as this could be a fatal setup error


def _clear_log_file_content(log_file_path: Path) -> None:
    """
    Clears the content of the specified log file if it exists.

    Args:
        log_file_path: The Path object representing the log file.
    """
    if log_file_path.exists():
        try:
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.truncate(0)
            logging.debug("Cleared content of log file: %s", log_file_path)
        except IOError as e:
            # Log an error but don't necessarily stop the application
            # as logging to console might still work.
            logging.error(
                "Could not clear log file '%s': %s. Logging to file might be affected.",
                log_file_path, e, exc_info=True
            )


class AppLoggerConfigurator:
    """
    Manages logging configuration using 'log_setting.yaml'.
    Sets up handlers for console and optional file logging.
    """
    # R0903: too-few-public-methods. This class has one main public method,
    # which is acceptable for a dedicated configurator.
    # pylint: disable=too-few-public-methods

    _is_configured: bool = False # Class variable to track if logging is already set up

    @staticmethod
    def setup_logging(
        settings_file: Path = _LOGGING_SETTINGS_YAML_FILE,
        app_log_file: Path = _APP_LOG_FILE_PATH,
        app_logger_name: str = _APP_LOGGER_NAME
    ) -> logging.Logger:
        """
        Sets up the application's logging system.

        1. Ensures the log directory exists.
        2. Clears the main application log file content (if configured to overwrite).
        3. Loads logging settings from the specified YAML configuration file.
        4. Configures handlers for console and file logging based on settings.
        5. Initializes and returns the application-specific logger.

        This method is designed to be called once at application startup.

        Args:
            settings_file: Path to the YAML file with logging settings.
            app_log_file: Path to the main application log file.
            app_logger_name: Name of the logger to configure and return.

        Returns:
            The configured application logger instance.

        Raises:
            LogSettingsFileNotFoundError: If 'log_setting.yaml' is not found.
            InvalidLogSettingsError: If 'log_setting.yaml' has an invalid format or content.
            OSError: If log directories/files cannot be created/accessed.
        """
        if AppLoggerConfigurator._is_configured:
            logging.warning("Logging system already configured. Skipping re-configuration.")
            return logging.getLogger(app_logger_name)

        _ensure_log_directory_exists(_LOG_FILES_DIR) # Ensure base log directory first

        # Load logging settings from YAML
        if not settings_file.is_file():
            err_msg = f"Logging settings YAML file not found: {settings_file}"
            # Use a basicConfig for this critical bootstrap error if logger isn't up yet
            logging.basicConfig(level=logging.ERROR)
            logging.critical(err_msg)
            raise LogSettingsFileNotFoundError(err_msg)

        try:
            with open(settings_file, "r", encoding="utf-8") as f_stream:
                config_dict = yaml.safe_load(f_stream)

            if not isinstance(config_dict, dict) or "logging" not in config_dict:
                err_msg = (
                    "Invalid 'log_setting.yaml': Missing 'logging' top-level key "
                    "or file is not a YAML dictionary."
                )
                raise InvalidLogSettingsError(err_msg)

            log_config_section: Dict[str, Any] = config_dict["logging"]

            # Determine if file logging is enabled from the loaded configuration
            enable_file_logging = log_config_section.get("enable_file_logging", False)

            # Clear the main app log file content if file logging is enabled and
            # if the handler for it is configured (implicitly or explicitly) to overwrite.
            # The actual 'w' mode is set below.
            if enable_file_logging:
                _clear_log_file_content(app_log_file)


            # Dynamically adjust handlers based on 'enable_file_logging'
            active_handlers = ["console"] # Console is assumed to be always desired
            if enable_file_logging:
                active_handlers.append("file")
                # Ensure the 'file' handler (if defined) uses the correct filename and mode
                if "handlers" in log_config_section and "file" in log_config_section["handlers"]:
                    file_handler_config = log_config_section["handlers"]["file"]
                    file_handler_config["filename"] = str(app_log_file) # Ensure path is string
                    file_handler_config["mode"] = "w" # Overwrite mode
                    # Ensure the directory for this specific log file exists
                    _ensure_log_directory_exists(app_log_file.parent)


            # Apply the configured active handlers to relevant loggers
            # (e.g., the main app logger and the root logger)
            if "loggers" in log_config_section and \
               app_logger_name in log_config_section["loggers"]:
                log_config_section["loggers"][app_logger_name]["handlers"] = active_handlers

            if "root" in log_config_section:
                log_config_section["root"]["handlers"] = active_handlers
            else: # Ensure root logger has at least console if not defined
                log_config_section["root"] = {"handlers": ["console"], "level": "WARNING"}


            logging.config.dictConfig(log_config_section)
            AppLoggerConfigurator._is_configured = True

        except yaml.YAMLError as e:
            err_msg = f"Error parsing logging settings YAML file '{settings_file}': {e}"
            logging.basicConfig(level=logging.ERROR) # Fallback logger
            logging.critical(err_msg, exc_info=True)
            raise InvalidLogSettingsError(err_msg) from e
        except KeyError as e:
            err_msg = f"Missing expected key in logging configuration '{settings_file}': {e}"
            logging.basicConfig(level=logging.ERROR)
            logging.critical(err_msg, exc_info=True)
            raise InvalidLogSettingsError(err_msg) from e
        except Exception as e: # Catch any other unexpected error during setup
            err_msg = f"Unexpected error during logging setup from '{settings_file}': {e}"
            logging.basicConfig(level=logging.ERROR)
            logging.critical(err_msg, exc_info=True)
            raise LoggingConfigError(err_msg) from e


        # Retrieve and return the application-specific logger
        app_logger = logging.getLogger(app_logger_name)
        app_logger.info(
            "Logging system initialized. File logging: %s. Log file: %s",
            "ENABLED" if enable_file_logging else "DISABLED",
            app_log_file if enable_file_logging else "N/A"
        )
        return app_logger


# --- Global Logger Instance ---
# Initialize the global logger instance for the application.
# This is done once when the module is imported.

# pylint: disable=invalid-name
# 'logger' is a conventional name for a module-level logger instance.
try:
    logger: logging.Logger = AppLoggerConfigurator.setup_logging()
except LoggingConfigError as e:
    # If setup fails critically, provide a fallback basic logger for critical messages.
    logging.basicConfig(
        level=logging.CRITICAL,
        format="CRITICAL_LOG_SETUP_FAILURE: %(asctime)s - %(levelname)s - %(message)s"
    )
    logging.critical(
        "Failed to initialize application logging system: %s. "
        "Subsequent logging may be incomplete or unformatted.", e
    )
    # Create a minimal fallback logger instance so 'logger' is always defined.
    logger = logging.getLogger("fallback_logger")
    logger.addHandler(logging.NullHandler()) # Prevent "No handlers could be found"
# pylint: enable=invalid-name


if __name__ == "__main__":
    # This block allows testing the logging configuration independently.
    # Ensure you have a 'log_setting.yaml' in the same directory.

    # Example 'log_setting.yaml' content:
    """
    # log_setting.yaml
    logging:
      version: 1
      disable_existing_loggers: False
      enable_file_logging: True # Set to true or false to test

      formatters:
        simple:
          format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        detailed:
          format: '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'

      handlers:
        console:
          class: logging.StreamHandler
          level: DEBUG
          formatter: simple
          stream: ext://sys.stdout

        file:
          class: logging.FileHandler
          level: INFO
          formatter: detailed
          # filename will be set by AppLoggerConfigurator based on _APP_LOG_FILE_PATH
          # mode will be set to 'w' by AppLoggerConfigurator
          encoding: utf-8

      loggers:
        app_logger: # This is our _APP_LOGGER_NAME
          level: DEBUG
          handlers: [] # Will be populated by AppLoggerConfigurator
          propagate: no # Do not pass messages to the root logger if handled here

        # Example for other libraries
        # 'another_library_logger':
        #   level: WARNING
        #   handlers: [console]
        #   propagate: no

      root:
        level: WARNING
        handlers: [] # Will be populated by AppLoggerConfigurator
    """

    # The global 'logger' is already initialized when this module is imported.
    # We can just use it for testing.

    print(f"--- Running Logging Configuration Self-Test ---")
    print(f"Log settings YAML file expected at: {_LOGGING_SETTINGS_YAML_FILE}")
    print(f"Application log file expected at: {_APP_LOG_FILE_PATH}")
    print(f"Log directory expected at: {_LOG_FILES_DIR}")


    if not _LOGGING_SETTINGS_YAML_FILE.exists():
        print(f"WARNING: Test requires '{_LOGGING_SETTINGS_YAML_FILE.name}' to be present "
              f"in '{_LOGGING_SETTINGS_YAML_FILE.parent}'. Please create it.")
        # Create a minimal dummy for the test to proceed if it doesn't exist
        minimal_yaml_content = """
logging:
  version: 1
  disable_existing_loggers: False
  enable_file_logging: False
  formatters:
    simple: {format: '%(asctime)s - %(levelname)s - %(message)s'}
  handlers:
    console: {class: logging.StreamHandler, level: DEBUG, formatter: simple, stream: ext://sys.stdout}
  loggers:
    app_logger: {level: DEBUG, handlers: [console], propagate: no}
  root: {level: WARNING, handlers: [console]}
"""
        try:
            with open(_LOGGING_SETTINGS_YAML_FILE, "w", encoding="utf-8") as f_yaml:
                f_yaml.write(minimal_yaml_content)
            print(f"Created a minimal dummy '{_LOGGING_SETTINGS_YAML_FILE.name}' for testing.")
            # Re-run setup if we just created the file (the global logger might be fallback)
            # This is a bit hacky for a self-test; ideally, mock AppLoggerConfigurator.
            print("Re-initializing logger with dummy config...")
            logger = AppLoggerConfigurator.setup_logging() # Re-call
        except Exception as e_dummy:
            print(f"Could not create dummy log_setting.yaml: {e_dummy}")


    # Test logging with the configured logger
    logger.debug("This is a self-test DEBUG message from the app_logger.")
    logger.info("This is a self-test INFO message from the app_logger.")
    logger.warning("This is a self-test WARNING message from the app_logger.")
    logger.error("This is a self-test ERROR message from the app_logger.")
    logger.critical("This is a self-test CRITICAL message from the app_logger.")

    # Test another logger to see root handler behavior
    other_lib_logger = logging.getLogger("another.library")
    other_lib_logger.warning("This is a WARNING from 'another.library' (should use root handlers).")

    if _APP_LOG_FILE_PATH.exists():
        print(f"Log file content of '{_APP_LOG_FILE_PATH}':")
        try:
            with open(_APP_LOG_FILE_PATH, "r", encoding="utf-8") as f_log:
                print(f_log.read())
        except Exception as e_read:
            print(f"Could not read log file: {e_read}")
    else:
        print(f"Log file '{_APP_LOG_FILE_PATH}' was not created (check 'enable_file_logging' in YAML).")

    print("--- Logging Configuration Self-Test Finished ---")