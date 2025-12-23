"""Base classes and protocols for Telegram message collection."""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Protocol

from telethon import TelegramClient

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    """Data class for telegram message structure."""

    id: int
    date: Optional[str]
    text: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class IDateFilter(Protocol):
    """Interface for date filtering."""

    def should_stop(self, message_date: datetime) -> bool:
        """Check if collection should stop based on date."""
        ...


class IMessageWriter(Protocol):
    """Interface for writing messages."""

    def add(self, message: TelegramMessage) -> None:
        """Add message to storage."""
        ...

    def save(self) -> int:
        """Save collected messages."""
        ...


class IMessageCollector(Protocol):
    """Interface for message collection."""

    async def collect(
        self, channel_url: str, stop_date: datetime, output_file: str
    ) -> int:
        """Collect messages from channel."""
        ...


class DateFilter:
    """Check if message date is within range."""

    def __init__(self, stop_date: datetime):
        self.stop_date = stop_date

    def should_stop(self, message_date: datetime) -> bool:
        """Return True if we should stop collecting."""
        if not message_date:
            return False

        if message_date.tzinfo is None:
            message_date = message_date.replace(tzinfo=timezone.utc)

        return message_date <= self.stop_date


class JSONWriter:
    """Write messages to JSON file."""

    def __init__(self, filename: str):
        self.filename = filename
        self.messages: list[dict] = []

    def add(self, message: TelegramMessage) -> None:
        """Add message to collection."""
        self.messages.append(message.to_dict())
        logger.info(
            f"Added: ID {message.id}, " f"Text: {self._preview(message.text)}"
        )

    def save(self) -> int:
        """Save all messages to file."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

        count = len(self.messages)
        logger.info(f"Saved {count} messages to {self.filename}")
        return count

    @staticmethod
    def _preview(text: Optional[str], max_len: int = 50) -> str:
        """Get text preview."""
        if not text:
            return "No text"
        return (text[:max_len] + "...") if len(text) > max_len else text


class TelegramCollector:
    """Collect messages from Telegram channel."""

    def __init__(self, api_id: str, api_hash: str):
        self.client = TelegramClient("session", api_id, api_hash)

    async def collect(
        self, channel_url: str, stop_date: datetime, output_file: str
    ) -> int:
        """Collect messages from channel until stop_date."""
        date_filter = DateFilter(stop_date)
        writer = JSONWriter(output_file)

        logger.info(f"Connecting to {channel_url}")

        async with self.client:
            channel = await self.client.get_entity(channel_url)

            async for msg in self.client.iter_messages(channel, limit=None):
                if date_filter.should_stop(msg.date):
                    logger.info("Reached stop date")
                    break

                telegram_msg = TelegramMessage(
                    id=msg.id,
                    date=(msg.date.isoformat() if msg.date else None),
                    text=msg.text,
                )
                writer.add(telegram_msg)

        return writer.save()


class BaseCollectionService(ABC):
    """Base class for collection services."""

    def __init__(self, collector: IMessageCollector):
        self.collector = collector

    @abstractmethod
    async def collect_all(self) -> Dict[str, int]:
        """Collect from all sources."""
        pass

    def _log_result(self, name: str, count: int) -> None:
        """Log collection result."""
        status = "Done" if count > 0 else "No new messages"
        logger.info(f"{status} {name}: {count} messages")
