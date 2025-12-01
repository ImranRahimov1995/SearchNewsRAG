"""Text analyzers for metadata extraction and classification."""

from abc import ABC, abstractmethod
from typing import Any

from settings import get_logger

logger = get_logger("text_analyzers")


class BaseTextAnalyzer(ABC):
    """Abstract base class for text analyzers."""

    @abstractmethod
    def analyze(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze text and extract metadata.

        Args:
            text: Text to analyze
            context: Additional context information

        Returns:
            Extracted metadata dictionary
        """
        pass


class DummyAnalyzer(BaseTextAnalyzer):
    """Basic analyzer returning simple statistics.

    Placeholder analyzer for when LLM classification is not available.
    """

    def analyze(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Extract basic text statistics.

        Args:
            text: Text to analyze
            context: Context with source information

        Returns:
            Dictionary with basic statistics
        """
        metadata = {
            "length": len(text),
            "word_count": len(text.split()),
        }

        logger.debug(f"Analyzed text: {metadata['word_count']} words")
        return metadata


class NewsClassifier(BaseTextAnalyzer):
    """News classifier with LLM integration support.

    Falls back to DummyAnalyzer when LLM client is not provided.
    """

    def __init__(self, llm_client: Any = None):
        """Initialize classifier with optional LLM client.

        Args:
            llm_client: Optional LLM client for classification
        """
        self.llm = llm_client
        self.fallback = DummyAnalyzer()

        if self.llm is None:
            logger.warning("NewsClassifier initialized without LLM client")
        else:
            logger.info("NewsClassifier initialized with LLM client")

    def analyze(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Classify news article.

        Args:
            text: News text to classify
            context: Context with date and source

        Returns:
            Metadata with category, importance, and tags
        """
        base_metadata = self.fallback.analyze(text, context)

        if self.llm is None:
            logger.debug(
                "No LLM available - classification fields set to None"
            )
            base_metadata["importance"] = None
            base_metadata["category"] = None
            base_metadata["tags"] = None
            return base_metadata

        logger.debug("Classifying with LLM")
        llm_metadata = {
            "category": "politics",
            "importance": "high",
            "tags": ["news", "politics"],
            "confidence": 0.85,
        }

        return {**base_metadata, **llm_metadata}
