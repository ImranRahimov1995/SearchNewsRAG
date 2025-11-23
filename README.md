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


## Environment
Requires `.env` with:
```
OPENAI_API_KEY=your_key_here
```
