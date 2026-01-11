import logging
import os
from config import Config

def setup_logger():

    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('eu_migration_api')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    if logger.handlers:
        return logger
    
    file_handler = logging.FileHandler(Config.LOG_FILE)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    return logging.getLogger(f'eu_migration_api.{name}')
