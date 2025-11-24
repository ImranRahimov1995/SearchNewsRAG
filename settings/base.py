import os
import pathlib
import logging
    
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

## BASE SETTINGS

BASE_DIR = pathlib.Path(__file__).resolve().parent
RAG_MODULE_DIR = BASE_DIR / "rag_module"
TELEGRAM_FETCHER_MODULE = BASE_DIR / "telegram_fetcher_module"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(file_name: str) -> logging.Logger:
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)

    log_path = LOG_DIR / f"{file_name}.log"

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        stream_added = any(
            isinstance(h, logging.StreamHandler) for h in logger.handlers
        )
        if not stream_added:
            logger.addHandler(logging.StreamHandler())

    return logger


## TELEGRAM SETTINGS
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
