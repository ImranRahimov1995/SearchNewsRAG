# VectorizationService - Flexible RAG Vectorization

## Overview

Comprehensive vectorization service with **three analyzer modes** and LangChain embeddings integration.

## Features

✅ **Three Analyzer Modes:**
- `async` - Async OpenAI analyzer with semaphore (max 50 concurrent)
- `sync` - Sync OpenAI analyzer for simple processing  
- `none` - No LLM analysis (fastest, basic metadata only)

✅ **LangChain Integration:**
- Uses `LangChainEmbedding` with OpenAI embeddings
- Recursive text splitting for optimal chunks

✅ **Flexible Configuration:**
- Centralized `VectorizationConfig` dataclass
- Full validation with clear error messages
- Easy switching between modes

---

## Quick Start

### 1. Async Mode (Default - Recommended)
```bash
# Full LLM analysis with concurrent processing
python -m rag_module vectorize \\
  --source data/news.json \\
  --source-name qafqazinfo_2024 \\
  --collection news_async

# With slicing (first 100 documents)
python -m rag_module vectorize \\
  --source data/news.json \\
  --source-name qafqazinfo_batch1 \\
  --end-index 100
```

### 2. Sync Mode
```bash
# Synchronous processing (simpler, sequential)
python -m rag_module vectorize \\
  --source data/news.json \\
  --source-name qafqazinfo_sync \\
  --sync
```

### 3. No Analyzer Mode
```bash
# Fast vectorization without LLM (no category/sentiment/etc)
python -m rag_module vectorize \\
  --source data/news.json \\
  --source-name qafqazinfo_fast \\
  --analyzer-mode none
```

---

## Python API Usage

### Using create_default() Factory

```python
from typing import Literal
from rag_module.services import VectorizationService

# Async mode (default)
service = VectorizationService.create_default(
    collection_name="news_async",
    persist_directory="./chroma_db",
    analyzer_mode="async",  # Literal['async', 'sync', 'none']
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    chunk_size=600,
    overlap=100,
    max_concurrent=50,
)

result = service.vectorize(
    source="data/news.json",
    source_name="qafqazinfo_2024",
    start_index=0,
    end_index=100,
)

print(f"✅ Vectorized {result.total_chunks} chunks from {result.total_documents} docs")
```

### Using Config Object

```python
from typing import Literal
from rag_module.services import VectorizationConfig, VectorizationService
from rag_module.vector_store import ChromaVectorStore
from rag_module.vector_store.embedding import LangChainEmbedding

# 1. Create config
config = VectorizationConfig(
    analyzer_mode="async",  # Literal['async', 'sync', 'none']
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0.1,
    chunk_size=600,
    overlap=100,
    max_concurrent=50,
    collection_name="news",
    persist_directory="./chroma_db",
    embedding_model="text-embedding-3-small",
)

# 2. Create vector store
embedding = LangChainEmbedding(model=config.embedding_model)
vector_store = ChromaVectorStore(
    collection_name=config.collection_name,
    embedding=embedding,
    persist_directory=config.persist_directory,
)

# 3. Create service
service = VectorizationService(
    vector_store=vector_store,
    config=config,
)

# 4. Vectorize
result = service.vectorize(
    source="data/news.json",
    source_name="qafqazinfo",
)
```

---

## Configuration Reference

### VectorizationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `analyzer_mode` | Literal['async', 'sync', 'none'] | `"async"` | Analyzer mode: async (concurrent LLM), sync (sequential), or none (no LLM) |
| `api_key` | str \| None | `None` | OpenAI API key (uses env var if None) |
| `model` | str | `"gpt-4o-mini"` | OpenAI model for analysis |
| `temperature` | float | `0.1` | Generation temperature (0-2) |
| `chunk_size` | int | `600` | Target chunk size in characters |
| `overlap` | int | `100` | Overlap between chunks |
| `max_concurrent` | int | `50` | Max concurrent requests (async mode) |
| `collection_name` | str | `"news"` | ChromaDB collection name |
| `persist_directory` | str | `"./chroma_db"` | ChromaDB persistence directory |
| `embedding_model` | str | `"text-embedding-3-small"` | OpenAI embedding model |

### Validation Rules

- `analyzer_mode` must be one of: Literal['async', 'sync', 'none']
- `chunk_size` must be > 0
- `overlap` must be >= 0 and < `chunk_size`
- `max_concurrent` must be > 0
- `temperature` must be between 0 and 2

---

## CLI Arguments

```bash
python -m rag_module vectorize --help
```

### Required Arguments
- `--source` - Path to source JSON file
- `--source-name` - Identifier for the source (used in document IDs)

### Optional Arguments
- `--collection` - ChromaDB collection name (default: `news`)
- `--persist-dir` - ChromaDB directory (default: `./chroma_db`)
- `--start-index` - Start index for slicing
- `--end-index` - End index for slicing
- `--analyzer-mode` - Analyzer mode: `async`, `sync`, or `none` (default: `async`)
- `--sync` - Shortcut for `--analyzer-mode sync`
- `--api-key` - OpenAI API key (uses env var if not provided)
- `--model` - OpenAI model (default: `gpt-4o-mini`)
- `--temperature` - Generation temperature (default: `0.1`)
- `--chunk-size` - Chunk size in characters (default: `600`)
- `--overlap` - Overlap between chunks (default: `100`)
- `--max-concurrent` - Max concurrent requests (default: `50`)

---

## Mode Comparison

