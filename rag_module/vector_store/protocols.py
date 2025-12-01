"""Protocol definitions for vector store components."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class VectorDocument:
    """Document for vector storage.

    Attributes:
        id: Unique document identifier
        content: Text content to be vectorized (chunk)
        metadata: Additional document metadata including full text
        vector: Optional pre-computed embedding vector
    """

    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    vector: list[float] | None = None


@dataclass
class VectorSearchResult:
    """Search result from vector store.

    Attributes:
        document: Retrieved document
        score: Similarity score
        distance: Distance metric (if applicable)
    """

    document: VectorDocument
    score: float
    distance: float | None = None


class IVectorStore(Protocol):
    """Interface for vector storage operations."""

    def add(self, document: VectorDocument) -> str:
        """Add single document to vector store.

        Args:
            document: Document to add

        Returns:
            Document ID

        Raises:
            ValueError: If document validation fails
        """
        ...

    def add_batch(self, documents: list[VectorDocument]) -> list[str]:
        """Add multiple documents to vector store.

        Args:
            documents: List of documents to add

        Returns:
            List of document IDs

        Raises:
            ValueError: If batch validation fails
        """
        ...

    def get(self, doc_id: str) -> VectorDocument | None:
        """Retrieve document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        ...

    def update(self, document: VectorDocument) -> bool:
        """Update existing document.

        Args:
            document: Document with updated data

        Returns:
            True if updated, False if not found

        Raises:
            ValueError: If document validation fails
        """
        ...

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def delete_batch(self, doc_ids: list[str]) -> int:
        """Delete multiple documents.

        Args:
            doc_ids: List of document identifiers

        Returns:
            Number of documents deleted
        """
        ...

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar documents.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of search results ordered by similarity
        """
        ...

    def count(self) -> int:
        """Get total number of documents in store.

        Returns:
            Document count
        """
        ...

    def clear(self) -> bool:
        """Remove all documents from store.

        Returns:
            True if successful
        """
        ...


class IEmbedding(Protocol):
    """Interface for embedding generation."""

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for single text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        ...
