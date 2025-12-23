"""Telegram fetcher configuration."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from logging_config import setup_logging

load_dotenv()
setup_logging()

_DEFAULT_SOURCES = {
    "qafqazinfo": "https://t.me/qafqazinfo",
    "operativ": "https://t.me/operativmm",
}

_ENV_VAR_HELP = (
    "Please create a .env file (see telegram_fetcher/.env.example) "
    "or set {var_name} in your environment."
)


@dataclass
class TelegramFetcherConfig:
    """Telegram fetcher configuration.

    Attributes:
        api_id: Telegram API ID
        api_hash: Telegram API hash
        session_name: Telethon session file name
        data_dir: Directory for data files
        logs_dir: Directory for log files
        sources: Telegram channel sources
        max_messages: Maximum messages per channel
        batch_size: Batch size for fetching
        delay_between_batches: Delay between batches in seconds
        log_level: Logging level
    """

    api_id: int
    api_hash: str
    session_name: str = "session"
    data_dir: Path = Path("./data")
    logs_dir: Path = Path("./logs")
    sources: dict[str, str] | None = None
    max_messages: int = 1000
    batch_size: int = 100
    delay_between_batches: float = 1.0
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "TelegramFetcherConfig":
        """Create config from environment variables.

        Returns:
            TelegramFetcherConfig instance

        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        api_id = cls._get_required_api_id()
        api_hash = cls._get_required_api_hash()

        return cls(
            api_id=api_id,
            api_hash=api_hash,
            session_name=os.getenv("TELEGRAM_SESSION_NAME", "session"),
            data_dir=Path(os.getenv("DATA_DIR", "./data")),
            logs_dir=Path(os.getenv("LOGS_DIR", "./logs")),
            sources=_DEFAULT_SOURCES.copy(),
            max_messages=int(os.getenv("TELEGRAM_MAX_MESSAGES", "1000")),
            batch_size=int(os.getenv("TELEGRAM_BATCH_SIZE", "100")),
            delay_between_batches=float(
                os.getenv("TELEGRAM_DELAY_BETWEEN_BATCHES", "1.0")
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @staticmethod
    def _get_required_api_id() -> int:
        """Get and validate API_ID from environment.

        Returns:
            API ID as integer

        Raises:
            ValueError: If API_ID is missing or invalid
        """
        api_id_str = os.getenv("API_ID")
        if not api_id_str:
            raise ValueError(
                f"API_ID environment variable is required. "
                f"{_ENV_VAR_HELP.format(var_name='API_ID')}"
            )

        try:
            return int(api_id_str)
        except ValueError as e:
            raise ValueError(
                f"API_ID must be a valid integer, got: {api_id_str}"
            ) from e

    @staticmethod
    def _get_required_api_hash() -> str:
        """Get API_HASH from environment.

        Returns:
            API hash string

        Raises:
            ValueError: If API_HASH is missing
        """
        api_hash = os.getenv("API_HASH")
        if not api_hash:
            raise ValueError(
                f"API_HASH environment variable is required. "
                f"{_ENV_VAR_HELP.format(var_name='API_HASH')}"
            )
        return api_hash