| Feature | Async | Sync | None |
|---------|-------|------|------|
| **Speed** | ⚡⚡⚡ Very Fast | 🐢 Slow | ⚡⚡⚡⚡ Ultra Fast |
| **LLM Analysis** | ✅ Full | ✅ Full | ❌ No |
| **Metadata** | Rich | Rich | Basic |
| **Concurrent** | Yes (50) | No | No |
| **Rate Limits** | Handled | N/A | N/A |
| **Use Case** | Large batches | Small datasets | Speed-critical |
| **Cost** | Moderate | Low | Minimal |

---

## Pipeline Details

### Async Mode Pipeline
```python
AsyncDocumentProcessingPipeline(
    loader=TelegramJSONLoader(),
    cleaner=TelegramNewsCleaner(),
    analyzer=AsyncOpenAINewsAnalyzer(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.1,
        max_concurrent=50,  # Semaphore limit
    ),
    chunker=LangChainRecursiveChunker(
        chunk_size=600,
        overlap=100,
        separators=["\\n\\n", "\\n", ". ", " ", ""],
    ),
)
```

### Sync Mode Pipeline
```python
DocumentProcessingPipeline(
    loader=TelegramJSONLoader(),
    cleaner=TelegramNewsCleaner(),
    analyzer=OpenAINewsAnalyzer(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.1,
    ),
    chunker=LangChainRecursiveChunker(
        chunk_size=600,
        overlap=100,
        separators=["\\n\\n", "\\n", ". ", " ", ""],
    ),
)
```

### None Mode Pipeline
```python
DocumentProcessingPipeline(
    loader=TelegramJSONLoader(),
    cleaner=TelegramNewsCleaner(),
    analyzer=None,  # No LLM analysis
    chunker=LangChainRecursiveChunker(
        chunk_size=600,
        overlap=100,
        separators=["\\n\\n", "\\n", ". ", " ", ""],
    ),
)
```

---

## Examples

### Example 1: Process Full Dataset (Async)
```bash
python -m rag_module vectorize \\
  --source data/qafqazfull.json \\
  --source-name qafqazinfo_full \\
  --collection news_production
```

### Example 2: Process Subset (First 1000)
```bash
python -m rag_module vectorize \\
  --source data/qafqazfull.json \\
  --source-name qafqazinfo_sample \\
  --end-index 1000 \\
  --collection news_sample
```

### Example 3: Fast Vectorization (No Analysis)
```bash
python -m rag_module vectorize \\
  --source data/news.json \\
  --source-name news_fast \\
  --analyzer-mode none \\
  --collection news_fast
```

### Example 4: Custom Parameters
```bash
python -m rag_module vectorize \\
  --source data/news.json \\
  --source-name news_custom \\
  --model gpt-4 \\
  --chunk-size 800 \\
  --overlap 150 \\
  --max-concurrent 100 \\
  --temperature 0.2
```

### Example 5: Sync Mode for Debugging
```bash
python -m rag_module vectorize \\
  --source data/test.json \\
  --source-name test_data \\
  --sync \\
  --end-index 10
```

---

## Metadata Generated

### With LLM Analysis (async/sync modes)
```python
{
    "category": "politics",  # Auto-classified
    "sentiment": "positive",  # positive/neutral/negative
    "sentiment_score": 0.75,  # -1 to 1
    "importance": 8,  # 1-10 scale
    "geographic_scope": "national",  # local/regional/national/international
    "temporal_relevance": "current",  # breaking/current/recent/historical
    "topics": ["government", "diplomacy"],
    "entities": ["Prezident", "Türkiyə"],
    "entity_count": 2,
    "keywords": ["görüş", "əməkdaşlıq", "layihə"],
    "summary": "Brief summary...",
    "llm_analysis_exists": True,  # Flag
    
    # Chunk metadata
    "source": "qafqazinfo_2024",
    "doc_id": "123",
    "chunk_index": 0,
    "total_chunks": 3,
    "chunk_size": 542,
}
```

### Without LLM Analysis (none mode)
```python
{
    "llm_analysis_exists": False,
    "source": "qafqazinfo_2024",
    "doc_id": "123",
    "chunk_index": 0,
    "total_chunks": 3,
    "chunk_size": 542,
}
```

---

## Architecture Highlights

✅ **SOLID Principles:**
- Single Responsibility: Each method has one clear purpose
- Open/Closed: Extend via config, not modification
- Dependency Inversion: Depends on `VectorizationConfig` abstraction

✅ **DRY:**
- Shared pipeline creation logic
- Reusable helper methods (all <15 lines)
- Configuration centralized

✅ **Clean Code:**
- No method > 25 lines
- Clear method names
- Comprehensive docstrings

---

## Troubleshooting

### Issue: "analyzer_mode must be 'async', 'sync', or 'none'"
**Solution:** Use valid mode from Literal['async', 'sync', 'none']: `--analyzer-mode async` or `--analyzer-mode sync` or `--analyzer-mode none`

### Issue: "chunk_size must be positive"
**Solution:** Ensure `--chunk-size` > 0

### Issue: "overlap must be less than chunk_size"
**Solution:** Set `--overlap` < `--chunk-size`

### Issue: OpenAI API rate limits
**Solution:** Reduce `--max-concurrent` (e.g., `--max-concurrent 20`)

### Issue: Out of memory
**Solution:** Process in batches with `--start-index` and `--end-index`

---

## Best Practices

1. **For large datasets (>500 docs):** Use `analyzer_mode="async"` with `max_concurrent=50`
2. **For debugging:** Use `analyzer_mode="sync"` with `--end-index 10`
3. **For speed:** Use `analyzer_mode="none"` (no LLM costs)
4. **For cost optimization:** Use smaller chunks (`chunk_size=400`) or none mode
5. **For better quality:** Use larger chunks (`chunk_size=800`) with more overlap

---

**Created:** 2024-12-04  
**Version:** 2.0 - Flexible Configuration Architecture
