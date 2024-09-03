import logging
import configparser
import os
from logging.handlers import RotatingFileHandler

config = configparser.ConfigParser()

def load_config(config_path='config.ini'):
    """Loads the configuration from a config file."""
    try:
        config.read(config_path)
        return config
    except configparser.Error as e:
        logging.error(f"Error reading config.ini: {e}")
        raise

def setup_logging(log_file='video_processing.log'):
    """Set up logging configuration."""
    log_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[log_handler])

def ensure_directory(directory):
    """Ensures that a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.debug(f"Directory exists: {directory}")