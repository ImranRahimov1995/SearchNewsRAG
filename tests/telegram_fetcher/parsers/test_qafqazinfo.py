"""
Tests for telegram_fetcher/parsers/qafqazinfo.py
"""

import pytest
from aioresponses import aioresponses

from telegram_fetcher.parsers.base import AsyncContentFetcher
from telegram_fetcher.parsers.qafqazinfo import (
    QafqazInfoParser,
    QafqazInfoURLExtractor,
    create_qafqazinfo_processor,
)


class TestQafqazInfoURLExtractor:
    """Tests for QafqazInfoURLExtractor."""

    def test_extract_qafqazinfo_url(self):
        """Test extracting QafqazInfo URL."""
        extractor = QafqazInfoURLExtractor()

        text = "Read more: https://qafqazinfo.az/news/detail/12345"
        url = extractor.extract(text)

        assert url == "https://qafqazinfo.az/news/detail/12345"

    def test_extract_url_without_protocol(self):
        """Test extracting URL without https://."""
        extractor = QafqazInfoURLExtractor()

        text = "Visit qafqazinfo.az/news/12345"
        url = extractor.extract(text)

        assert url.startswith("https://")
        assert "qafqazinfo.az" in url


class TestQafqazInfoParser:
    """Tests for QafqazInfoParser."""

    @pytest.mark.asyncio
    async def test_parse_success(self):
        """Test successful parsing."""
        fetcher = AsyncContentFetcher()
        parser = QafqazInfoParser(fetcher)

        html = """
        <html>
            <div class="panel-body news_text">
                <p>This is a long article content that should be parsed correctly.</p>
                <p>It contains multiple paragraphs with enough text.</p>
            </div>
        </html>
        """

        with aioresponses() as m:
            m.get("https://qafqazinfo.az/news/12345", status=200, body=html)

            result = await parser.parse("https://qafqazinfo.az/news/12345")

            assert "article content" in result
            assert "multiple paragraphs" in result

        await fetcher.close()

    @pytest.mark.asyncio
    async def test_parse_selector_not_found(self):
        """Test when selector not found."""
        fetcher = AsyncContentFetcher()
        parser = QafqazInfoParser(fetcher)

        html = """
        <html>
            <body>
                <p>No matching selector here. Adding more text to make it longer than 100 characters.</p>
                <p>This ensures the fetcher doesn't return "Invalid content" error.</p>
            </body>
        </html>
        """

        with aioresponses() as m:
            m.get("https://qafqazinfo.az/news/12345", status=200, body=html)

            result = await parser.parse("https://qafqazinfo.az/news/12345")

            assert "Content not found" in result or "selector" in result

        await fetcher.close()

    @pytest.mark.asyncio
    async def test_parse_short_content(self):
        """Test parsing short content."""
        fetcher = AsyncContentFetcher()
        parser = QafqazInfoParser(fetcher)

        html = """
        <html>
            <div class="panel-body news_text">
                Short
            </div>
        </html>
        """

        with aioresponses() as m:
            m.get("https://qafqazinfo.az/news/12345", status=200, body=html)

            result = await parser.parse("https://qafqazinfo.az/news/12345")

            assert "Short" in result
            assert len(result) <= 50

        await fetcher.close()

    @pytest.mark.asyncio
    async def test_parse_fetch_error(self):
        """Test when fetch fails."""
        fetcher = AsyncContentFetcher(max_retries=0)
        parser = QafqazInfoParser(fetcher)

        with aioresponses() as m:
            m.get("https://qafqazinfo.az/news/12345", status=500)

            result = await parser.parse("https://qafqazinfo.az/news/12345")

            assert "Error" in result or "Failed" in result

        await fetcher.close()


def test_create_qafqazinfo_processor():
    """Test factory function."""
    processor = create_qafqazinfo_processor()

    assert processor is not None
    assert processor.url_extractor is not None
    assert processor.content_parser is not None
