"""
Tests for telegram_fetcher/parsers/base.py
"""

import pytest
from aioresponses import aioresponses

from telegram_fetcher.parsers.base import (
    AsyncContentFetcher,
    BaseURLExtractor,
    NewsItem,
)


class TestBaseURLExtractor:
    """Tests for BaseURLExtractor."""

    def test_extract_simple_url(self):
        """Test extracting simple URL."""
        extractor = BaseURLExtractor()

        text = "Check this out: https://example.com/article"
        url = extractor.extract(text)

        assert url == "https://example.com/article"

    def test_extract_url_with_markdown(self):
        """Test extracting URL with markdown formatting."""
        extractor = BaseURLExtractor()

        text = "**Breaking**: https://example.com/news"
        url = extractor.extract(text)

        assert url == "https://example.com/news"

    def test_extract_url_without_protocol(self):
        """Test extracting URL without protocol."""
        extractor = BaseURLExtractor(url_patterns=[r"example\.com/[^\s]+"])

        text = "Visit example.com/article"
        url = extractor.extract(text)

        assert url == "https://example.com/article"

    def test_extract_no_url(self):
        """Test when no URL present."""
        extractor = BaseURLExtractor()

        text = "No URL in this text"
        url = extractor.extract(text)

        assert url is None

    def test_extract_empty_text(self):
        """Test with empty text."""
        extractor = BaseURLExtractor()

        url = extractor.extract("")

        assert url is None

    def test_extract_none_text(self):
        """Test with None text."""
        extractor = BaseURLExtractor()

        url = extractor.extract(None)

        assert url is None


class TestAsyncContentFetcher:
    """Tests for AsyncContentFetcher."""

    @pytest.mark.asyncio
    async def test_fetch_success(self, sample_html_content):
        """Test successful fetch."""
        fetcher = AsyncContentFetcher()

        with aioresponses() as m:
            m.get(
                "https://example.com/article",
                status=200,
                body=sample_html_content,
            )

            result = await fetcher.fetch("https://example.com/article")

            assert len(result) > 100
            assert "article content" in result

        await fetcher.close()

    @pytest.mark.asyncio
    async def test_fetch_404(self):
        """Test 404 error handling."""
        fetcher = AsyncContentFetcher(max_retries=0)

        with aioresponses() as m:
            m.get("https://example.com/notfound", status=404)

            result = await fetcher.fetch("https://example.com/notfound")

            assert result == ""

        await fetcher.close()

    @pytest.mark.asyncio
    async def test_fetch_invalid_content(self):
        """Test invalid content (too short)."""
        fetcher = AsyncContentFetcher()

        with aioresponses() as m:
            m.get("https://example.com/short", status=200, body="short")

            result = await fetcher.fetch("https://example.com/short")

            assert "Invalid content" in result

        await fetcher.close()


class TestNewsItem:
    """Tests for NewsItem dataclass."""

    def test_create_news_item(self):
        """Test creating NewsItem."""
        item = NewsItem(
            id=123,
            date="2025-01-01",
            text="Test news",
            url="https://example.com",
            detail="Full content",
        )

        assert item.id == 123
        assert item.date == "2025-01-01"
        assert item.text == "Test news"
        assert item.url == "https://example.com"
        assert item.detail == "Full content"

    def test_news_item_defaults(self):
        """Test NewsItem with default values."""
        item = NewsItem(id=123, date="2025-01-01", text="Test")

        assert item.url is None
        assert item.detail is None
