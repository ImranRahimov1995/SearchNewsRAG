"""Text chunking strategies for document splitting."""

import re
from abc import ABC, abstractmethod

from langchain_text_splitters import RecursiveCharacterTextSplitter

from settings import get_logger

logger = get_logger("text_chunkers")


class BaseTextChunker(ABC):
    """Abstract base class for text chunkers."""

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Split text into chunks.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        pass


class SentenceChunker(BaseTextChunker):
    """Split text by sentences with configurable grouping."""

    def __init__(self, max_sentences: int = 3):
        """Initialize sentence chunker.

        Args:
            max_sentences: Maximum sentences per chunk
        """
        self.max_sentences = max_sentences
        logger.debug(
            f"Initialized SentenceChunker(max_sentences={max_sentences})"
        )

    def chunk(self, text: str) -> list[str]:
        """Split text into sentence-based chunks.

        Args:
            text: Text to split

        Returns:
            List of chunks, each containing up to max_sentences
        """
        if not text or not text.strip():
            return []

        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        for i in range(0, len(sentences), self.max_sentences):
            chunk = ". ".join(sentences[i : i + self.max_sentences])
            if chunk:
                chunks.append(chunk)

        logger.debug(f"Split into {len(chunks)} sentence chunks")
        return chunks


class FixedSizeChunker(BaseTextChunker):
    """Split text into fixed-size chunks with overlap."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """Initialize fixed-size chunker.

        Args:
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

        if overlap >= chunk_size:
            raise ValueError("Overlap must be less than chunk_size")

        logger.debug(
            f"Initialized FixedSizeChunker(size={chunk_size}, overlap={overlap})"
        )

    def chunk(self, text: str) -> list[str]:
        """Split text into fixed-size chunks with overlap.

        Args:
            text: Text to split

        Returns:
            List of overlapping chunks
        """
        if not text or not text.strip():
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end - self.overlap

            if end == len(text):
                break

        logger.debug(f"Split into {len(chunks)} fixed-size chunks")
        return chunks


class LangChainRecursiveChunker(BaseTextChunker):
    """LangChain RecursiveCharacterTextSplitter wrapper.

    Uses LangChain's battle-tested recursive text splitter with
    configurable separators and overlap.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50,
        separators: list[str] | None = None,
    ):
        """Initialize LangChain recursive chunker.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Number of overlapping characters between chunks
            separators: List of separators in priority order
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=separators or ["\n\n", "\n", ". ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

        logger.info(
            f"Initialized LangChainRecursiveChunker(size={chunk_size}, "
            f"overlap={overlap})"
        )

    def chunk(self, text: str) -> list[str]:
        """Split text using LangChain's recursive splitter.

        Args:
            text: Text to split

        Returns:
            List of semantically coherent chunks
        """
        if not text or not text.strip():
            return []

        chunks = list(self.splitter.split_text(text))
        logger.debug(f"LangChain split produced {len(chunks)} chunks")
        return chunks
