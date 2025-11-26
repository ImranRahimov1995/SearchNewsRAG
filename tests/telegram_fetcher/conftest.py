"""
Pytest fixtures for telegram_fetcher tests.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def sample_news_item():
    """Sample news item for testing."""
    return {
        "id": 12345,
        "date": "2025-11-24T10:30:00+00:00",
        "text": "Breaking news from https://qafqazinfo.az/news/12345",
    }


@pytest.fixture
def sample_news_list():
    """Sample list of news items."""
    return [
        {
            "id": 1,
            "date": "2025-11-24T10:00:00+00:00",
            "text": "News 1 https://qafqazinfo.az/news/1",
        },
        {
            "id": 2,
            "date": "2025-11-23T10:00:00+00:00",
            "text": "News 2 https://qafqazinfo.az/news/2",
        },
        {
            "id": 3,
            "date": "2025-11-22T10:00:00+00:00",
            "text": "News 3 https://qafqazinfo.az/news/3",
        },
    ]


@pytest.fixture
def sample_html_content():
    """Sample HTML content for parsing."""
    return """
    <html>
        <body>
            <div class="panel-body news_text">
                <p>This is the main article content.</p>
                <p>It contains multiple paragraphs.</p>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def telegram_api_credentials():
    """Telegram API credentials for testing."""
    return {"api_id": 12345, "api_hash": "test_api_hash"}


@pytest.fixture
def mock_telegram_message():
    """Create a single mock Telegram message."""
    msg = Mock()
    msg.id = 1
    msg.date = datetime(2025, 11, 24, 10, 0, 0, tzinfo=timezone.utc)
    msg.text = "Test message"
    return msg


@pytest.fixture
def create_mock_message():
    """Factory fixture for creating custom mock messages."""

    def _create_message(msg_id: int, date: datetime = None, text: str = None):
        msg = Mock()
        msg.id = msg_id
        msg.date = date
        msg.text = text
        return msg

    return _create_message


@pytest.fixture
def mock_telegram_client():
    """Factory fixture for creating mock Telegram client."""

    async def _create_client(messages=None):
        """
        Create mock client with given messages.

        Args:
            messages: List of mock messages to iterate over

        Returns:
            Mock async client
        """
        if messages is None:
            messages = []

        mock_client = AsyncMock()
        mock_entity = Mock()
        mock_client.get_entity = AsyncMock(return_value=mock_entity)

        # Create async generator for messages
        async def mock_iter():
            for msg in messages:
                yield msg

        mock_client.iter_messages = Mock(return_value=mock_iter())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        return mock_client

    return _create_client


@pytest.fixture
def output_file(temp_dir):
    """Standard output file path for tests."""
    return temp_dir / "output.json"


@pytest.fixture
def stop_date():
    """Create a stop date for testing."""
    return datetime(2025, 11, 23, tzinfo=timezone.utc)


@pytest.fixture
def sources():
    """Create test sources dictionary."""
    return {
        "operativ": "https://t.me/operativ_news",
        "qafqazinfo": "https://t.me/qafqazinfo",
    }


@pytest.fixture
def mock_collector():
    """Create a mock message collector."""
    collector = AsyncMock()
    collector.collect = AsyncMock(return_value=10)
    return collector
