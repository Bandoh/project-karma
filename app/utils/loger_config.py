# logger_config.py
import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Set the default logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str):
    """
    Returns a logger instance with the specified name.
    """
    return logging.getLogger(name)
