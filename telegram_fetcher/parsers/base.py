"""Base classes and interfaces for news detail fetching with async support."""

import asyncio
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol

import aiohttp
from fake_useragent import UserAgent

from telegram_fetcher.config import get_logger

logger = get_logger("news_detail_fetcher")


@dataclass
class NewsItem:
    """Data class for news item."""

    id: int
    date: str
    text: str
    url: Optional[str] = None
    detail: Optional[str] = None
    image_url: Optional[str] = None


class IURLExtractor(Protocol):
    """Interface for URL extraction."""

    def extract(self, text: str) -> Optional[str]:
        """Extract URL from text."""
        ...


class IContentParser(Protocol):
    """Interface for content parsing."""

    def parse(self, html: str) -> str:
        """Parse content from HTML."""
        ...

    async def parse_img_url(self, url: str) -> Optional[str]:
        """Parse image URL from article."""
        ...


class IContentFetcher(Protocol):
    """Interface for async content fetching."""

    async def fetch(self, url: str) -> str:
        """Fetch content from URL."""
        ...


class BaseURLExtractor:
    """Base URL extractor with common logic."""

    def __init__(self, url_patterns: Optional[list] = None):
        self.url_patterns = url_patterns or [
            r"https?://[^\s\*]+",
        ]

    def extract(self, text: str) -> Optional[str]:
        """Extract first URL from text."""
        if not text:
            return None

        cleaned_text = re.sub(r"\*+", "", text)

        for pattern in self.url_patterns:
            urls = re.findall(pattern, cleaned_text)
            if urls:
                url: str = urls[0]
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                return url

        return None


class BaseContentParser(ABC):
    """Base abstract parser - each site implements its own logic."""

    def __init__(self, fetcher: IContentFetcher):
        self.fetcher = fetcher
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def parse(self, url: str) -> str:
        """Parse content from URL - implement per site."""
        pass


class AsyncContentFetcher:
    """Async content fetcher using aiohttp."""

    def __init__(
        self, timeout: int = 15, max_retries: int = 2, delay: float = 0.5
    ):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.delay = delay
        self.ua = UserAgent()
        self.session = None

    def _get_headers(self) -> dict:
        """Get HTTP headers."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
        }

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout, headers=self._get_headers()
            )

    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, url: str) -> str:
        """Fetch content from URL with retry logic."""
        await self._ensure_session()

        for attempt in range(self.max_retries + 1):
            try:
                await asyncio.sleep(self.delay)

                headers = {"User-Agent": self.ua.random}

                if self.session is None:
                    return "Error: Session not initialized"

                async with self.session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    html_content: str = await response.text()

                    if len(html_content) < 100:
                        return (
                            f"Invalid content "
                            f"(length: {len(html_content)})"
                        )

                    return html_content

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Timeout on {url}, "
                        f"retry {attempt + 1}/{self.max_retries}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                return "Error: Request timeout"

            except aiohttp.ClientError as e:
                if attempt < self.max_retries:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"Client error on {url}, "
                        f"retry {attempt + 1}/{self.max_retries}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                return f"Error fetching URL: {str(e)}"

            except Exception as e:
                logger.error(
                    f"✗ Unexpected error fetching {url}: {e}", exc_info=True
                )
                return f"Unexpected error: {str(e)}"

        logger.error(
            f"✗ Failed to fetch {url} after "
            f"{self.max_retries + 1} attempts"
        )
        return "Failed to fetch content after all retries"


class SiteProcessor:
    """Generic processor using dependency injection."""

    def __init__(
        self, url_extractor: IURLExtractor, content_parser: IContentParser
    ):
        self.url_extractor = url_extractor
        self.content_parser = content_parser
        self.logger = get_logger(self.__class__.__name__)

    async def process_item(self, item: NewsItem) -> NewsItem:
        """Process single news item asynchronously."""
        if not item.url:
            item.url = self.url_extractor.extract(item.text)
            if not item.url:
                item.detail = "No URL found"
                return item

        item.detail = await self.content_parser.parse(item.url)  # type: ignore[misc]
        item.image_url = await self.content_parser.parse_img_url(item.url)  # type: ignore[misc]
        return item
