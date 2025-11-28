"""Protocol definitions for data processing pipeline components."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Document:
    """Processed document with content, metadata, and chunks."""

    content: str
    metadata: dict[str, Any]
    chunks: list[str] = field(default_factory=list)


class IDataLoader(Protocol):
    """Interface for loading data from various sources."""

    def load(self, source: str) -> list[dict[str, Any]]:
        """Load raw data from source.

        Args:
            source: Path or identifier of data source

        Returns:
            List of raw data dictionaries
        """
        ...


class ITextCleaner(Protocol):
    """Interface for text cleaning and normalization."""

    def clean(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        ...


class ITextAnalyzer(Protocol):
    """Interface for text analysis and metadata extraction."""

    def analyze(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze text and extract metadata.

        Args:
            text: Text to analyze
            context: Additional context information

        Returns:
            Extracted metadata dictionary
        """
        ...


class ITextChunker(Protocol):
    """Interface for splitting text into chunks."""

    def chunk(self, text: str) -> list[str]:
        """Split text into processable chunks.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        ...
