"""Production settings."""

from .base import (
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
