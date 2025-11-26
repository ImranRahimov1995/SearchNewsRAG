import os

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

SETTINGS_MODULE = os.getenv("SETTINGS", "local").lower()

if SETTINGS_MODULE == "prod":
    from .prod import (
        API_HASH,
        API_ID,
        BASE_DIR,
        LOG_DIR,
        RAG_MODULE_DIR,
        SOURCES,
        TELEGRAM_FETCHER_MODULE,
        get_logger,
    )
else:
    from .local import (
        API_HASH,
        API_ID,
        BASE_DIR,
        LOG_DIR,
        RAG_MODULE_DIR,
        SOURCES,
        TELEGRAM_FETCHER_MODULE,
        get_logger,
    )

__all__ = [
    "BASE_DIR",
    "RAG_MODULE_DIR",
    "TELEGRAM_FETCHER_MODULE",
    "LOG_DIR",
    "get_logger",
    "API_ID",
    "API_HASH",
    "SOURCES",
]
