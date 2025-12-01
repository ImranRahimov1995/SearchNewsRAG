"""Protocol definitions for query processing components."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class QueryIntent(str, Enum):
    """Query intent classification types."""

    FACTOID = "factoid"  # who, what, when, where
    DEFINITION = "definition"  # definition requests
    STATISTICAL = "statistical"  # numbers, percentages, dynamics
    ANALYTICAL = "analytical"  # why, explain, reasoning
    TASK_ORIENTED = "task_oriented"  # create, build, generate
    OPINION = "opinion"  # subjective, no factual answer
    LOCAL_AZ = "local_az"  # Azerbaijan-specific entities/slang
    UNKNOWN = "unknown"  # cannot classify


class RetrievalStrategy(str, Enum):
    """Retrieval strategy for different query types."""

    SIMPLE_SEARCH = "simple_search"  # Basic vector/keyword search
    STATISTICAL_AGGREGATION = "statistical_aggregation"  # Count/aggregate
    RAG_RETRIEVAL = "rag_retrieval"  # Retrieve + generate
    TOOL_CALLING = "tool_calling"  # Execute specific tool
    LLM_REASONING = "llm_reasoning"  # Pure LLM generation
    HYBRID_SEARCH = "hybrid_search"  # Combine multiple strategies
    LOCAL_SEARCH = "local_search"  # Search in AZ-specific data


class EntityType(str, Enum):
    """Named entity types."""

    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    DOCUMENT = "document"
    NUMBER = "number"
    MONEY = "money"
    OTHER = "other"


@dataclass
class Entity:
    """Named entity extracted from query."""

    text: str  # Original entity text
    type: EntityType  # Entity classification
    normalized: str | None = None  # Normalized form
    confidence: float = 1.0  # Extraction confidence


@dataclass
class ProcessedQuery:
    """Cleaned and corrected query."""

    original: str  # Original raw query
    cleaned: str  # After cleaning (lowercase, whitespace)
    corrected: str  # After grammar/spell correction
    language: str = "az"  # Detected language


@dataclass
class QueryAnalysis:
    """Complete query analysis result."""

    intent: QueryIntent  # Primary intent
    entities: list[Entity] = field(default_factory=list)  # Extracted entities
    confidence: float = 0.0  # Overall confidence
    keywords: list[str] = field(default_factory=list)  # Key terms
    is_local_content: bool = False  # Azerbaijan-specific
    requires_temporal_filter: bool = False  # Date filtering needed
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional info


class IQueryCleaner(Protocol):
    """Interface for query text cleaning."""

    def clean(self, query: str) -> str:
        """Clean raw query text.

        Args:
            query: Raw user query

        Returns:
            Cleaned query text
        """
        ...


class IQueryCorrector(Protocol):
    """Interface for grammar/spell correction."""

    def correct(self, query: str) -> str:
        """Correct grammar and spelling.

        Args:
            query: Cleaned query text

        Returns:
            Corrected query text
        """
        ...


class IEntityExtractor(Protocol):
    """Interface for Named Entity Recognition."""

    def extract(self, query: str) -> list[Entity]:
        """Extract named entities from query.

        Args:
            query: Query text

        Returns:
            List of extracted entities
        """
        ...


class IIntentClassifier(Protocol):
    """Interface for query intent classification."""

    def classify(self, query: str, entities: list[Entity]) -> QueryAnalysis:
        """Classify query intent.

        Args:
            query: Processed query text
            entities: Extracted entities

        Returns:
            Query analysis with intent and metadata
        """
        ...


class IQueryRouter(Protocol):
    """Interface for routing queries to retrieval strategies."""

    def route(self, analysis: QueryAnalysis) -> RetrievalStrategy:
        """Determine optimal retrieval strategy.

        Args:
            analysis: Query analysis result

        Returns:
            Recommended retrieval strategy
        """
        ...
