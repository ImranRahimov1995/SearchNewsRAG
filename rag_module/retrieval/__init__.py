"""Retrieval module - search handlers and pipeline."""

from .handlers import SimpleSearchHandler, UnknownHandler
from .pipeline import RetrievalPipeline, RetrievalResult
from .protocols import SearchResult

__all__ = [
    "SimpleSearchHandler",
    "UnknownHandler",
    "RetrievalPipeline",
    "RetrievalResult",
    "SearchResult",
]
