import logging

# Function to set up logging for console output
def setup_console_logger(log_level=logging.INFO):
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Define logging format
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up console handler and apply the format
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # If the logger already has handlers, remove them to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add console handler to the logger
    logger.addHandler(console_handler)

    return logger

logger = setup_console_logger()

logger.info("Logging Started for Transaction  App.")