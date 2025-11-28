"""Data loaders for various sources."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from settings import get_logger

logger = get_logger("data_loaders")


class BaseDataLoader(ABC):
    """Abstract base class for data loaders."""

    @abstractmethod
    def load(self, source: str) -> list[dict[str, Any]]:
        """Load data from source.

        Args:
            source: Path or identifier of data source

        Returns:
            List of raw data dictionaries

        Raises:
            FileNotFoundError: If source file not found
            ValueError: If data format is invalid
        """
        pass


class JSONFileLoader(BaseDataLoader):
    """Load data from JSON files."""

    def load(self, source: str) -> list[dict[str, Any]]:
        """Load data from JSON file.

        Args:
            source: Path to JSON file

        Returns:
            List of data dictionaries

        Raises:
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        logger.info(f"Loading data from {source}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            logger.info(f"Loaded {len(data)} items from {source}")
            return data

        logger.info(f"Loaded single item from {source}")
        return [data]


class TelegramJSONLoader(JSONFileLoader):
    """Load and validate Telegram message data from JSON."""

    def load(self, source: str) -> list[dict[str, Any]]:
        """Load and validate Telegram data.

        Args:
            source: Path to Telegram JSON file

        Returns:
            List of validated Telegram messages (items without text/detail are skipped)
        """
        data = super().load(source)

        valid_items = []
        skipped_count = 0

        for idx, item in enumerate(data):
            if not item.get("text") and not item.get("detail"):
                logger.warning(
                    f"Skipping item {idx}: missing both 'text' and 'detail' fields"
                )
                skipped_count += 1
                continue
            valid_items.append(item)

        logger.info(
            f"Loaded {len(valid_items)} valid Telegram messages "
            f"({skipped_count} items skipped)"
        )
        return valid_items
