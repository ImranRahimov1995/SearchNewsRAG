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

**Architecture:**
- `base.py` - Core abstractions and collectors
- `services.py` - NewsCollectionService implementation
- `__main__.py` - CLI entry point

## Environment
Requires `.env` with:
```
SETTINGS=local
OPENAI_API_KEY=your_key_here
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
```
