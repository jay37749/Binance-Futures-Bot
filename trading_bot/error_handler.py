# error_handler.py

import logging
import os
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Error log file path
ERROR_LOG_FILE = os.path.join(os.path.dirname(__file__), "error_log.txt")

# Retry settings
RETRY_DELAY = 5  # Seconds
MAX_RETRIES = 3

# Generic error handler function
def handle_error(error, error_type="general", critical=False, log_to_file=True, recoverable=False):
    """
    Logs and handles errors, with optional persistence to a log file and retry mechanism for recoverable errors.

    :param error: Exception or error message to be logged.
    :param error_type: Type of error (e.g., 'API', 'Data', 'Strategy').
    :param critical: Boolean indicating whether the error is critical and requires halting the bot.
    :param log_to_file: Boolean indicating whether to log the error to a file.
    :param recoverable: Boolean indicating whether the error is recoverable and should be retried.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    error_message = f"{timestamp} | Error Type: {error_type} | Error: {str(error)}"

    if recoverable:
        logger.warning(f"Recoverable Error: {error_message}. Retrying...")
        if log_to_file:
            _log_error_to_file(error_message)
        _retry_action(lambda: _recover_action(), error_message)
    elif critical:
        logger.critical(f"CRITICAL ERROR: {error_message}. Shutting down the bot.")
        if log_to_file:
            _log_error_to_file(error_message)
        raise SystemExit("Critical Error - Shutting down.")
    else:
        logger.error(f"Non-critical Error: {error_message}. Continuing operation.")
        if log_to_file:
            _log_error_to_file(error_message)

# Retry mechanism for recoverable errors
def _retry_action(action, error_message):
    """
    Attempts to retry a recoverable action up to MAX_RETRIES times.

    :param action: The action to attempt.
    :param error_message: The error message to log if retries fail.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            action()
            return
        except Exception as e:
            retries += 1
            logger.warning(f"Retry {retries}/{MAX_RETRIES} failed for action. Error: {e}")
            time.sleep(RETRY_DELAY)
    logger.error(f"Action failed after {MAX_RETRIES} retries. Error: {error_message}")

# Recovery action (dummy implementation for demonstration purposes)
def _recover_action():
    """
    Placeholder for recoverable actions (e.g., reconnecting to API or retrying a data fetch).
    """
    logger.info("Recovering action...")
    # Add specific recovery logic here
    raise NotImplementedError("Recovery action not implemented.")

# Logs the error message to a file for persistent tracking
def _log_error_to_file(error_message):
    """
    Logs the error message to a file for persistent tracking.

    :param error_message: The error message to log.
    """
    try:
        with open(ERROR_LOG_FILE, "a") as log_file:
            log_file.write(error_message + "\n")
    except Exception as e:
        logger.error(f"Failed to write to error log file: {e}")

# Example usage of the error handler
if __name__ == "__main__":
    try:
        # Simulate a recoverable error
        raise TimeoutError("Sample recoverable API timeout error")
    except Exception as e:
        handle_error(e, error_type="API", critical=False, recoverable=True)

    try:
        # Simulate a non-critical error
        raise ValueError("Sample non-critical error")
    except Exception as e:
        handle_error(e, error_type="Sample", critical=False)

    try:
        # Simulate a critical error
        raise RuntimeError("Sample critical error")
    except Exception as e:
        handle_error(e, error_type="Sample", critical=True)