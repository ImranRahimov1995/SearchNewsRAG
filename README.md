# SearchNewsRAG - AI-Powered News Search & Analytics

[![Production](https://img.shields.io/badge/production-news.aitools.az-blue)](https://news.aitools.az)
[![GitHub](https://img.shields.io/badge/github-SearchNewsRAG-black)](https://github.com/ImranRahimov1995/SearchNewsRAG)

**Semantic search engine and analytics platform for Azerbaijani news using RAG (Retrieval-Augmented Generation) with vector embeddings and LLM-powered metadata analysis.**

## Description

SearchNewsRAG enables intelligent search across large-scale Azerbaijani news archives by combining vector similarity search with AI-powered content analysis. The system automatically collects news from Telegram channels, processes and analyzes articles using OpenAI, stores them with rich metadata in a vector database, and provides both semantic search and conversational Q&A interface.

**Key Capabilities**:
- Semantic search across thousands of news articles
- Real-time news analytics and categorization
- Statistical analysis (trends, frequencies, distributions)
- Predictive insights based on historical patterns
- Conversational Q&A interface

## System Architecture

### Telegram Module
Asynchronous data collection system that:
- Fetches news messages from configured Telegram channels
- Extracts full article content from news URLs
- Handles rate limiting and retries automatically
- Outputs structured JSON with metadata

### RAG Module
Advanced document processing pipeline that:
- Analyzes articles using OpenAI (categories, entities, sentiment, importance)
- Splits documents into semantic chunks (600 chars, 150 overlap)
- Generates embeddings via OpenAI text-embedding-3-small
- Stores vectors in ChromaDB with metadata for enhanced search
- Enables hybrid search (semantic + keyword + metadata filtering)

**Analysis Features**:
- Content categorization (politics, economy, sports, etc.)
- Named entity extraction (people, organizations, locations)
- Sentiment analysis and importance scoring
- Geographic and temporal tagging

### Backend
FastAPI service providing:
- RESTful API for news search and filtering
- Conversational Q&A endpoint powered by RAG
- Metadata aggregation (categories, date ranges, entities)
- Pagination and advanced filtering

**Scalability**:
- Stateless design for horizontal scaling
- Async I/O for high throughput
- Connection pooling for ChromaDB
- Ready for load balancing and Redis caching
- Future: PostgreSQL for structured analytics data

**Background Tasks** (Coming Soon):
- Scheduled news collection via Celery workers
- Automatic article processing and vectorization
- Periodic database reindexing
- Analytics computation and caching

### Frontend
React/TypeScript single-page application with:
- News browsing interface with filtering by category, date, importance
- Conversational chat interface for natural language queries
- Real-time search with highlighting
- Responsive design for mobile and desktop

## Tech Stack

- **Vector Database**: ChromaDB (persistent, scalable)
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-4 (analysis and Q&A)
- **Backend**: FastAPI, Python 3.12
- **Frontend**: React, Vite, TypeScript, Tailwind CSS
- **Data Collection**: Telethon (Telegram), aiohttp (async scraping)
- **Infrastructure**: Docker, Nginx, GitHub Actions CI/CD

## Documentation

- **[Data Collection Guide](docs/DATA_COLLECTION.md)** - Telegram fetcher and content parsers
- **[Deployment Guide](docs/DEPLOYMENT.md)** - CI/CD pipeline and production setup
- **[QA Service](docs/QA_SERVICE.md)** - Question answering system architecture
- **[Vectorization Service](docs/VECTORIZATION_SERVICE.md)** - Document processing pipeline

## Local Development

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development without Docker)
- OpenAI API key
- Telegram API credentials

### Setup

1. **Clone repository**:
```bash
git clone https://github.com/ImranRahimov1995/SearchNewsRAG.git
cd SearchNewsRAG
```

2. **Configure environment**:
```bash
# Create .env file in project root
cat > .env << EOF
SETTINGS=local
ENVIRONMENT=local

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Telegram API (get from https://my.telegram.org/apps)
API_ID=12345678
API_HASH=your_telegram_api_hash

# ChromaDB
CHROMA_COLLECTION_NAME=news_analyzed_0_5k_800_200_large
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# CORS (for local development)
CORS_ORIGINS='["http://localhost:5173","http://localhost:3000"]'
EOF
```

3. **Start services**:
```bash
docker-compose up -d
```

Services will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ChromaDB**: http://localhost:8001

### Data Collection & Processing

**Step 1: Collect news from Telegram**:
```bash
python -m telegram_fetcher --stop-date 2025-11-23 --output-dir ./data
```

**Step 2: Extract full article content**:
```bash
python -m telegram_fetcher.parsers --site qafqazinfo --input data/qafqazinfo.json
```

**Step 3: Process and vectorize**:
```bash
python -m rag_module --source data/qafqazinfo.json --collection news_v1
```

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Fast tests only
make test-fast
```

### Code Quality

```bash
# Format code
make format

# Lint
make lint

# Full CI checks
make ci
```

## Production Deployment

Automated CI/CD pipeline deploys to production on PR merge to `main` branch.

**Live Site**: [https://news.aitools.az](https://news.aitools.az)

See [Deployment Guide](docs/DEPLOYMENT.md) for details.

## Project Structure

```
SearchNewsRAG/
├── telegram_fetcher/       # Async data collection from Telegram
│   ├── base.py            # Core abstractions
│   ├── services.py        # Collection orchestration
│   └── parsers/           # Site-specific HTML parsers
├── rag_module/            # RAG pipeline and vectorization
│   ├── data_processing/   # Text cleaning, chunking, analysis
│   ├── vector_store/      # ChromaDB interface
│   ├── query_processing/  # Query understanding and routing
│   └── retrieval/         # Search strategies
├── backend/               # FastAPI service
│   └── src/
│       ├── news/          # News search endpoints
│       ├── chats/         # Q&A chat endpoints
│       └── main.py        # Application entry point
├── frontend/              # React SPA
│   └── src/
│       ├── components/    # UI components
│       └── services/      # API clients
├── docker/                # Docker configurations
├── docs/                  # Documentation
└── tests/                 # Comprehensive test suite
```

## Roadmap

### Upcoming Features

1. **Statistical Analytics**:
   - Trend analysis and visualization
   - Frequency distributions by category/entity
   - Time-series forecasting

2. **Predictive Capabilities**:
   - Event prediction based on historical patterns
   - Topic emergence detection
   - Sentiment trend forecasting

3. **Background Processing**:
   - Celery workers for scheduled tasks
   - Automatic news ingestion pipeline
   - Real-time notifications for breaking news

4. **Database Expansion**:
   - PostgreSQL for analytics and user data
   - Redis for caching and rate limiting
   - Elasticsearch for advanced full-text search

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and code standards.

## License

Open Source Non-Commercial License - see [LICENSE](LICENSE) for details.

**Note**: Commercial use is prohibited. For commercial licensing inquiries, please contact the author.

---

**Built with ❤️ for Azerbaijani news consumers**
