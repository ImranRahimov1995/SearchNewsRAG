# Question Answering Service Documentation

## Overview

The `QuestionAnsweringService` is a complete RAG (Retrieval-Augmented Generation) pipeline that answers questions based on retrieved Azerbaijani news articles. It combines semantic search with LLM-based answer generation.

## Architecture

```
User Query → Query Processing → Document Retrieval → LLM Generation → Structured Answer
              ↓                    ↓                      ↓
         (translation, NER)   (vector search)    (OpenAI + context)
```

### Pipeline Components

1. **Query Processing**: Language detection, translation to Azerbaijani, NER, intent classification
2. **Document Retrieval**: Vector search in ChromaDB for relevant news articles
3. **Answer Generation**: LLM synthesizes answer from retrieved documents with source attribution

## Installation

```bash
# Install dependencies
poetry install

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
```

## Quick Start

### Basic Usage

```python
import os
from rag_module.services import QuestionAnsweringService
from rag_module.vector_store import ChromaVectorStore
from rag_module.vector_store.embedding import LangChainEmbedding

# Initialize vector store
embedding = LangChainEmbedding(model="text-embedding-3-large")
vector_store = ChromaVectorStore(
    collection_name="news_analyzed_0_5k_800_200_large",
    embedding=embedding,
    persist_directory="./chroma_db",
)

# Initialize QA service
qa_service = QuestionAnsweringService(
    vector_store=vector_store,
    llm_api_key=os.getenv("OPENAI_API_KEY"),
    llm_model="gpt-4o-mini",
    temperature=0.3,
    top_k=5,
)

# Ask a question
response = qa_service.answer("Azərbaycanın prezidenti kimdir?")

# Access results
print(response.answer)        # Full answer text
print(response.confidence)    # "high", "medium", or "low"
print(response.sources)       # List of SourceInfo objects
print(response.key_facts)     # List of key facts
```

## API Reference

### QuestionAnsweringService

#### Constructor

```python
QuestionAnsweringService(
    vector_store: IVectorStore,
    llm_api_key: str,
    llm_model: str = "gpt-4o-mini",
    temperature: float = 0.3,
    top_k: int = 5,
)
```

**Parameters:**

- `vector_store` (IVectorStore): Vector store instance for document retrieval
- `llm_api_key` (str): OpenAI API key
- `llm_model` (str, optional): LLM model name. Default: `"gpt-4o-mini"`
- `temperature` (float, optional): Generation temperature (0.0-1.0). Default: `0.3`
- `top_k` (int, optional): Number of documents to retrieve. Default: `5`

#### Methods

##### `answer(query: str, top_k: int | None = None) -> QAResponse`

Answer a single question.

**Parameters:**

- `query` (str): User question in any language (Azerbaijani, English, Russian)
- `top_k` (int | None, optional): Override default number of documents to retrieve

**Returns:**

`QAResponse` object with:

- `query` (str): Original user query
- `language` (str): Detected language ("az", "en", "ru")
- `intent` (str): Query intent type ("factoid", "statistical", etc.)
- `answer` (str): Generated answer text
- `sources` (list[SourceInfo]): List of source documents
- `confidence` (str): Answer confidence ("high", "medium", "low")
- `key_facts` (list[str]): Extracted key facts
- `search_results` (list[SearchResult]): Raw search results
- `total_found` (int): Number of documents retrieved
- `handler_used` (str): Handler that processed the query

**Example:**

```python
response = qa_service.answer("Bakıda nə baş verdi?")
print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence}")
for source in response.sources:
    print(f"- {source.name} (ID: {source.id})")
```

##### `answer_batch(queries: list[str]) -> list[QAResponse]`

Answer multiple questions in batch.

**Parameters:**

- `queries` (list[str]): List of user questions

**Returns:**

List of `QAResponse` objects

**Example:**

```python
queries = [
    "Prezident kimdir?",
    "Who won the match?",
    "Что случилось вчера?",
]
responses = qa_service.answer_batch(queries)

for i, resp in enumerate(responses, 1):
    print(f"{i}. {resp.query}")
    print(f"   Answer: {resp.answer}")
    print(f"   Confidence: {resp.confidence}")
```

### QAResponse

Response object containing complete answer information.

#### Attributes

- `query` (str): Original user query
- `language` (str): Detected language code
- `intent` (str): Query intent classification
- `answer` (str): Generated answer text
- `sources` (list[SourceInfo]): Source documents with metadata
- `confidence` (str): Confidence level ("high", "medium", "low")
- `key_facts` (list[str]): Extracted key facts from sources
- `search_results` (list[SearchResult]): Full search results
- `total_found` (int): Total documents retrieved
- `handler_used` (str): Handler name that processed query

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert response to dictionary for API serialization.

**Returns:**

Dictionary with all response fields, including:
- Query metadata
- Answer and confidence
- Sources with URLs
- Key facts
- Retrieved documents with previews

**Example:**

```python
response = qa_service.answer("Test query")
api_data = response.to_dict()

# Use in API endpoint
return jsonify(api_data)
```

### SourceInfo

Source document information.

#### Attributes

- `id` (str): Document ID
- `name` (str): Source name (e.g., "Qafqazinfo", "Operativ.az")
- `url` (str | None): Article URL if available

**Example:**

```python
for source in response.sources:
    print(f"Source: {source.name}")
    print(f"ID: {source.id}")
    if source.url:
        print(f"URL: {source.url}")
```

## Multi-Language Support

The service automatically detects and processes queries in:

- **Azerbaijani** (az)
- **English** (en)
- **Russian** (ru)

Queries are automatically translated to Azerbaijani for vector search, and answers are returned in the original query language.

**Example:**

```python
# Azerbaijani query
response_az = qa_service.answer("Bakıda hava necə olacaq?")
# Answer in Azerbaijani

# English query
response_en = qa_service.answer("What is the weather in Baku?")
# Answer in English

# Russian query
response_ru = qa_service.answer("Какая погода в Баку?")
# Answer in Russian
```

## Advanced Usage

### Custom Configuration

```python
# High precision, more documents
qa_service = QuestionAnsweringService(
    vector_store=vector_store,
    llm_api_key=api_key,
    llm_model="gpt-4o",           # More capable model
    temperature=0.1,               # Lower temperature for factual accuracy
    top_k=10,                      # Retrieve more documents
)

# Fast, creative responses
qa_service = QuestionAnsweringService(
    vector_store=vector_store,
    llm_api_key=api_key,
    llm_model="gpt-4o-mini",      # Faster model
    temperature=0.7,               # Higher creativity
    top_k=3,                       # Fewer documents for speed
)
```

### Error Handling

```python
try:
    response = qa_service.answer(query)

    if response.confidence == "low":
        print("⚠️ Low confidence answer")

    if not response.sources:
        print("⚠️ No sources found")

    print(response.answer)

except Exception as e:
    print(f"Error: {e}")
    # Fallback logic
```
