import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from ..config import Config

# Ensure logs dir exists
os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))

    # Formatter: [2025-06-12 14:30:00] [INFO] [patch_watcher] Nova versão...
    formatter = logging.Formatter(
        f'[%(asctime)s] [%(levelname)s] [{name}] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File Handler with Daily Rotation
    file_handler = TimedRotatingFileHandler(Config.LOG_FILE, when="midnight", interval=1, backupCount=7)
    file_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Root logger
root_logger = setup_logger("root")
