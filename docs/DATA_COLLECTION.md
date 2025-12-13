# Data Collection Guide

## Overview

Data collection system for fetching news from Telegram channels and extracting full article content from websites. Consists of two main components:

1. **Telegram Fetcher** - Collects messages from Telegram channels
2. **Content Parser** - Extracts full article text from URLs

## Telegram Fetcher

### Features

- Configurable date filtering
- JSON output with automatic directory creation
- Support for multiple channels
- Rate limiting and error handling

### Usage

**Collect all sources**:
```bash
python -m telegram_fetcher --stop-date 2025-11-23
```

**Specific source**:
```bash
python -m telegram_fetcher --source qafqazinfo --stop-date 2024-01-01
```

**Custom output directory**:
```bash
python -m telegram_fetcher --stop-date 2025-11-23 --output-dir ./datanew
```

### Output Format

```json
[
  {
    "id": 12345,
    "date": "2024-11-24T10:30:00+00:00",
    "text": "Breaking news content...",
    "url": "https://qafqazinfo.az/news/detail/12345"
  }
]
```

### Architecture

- `base.py` - Core abstractions and collectors
- `services.py` - NewsCollectionService implementation
- `__main__.py` - CLI entry point

## Content Parser

### Features

- Async HTTP requests with aiohttp (2-3x faster than threading)
- Configurable concurrent request limit (semaphore)
- Site-specific parsers (easily extensible)
- Smart retry logic with exponential backoff
- Comprehensive error logging

### Usage

**Parse article details**:
```bash
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json
```

**Save to different file**:
```bash
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json \
  --output datanew/qafqazinfo_full.json
```

**Overwrite existing details**:
```bash
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json \
  --overwrite
```

**Increase concurrency**:
```bash
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json \
  --concurrent 100
```

### Output Format

```json
[
  {
    "id": 12345,
    "date": "2024-11-24T10:30:00+00:00",
    "text": "Breaking news...",
    "url": "https://qafqazinfo.az/news/detail/12345",
    "detail": "Full article content extracted from webpage...",
    "image_url": "https://qafqazinfo.az/uploads/1234567890/image.jpg"
  }
]
```

**Note**: `image_url` field is automatically extracted from article pages when available.

### Architecture

- `parsers/base.py` - Abstract interfaces and base implementations
  - `IURLExtractor` - Extract URLs from text
  - `IContentFetcher` - Async HTTP fetching
  - `IContentParser` - Parse HTML content and image URLs
  - `BaseContentParser` - Base parser class
  - `NewsItem` - Data class with id, date, text, url, detail, image_url
- `parsers/qafqazinfo.py` - Site-specific parser implementations
  - `parse()` - Extract article text
  - `parse_img_url()` - Extract image URL from article
- `parsers/__main__.py` - CLI for batch processing

## Adding New Parser

To add support for a new news site:

1. **Create parser class**:
```python
# telegram_fetcher/parsers/mysite.py
from .base import BaseContentParser, IURLExtractor

class MySiteURLExtractor(IURLExtractor):
    def extract(self, text: str) -> str | None:
        # Extract URL from Telegram message
        import re
        match = re.search(r'https://mysite\.az/[\w/-]+', text)
        return match.group(0) if match else None

class MySiteParser(BaseContentParser):
    def __init__(self):
        from .base import AsyncContentFetcher
        super().__init__(
            url_extractor=MySiteURLExtractor(),
            fetcher=AsyncContentFetcher(),
            content_selector=".article-content"  # CSS selector
        )
        self.image_selector = ".article-image img"  # Image selector

    def parse(self, html: str) -> str:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        content = soup.select_one(self.content_selector)
        return content.get_text(strip=True) if content else ""

    async def parse_img_url(self, url: str) -> str | None:
        """Extract image URL from article page."""
        html = await self.fetcher.fetch(url)
        if html.startswith(("Error", "Failed")):
            return None

        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        soup = BeautifulSoup(html, "html.parser")
        img = soup.select_one(self.image_selector)
        if not img:
            return None

        src = img.get("src")
        if not src or not isinstance(src, str):
            return None

        return urljoin(url, src) if not src.startswith("http") else src
```

2. **Register in CLI**:
```python
# telegram_fetcher/parsers/__main__.py
from .mysite import MySiteParser

PARSERS = {
    "qafqazinfo": QafqazInfoParser,
    "mysite": MySiteParser,  # Add here
}
```

3. **Use**:
```bash
python -m telegram_fetcher.parsers --site mysite --input data/mysite.json
```

## Complete Workflow

**Step 1: Collect messages from Telegram**:
```bash
python -m telegram_fetcher --stop-date 2025-11-23 --output-dir ./data
# Output: data/qafqazinfo.json, data/operativ.json
```

**Step 2: Extract full article content**:
```bash
python -m telegram_fetcher.parsers --site qafqazinfo --input data/qafqazinfo.json
# Adds "detail" field to each article
```

**Step 3: Process and vectorize** (see main documentation):
```bash
# Process with RAG pipeline
python -m rag_module --source data/qafqazinfo.json --collection news_v1
```

## Configuration

Set up `.env` file with Telegram API credentials:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
```

Get credentials from: https://my.telegram.org/apps

## Performance Tips

- **Concurrent requests**: Increase `--concurrent` for faster parsing (default: 50)
- **Rate limiting**: Telegram fetcher auto-handles rate limits
- **Error handling**: Failed URLs logged but don't stop the process
- **Caching**: Parsed content cached to avoid re-fetching

## Troubleshooting

**Issue: Telegram session errors**

Solution: Delete `session.session` file and re-authenticate

**Issue: Parser returns empty content**

Check:
1. URL extraction working: verify `url` field in JSON
2. CSS selector correct: inspect target website HTML
3. Website structure changed: update parser

**Issue: Slow parsing**

Solutions:
- Increase concurrency: `--concurrent 100`
- Check network connection
- Verify website response time
