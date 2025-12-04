"""Data processing pipeline components for RAG module."""

from .chunkers import FixedSizeChunker, SentenceChunker
from .cleaners import AzerbaijaniNewsCleaner
from .loaders import JSONFileLoader, TelegramJSONLoader
from .pipeline import (
    AsyncDocumentProcessingPipeline,
    AsyncPipelineFactory,
    DocumentProcessingPipeline,
    PipelineFactory,
)
from .protocols import (
    Document,
    IAsyncTextAnalyzer,
    IDataLoader,
    ITextAnalyzer,
    ITextChunker,
    ITextCleaner,
)

__all__ = [
    # Protocols
    "Document",
    "IDataLoader",
    "ITextCleaner",
    "ITextAnalyzer",
    "IAsyncTextAnalyzer",
    "ITextChunker",
    # Chunkers
    "FixedSizeChunker",
    "SentenceChunker",
    # Cleaners
    "AzerbaijaniNewsCleaner",
    # Loaders
    "JSONFileLoader",
    "TelegramJSONLoader",
    # Pipeline
    "DocumentProcessingPipeline",
    "PipelineFactory",
    "AsyncDocumentProcessingPipeline",
    "AsyncPipelineFactory",
]
