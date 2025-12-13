from urllib.parse import urljoin

from bs4 import BeautifulSoup

from telegram_fetcher.parsers.base import (
    AsyncContentFetcher,
    BaseContentParser,
    BaseURLExtractor,
    IContentFetcher,
    SiteProcessor,
)


class QafqazInfoURLExtractor(BaseURLExtractor):
    """URL extractor for QafqazInfo."""

    def __init__(self):
        super().__init__(
            url_patterns=[
                r"https?://[^\s\*]+",
                r"(?:https?://)?(?:www\.)?qafqazinfo\.az/[^\s\*]+",
            ]
        )


class QafqazInfoParser(BaseContentParser):
    """QafqazInfo-specific parser.

    Uses simple CSS selector approach.
    """

    def __init__(self, fetcher: IContentFetcher):
        super().__init__(fetcher)
        self.selector = ".panel-body.news_text"
        self.image_selector = ".news .img-responsive"

    async def parse(self, url: str) -> str:
        """Parse QafqazInfo article content."""
        html = await self.fetcher.fetch(url)

        if html.startswith(("Error", "Failed", "Invalid")):
            return html

        # Parse with BeautifulSoup
        try:
            soup = BeautifulSoup(html, "html.parser")
            element = soup.select_one(self.selector)

            if element:
                text = element.get_text(strip=True)

                if len(text) > 50:
                    self.logger.debug(
                        f"Parsed {len(text)} chars from {url[:50]}..."
                    )
                return text

            else:
                self.logger.error(
                    f"Selector '{self.selector}' not found " f"on {url}"
                )
                return "Content not found with selector"

        except Exception as e:
            self.logger.error(
                f"Error parsing HTML from {url}: {str(e)}", exc_info=True
            )
            return f"Error parsing HTML: {str(e)}"

    async def parse_img_url(self, url: str) -> str | None:
        """Parse and return image URL from QafqazInfo article.

        Args:
            url: Article URL

        Returns:
            Absolute image URL or None if not found
        """
        html = await self.fetcher.fetch(url)

        if html.startswith(("Error", "Failed", "Invalid")):
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")
            image_element = soup.select_one(self.image_selector)

            if not image_element:
                self.logger.debug(f"No image found for {url}")
                return None

            src = image_element.get("src")
            if not src or not isinstance(src, str):
                return None

            if src.startswith(("http://", "https://")):
                return src

            return urljoin(url, src)

        except Exception as e:
            self.logger.error(
                f"Error extracting image from {url}: {str(e)}", exc_info=True
            )
            return None


def create_qafqazinfo_processor() -> SiteProcessor:
    """Factory function to create QafqazInfo processor."""
    url_extractor = QafqazInfoURLExtractor()
    fetcher = AsyncContentFetcher(timeout=15, max_retries=2, delay=0.3)
    parser = QafqazInfoParser(fetcher)

    return SiteProcessor(url_extractor, parser)  # type: ignore[arg-type]
