# SearchNewsApp - RAG-based News Search System

## Goal
Build a semantic search engine for Azerbaijani news articles using
Retrieval-Augmented Generation (RAG) with vector embeddings.

## Tech Stack
- **Vector DB**: ChromaDB (persistent storage)
- **Embeddings**: OpenAI text-embedding-3-small
- **Framework**: LangChain
- **Text Processing**: Custom pipeline for Azerbaijani text
- **Data Source**: Telegram news channels

## Flow
1. **Data Collection** → Fetch news from Telegram channels
2. **Text Processing** → Clean markdown, remove emojis, normalize text
3. **Chunking** → Split documents (600 chars, 150 overlap)
4. **Vectorization** → Generate embeddings via OpenAI
5. **Storage** → Store in ChromaDB with metadata
6. **Search** → Hybrid search (semantic + keyword matching)

## Telegram Fetcher
Modular service for collecting messages from Telegram channels.

**Features:**
- Configurable date filtering
- JSON output with automatic directory creation
- Support for multiple channels

**Usage:**
```bash
# Collect all sources
python -m telegram_fetcher --stop-date 2025-11-23

# Specific source
python -m telegram_fetcher --source qafqazinfo --stop-date 2024-01-01

# Custom output directory
python -m telegram_fetcher --stop-date 2025-11-23 --output-dir ./datanew
```


### 2. News Detail Parser
Async service for extracting full article content from URLs.

**Features:**
- Async HTTP requests with aiohttp (2-3x faster than threading)
- Configurable concurrent request limit (semaphore)
- Site-specific parsers (easily extensible)
- Smart retry logic with exponential backoff
- Comprehensive error logging


**Usage:**
```bash
# Parse article details from JSON
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json

# Save to different file
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json \
  --output datanew/qafqazinfo_full.json

# Overwrite existing details
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json \
  --overwrite

# Increase concurrency for faster processing
python -m telegram_fetcher.parsers \
  --site qafqazinfo \
  --input datanew/qafqazinfo.json \
  --concurrent 100
```

**Output format:**
```json
[
  {
    "id": 12345,
    "date": "2024-11-24T10:30:00+00:00",
    "text": "Breaking news content...",

  }
]
```


**Architecture:**
- `base.py` - Core abstractions and collectors
- `services.py` - NewsCollectionService implementation
- `__main__.py` - CLI entry point


**Output format:**
```json
[
  {
    "id": 12345,
    "date": "2024-11-24T10:30:00+00:00",
    "text": "Breaking news...",
    "url": "https://qafqazinfo.az/news/detail/12345",
    "detail": "Full article content extracted from webpage..."
  }
]
```

**Architecture:**
- `parsers/base.py` - Abstract interfaces and base implementations
  - `IURLExtractor` - Extract URLs from text
  - `IContentFetcher` - Async HTTP fetching
  - `IContentParser` - Parse HTML content
  - `BaseContentParser` - Base parser class
- `parsers/qafqazinfo.py` - QafqazInfo site-specific parser
- `parsers/__main__.py` - CLI for batch processing




## Environment
Requires `.env` with:
```
SETTINGS=local
OPENAI_API_KEY=your_key_here
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
```
