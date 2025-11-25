"""
Tests for telegram_fetcher/base.py
"""

import json
from datetime import datetime, timezone

import pytest

from telegram_fetcher.base import (
    DateFilter,
    JSONWriter,
    TelegramCollector,
    TelegramMessage,
)


class TestTelegramMessage:
    """Tests for TelegramMessage dataclass."""

    def test_create_message(self):
        """Test creating a message."""
        msg = TelegramMessage(
            id=123, date="2025-11-24T10:00:00+00:00", text="Test message"
        )

        assert msg.id == 123
        assert msg.text == "Test message"

    def test_to_dict(self):
        """Test converting message to dict."""
        msg = TelegramMessage(
            id=123, date="2025-11-24T10:00:00+00:00", text="Test"
        )

        result = msg.to_dict()

        assert result["id"] == 123
        assert result["text"] == "Test"
        assert result["date"] == "2025-11-24T10:00:00+00:00"


class TestDateFilter:
    """Tests for DateFilter class."""

    def test_should_stop_before_stop_date(self, stop_date):
        """Test stopping before stop date."""
        date_filter = DateFilter(stop_date)

        old_date = datetime(2025, 11, 22, tzinfo=timezone.utc)

        assert date_filter.should_stop(old_date) is True

    def test_should_not_stop_after_stop_date(self, stop_date):
        """Test not stopping after stop date."""
        date_filter = DateFilter(stop_date)

        new_date = datetime(2025, 11, 25, tzinfo=timezone.utc)

        assert date_filter.should_stop(new_date) is False

    def test_should_stop_exact_stop_date(self, stop_date):
        """Test stopping at exact stop date."""
        date_filter = DateFilter(stop_date)

        assert date_filter.should_stop(stop_date) is True

    def test_handle_none_date(self, stop_date):
        """Test handling None date."""
        date_filter = DateFilter(stop_date)

        assert date_filter.should_stop(None) is False

    def test_handle_naive_datetime(self, stop_date):
        """Test handling naive datetime (no timezone)."""
        date_filter = DateFilter(stop_date)

        naive_date = datetime(2025, 11, 22, 10, 0, 0)

        assert date_filter.should_stop(naive_date) is True


class TestJSONWriter:
    """Tests for JSONWriter class."""

    def test_add_message(self, temp_dir, sample_news_item):
        """Test adding message."""
        output_file = temp_dir / "test.json"
        writer = JSONWriter(str(output_file))

        msg = TelegramMessage(**sample_news_item)
        writer.add(msg)

        assert len(writer.messages) == 1
        assert writer.messages[0]["id"] == 12345

    def test_save_to_file(self, temp_dir, sample_news_item):
        """Test saving messages to file."""
        output_file = temp_dir / "test.json"
        writer = JSONWriter(str(output_file))

        msg = TelegramMessage(**sample_news_item)
        writer.add(msg)

        count = writer.save()

        assert count == 1
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["id"] == 12345

    def test_save_multiple_messages(self, temp_dir, sample_news_list):
        """Test saving multiple messages."""
        output_file = temp_dir / "test.json"
        writer = JSONWriter(str(output_file))

        for item in sample_news_list:
            msg = TelegramMessage(
                id=item["id"], date=item["date"], text=item["text"]
            )
            writer.add(msg)

        count = writer.save()

        assert count == 3

    def test_preview_long_text(self):
        """Test text preview for long text."""
        writer = JSONWriter("dummy.json")

        long_text = "a" * 100
        preview = writer._preview(long_text, max_len=50)

        assert len(preview) == 53
        assert preview.endswith("...")

    def test_preview_short_text(self):
        """Test text preview for short text."""
        writer = JSONWriter("dummy.json")

        short_text = "Short text"
        preview = writer._preview(short_text, max_len=50)

        assert preview == "Short text"

    def test_preview_none_text(self):
        """Test text preview for None."""
        writer = JSONWriter("dummy.json")

        preview = writer._preview(None)

        assert preview == "No text"


class TestTelegramCollector:
    """Tests for TelegramCollector class."""

    @pytest.mark.asyncio
    async def test_collect_basic(
        self,
        telegram_api_credentials,
        mock_telegram_client,
        create_mock_message,
        output_file,
        stop_date,
    ):
        """Test basic message collection."""
        msg = create_mock_message(
            msg_id=1,
            date=datetime(2025, 11, 24, 10, 0, 0, tzinfo=timezone.utc),
            text="Test message",
        )

        collector = TelegramCollector(**telegram_api_credentials)
        collector.client = await mock_telegram_client([msg])

        count = await collector.collect(
            channel_url="https://t.me/test_channel",
            stop_date=stop_date,
            output_file=str(output_file),
        )

        assert count == 1
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["text"] == "Test message"

    @pytest.mark.asyncio
    async def test_collect_stops_at_date(
        self,
        telegram_api_credentials,
        mock_telegram_client,
        create_mock_message,
        output_file,
        stop_date,
    ):
        """Test that collection stops at stop_date."""
        messages = [
            create_mock_message(
                3, datetime(2025, 11, 25, tzinfo=timezone.utc), "New 1"
            ),
            create_mock_message(
                2, datetime(2025, 11, 24, tzinfo=timezone.utc), "New 2"
            ),
            create_mock_message(
                1, datetime(2025, 11, 21, tzinfo=timezone.utc), "Old"
            ),
        ]

        collector = TelegramCollector(**telegram_api_credentials)
        collector.client = await mock_telegram_client(messages)

        count = await collector.collect(
            channel_url="https://t.me/test",
            stop_date=stop_date,
            output_file=str(output_file),
        )

        assert count == 2

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["id"] == 3
        assert data[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_collect_empty_channel(
        self,
        telegram_api_credentials,
        mock_telegram_client,
        output_file,
        stop_date,
    ):
        collector = TelegramCollector(**telegram_api_credentials)
        collector.client = await mock_telegram_client([])

        count = await collector.collect(
            channel_url="https://t.me/empty",
            stop_date=stop_date,
            output_file=str(output_file),
        )

        assert count == 0
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_collect_handles_none_date(
        self,
        telegram_api_credentials,
        mock_telegram_client,
        create_mock_message,
        output_file,
        stop_date,
    ):
        """Test handling messages with None date."""
        msg = create_mock_message(
            msg_id=1, date=None, text="Message without date"
        )

        collector = TelegramCollector(**telegram_api_credentials)
        collector.client = await mock_telegram_client([msg])

        count = await collector.collect(
            channel_url="https://t.me/test",
            stop_date=stop_date,
            output_file=str(output_file),
        )

        assert count == 1

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data[0]["id"] == 1
        assert data[0]["date"] is None

    @pytest.mark.asyncio
    async def test_collect_handles_none_text(
        self,
        telegram_api_credentials,
        mock_telegram_client,
        create_mock_message,
        output_file,
        stop_date,
    ):
        """Test handling messages with None text."""
        msg = create_mock_message(
            msg_id=1,
            date=datetime(2025, 11, 24, tzinfo=timezone.utc),
            text=None,
        )

        collector = TelegramCollector(**telegram_api_credentials)
        collector.client = await mock_telegram_client([msg])

        count = await collector.collect(
            channel_url="https://t.me/test",
            stop_date=stop_date,
            output_file=str(output_file),
        )

        assert count == 1

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data[0]["id"] == 1
        assert data[0]["text"] is None
