"""Text cleaning components using text processors."""

from abc import ABC, abstractmethod

from rag_module.baseclasses.text.pre_processing import (
    azerbaijani_news_processor,
    default_telegram_news_processor,
)
from settings import get_logger

logger = get_logger("text_cleaners")


class BaseTextCleaner(ABC):
    """Abstract base class for text cleaners."""

    @abstractmethod
    def clean(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        pass


class TelegramNewsCleaner(BaseTextCleaner):
    """Clean Telegram news messages using default processor."""

    def __init__(self):
        """Initialize with default Telegram news processor."""
        self.processor = default_telegram_news_processor
        logger.debug("Initialized TelegramNewsCleaner")

    def clean(self, text: str) -> str:
        """Clean Telegram message text.

        Removes markdown, emojis, normalizes whitespace and case.

        Args:
            text: Raw Telegram message text

        Returns:
            Cleaned text ready for processing
        """
        if not text or not text.strip():
            return ""

        cleaned = str(self.processor.process(text))
        logger.debug(f"Cleaned text: {len(text)} -> {len(cleaned)} chars")
        return cleaned


class AzerbaijaniNewsCleaner(BaseTextCleaner):
    """Clean Azerbaijani news with date context support."""

    def __init__(self):
        """Initialize with Azerbaijani news processor."""
        self.processor = azerbaijani_news_processor
        logger.debug("Initialized AzerbaijaniNewsCleaner")

    def clean(self, text: str, context: dict | None = None) -> str:
        """Clean text with optional date context.

        Args:
            text: Raw news text
            context: Optional context with date information

        Returns:
            Cleaned text with optional date prefix
        """
        if not text or not text.strip():
            return ""

        if context:
            cleaned = str(self.processor.process(text, context))
            logger.debug(f"Cleaned with context: {len(text)} chars")
        else:
            cleaned = str(self.processor.process(text, {}))
            logger.debug(f"Cleaned without context: {len(text)} chars")

        return cleaned
