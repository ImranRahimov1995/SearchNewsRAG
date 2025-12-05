"""Retrieval handlers for different query types."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class SearchResult:
    """Single search result from retrieval."""

    doc_id: int | str
    content: str
    score: float
    metadata: dict


class IRetrievalHandler(Protocol):
    """Interface for retrieval handlers."""

    def retrieve(
        self, query: str, entities: list, top_k: int = 10
    ) -> list[SearchResult]:
        """Retrieve relevant documents.

        Args:
            query: Search query
            entities: Extracted entities from query
            top_k: Number of results to return

        Returns:
            List of search results
        """
        ...
