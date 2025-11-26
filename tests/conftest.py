"""
Pytest configuration and shared fixtures.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


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
def stop_date():
    """Stop date for filtering."""
    return datetime(2025, 11, 23, tzinfo=timezone.utc)
