"""Text analyzers for metadata extraction and classification."""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


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
            "llm_analysis_exists": False,
        }

        logger.debug(f"Analyzed text: {metadata['word_count']} words")
        return metadata
