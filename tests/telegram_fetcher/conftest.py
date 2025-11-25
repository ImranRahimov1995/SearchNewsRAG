"""
Pytest fixtures for telegram_fetcher tests.
"""

import pytest

from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def telegram_api_credentials():
    """Telegram API credentials for testing."""
    return {
        'api_id': 12345,
        'api_hash': 'test_api_hash'
    }


@pytest.fixture
def mock_telegram_message():
    """Create a single mock Telegram message."""
    msg = Mock()
    msg.id = 1
    msg.date = datetime(
        2025, 11, 24, 10, 0, 0,
        tzinfo=timezone.utc
    )
    msg.text = "Test message"
    return msg


@pytest.fixture
def create_mock_message():
    """Factory fixture for creating custom mock messages."""
    def _create_message(
        msg_id: int,
        date: datetime = None,
        text: str = None
    ):
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
        mock_client.get_entity = AsyncMock(
            return_value=mock_entity
        )
        
        # Create async generator for messages
        async def mock_iter():
            for msg in messages:
                yield msg
        
        mock_client.iter_messages = Mock(
            return_value=mock_iter()
        )
        mock_client.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        return mock_client
    
    return _create_client


@pytest.fixture
def output_file(temp_dir):
    """Standard output file path for tests."""
    return temp_dir / "output.json"
