"""Data loaders for various sources."""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


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
    """Load and validate Telegram message data from JSON.

    Supports optional data slicing for processing subsets of data.
    """

    def __init__(
        self, start_index: int | None = None, end_index: int | None = None
    ):
        """Initialize Telegram JSON loader.

        Args:
            start_index: Start index for data slicing (inclusive)
            end_index: End index for data slicing (exclusive)
        """
        self.start_index = start_index
        self.end_index = end_index

    def load(self, source: str) -> list[dict[str, Any]]:
        """Load and validate Telegram data.

        Args:
            source: Path to Telegram JSON file

        Returns:
            List of validated Telegram messages
            (items without text/detail are skipped)
        """
        data = super().load(source)

        if self.start_index is not None or self.end_index is not None:
            start = self.start_index or 0
            end = self.end_index
            original_count = len(data)
            data = data[start:end]
            logger.info(
                f"Applied slicing [{start}:{end}]: "
                f"{original_count} -> {len(data)} items"
            )

        valid_items = []
        skipped_count = 0

        for idx, item in enumerate(data):
            if not item.get("text") and not item.get("detail"):
                logger.warning(
                    f"Skipping item {idx}: "
                    f"missing both 'text' and 'detail' fields"
                )
                skipped_count += 1
                continue
            valid_items.append(item)

        logger.info(
            f"Loaded {len(valid_items)} valid Telegram messages "
            f"({skipped_count} items skipped)"
        )
        return valid_items
