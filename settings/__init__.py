
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

SETTINGS_MODULE = os.getenv('settings', 'local').lower()

if SETTINGS_MODULE == 'prod':
    from .prod import *
else:
    from .local import *

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