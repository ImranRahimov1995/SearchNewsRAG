"""Tests for query processing protocols and data structures."""

from rag_module.query_processing.protocols import (
    Entity,
    EntityType,
    ProcessedQuery,
    QueryAnalysis,
    QueryIntent,
    RetrievalStrategy,
)


class TestEnums:
    """Test enum definitions."""

    def test_query_intent_values(self):
        """Test all QueryIntent enum values."""
        assert QueryIntent.FACTOID == "factoid"
        assert QueryIntent.DEFINITION == "definition"
        assert QueryIntent.STATISTICAL == "statistical"
        assert QueryIntent.ANALYTICAL == "analytical"
        assert QueryIntent.TASK_ORIENTED == "task_oriented"
        assert QueryIntent.OPINION == "opinion"
        assert QueryIntent.LOCAL_AZ == "local_az"
        assert QueryIntent.UNKNOWN == "unknown"

    def test_retrieval_strategy_values(self):
        """Test all RetrievalStrategy enum values."""
        assert RetrievalStrategy.SIMPLE_SEARCH == "simple_search"
        assert (
            RetrievalStrategy.STATISTICAL_AGGREGATION
            == "statistical_aggregation"
        )
        assert RetrievalStrategy.RAG_RETRIEVAL == "rag_retrieval"
        assert RetrievalStrategy.TOOL_CALLING == "tool_calling"
        assert RetrievalStrategy.LLM_REASONING == "llm_reasoning"
        assert RetrievalStrategy.HYBRID_SEARCH == "hybrid_search"
        assert RetrievalStrategy.LOCAL_SEARCH == "local_search"

    def test_entity_type_values(self):
        """Test EntityType enum values."""
        assert EntityType.PERSON == "person"
        assert EntityType.ORGANIZATION == "organization"
        assert EntityType.LOCATION == "location"
        assert EntityType.DATE == "date"
        assert EntityType.DOCUMENT == "document"


class TestEntity:
    """Test Entity dataclass."""

    def test_create_entity(self):
        """Test creating entity with all fields."""
        entity = Entity(
            text="Bakı",
            type=EntityType.LOCATION,
            normalized="Baku",
            confidence=0.95,
        )

        assert entity.text == "Bakı"
        assert entity.type == EntityType.LOCATION
        assert entity.normalized == "Baku"
        assert entity.confidence == 0.95

    def test_entity_defaults(self):
        """Test entity default values."""
        entity = Entity(text="Test", type=EntityType.OTHER)

        assert entity.normalized is None
        assert entity.confidence == 1.0


class TestProcessedQuery:
    """Test ProcessedQuery dataclass."""

    def test_create_processed_query(self):
        """Test creating processed query."""
        query = ProcessedQuery(
            original="BAKI harada?",
            cleaned="baki harada",
            corrected="bakı harada",
            language="az",
        )

        assert query.original == "BAKI harada?"
        assert query.cleaned == "baki harada"
        assert query.corrected == "bakı harada"
        assert query.language == "az"

    def test_default_language(self):
        """Test default language is Azerbaijani."""
        query = ProcessedQuery(
            original="test", cleaned="test", corrected="test"
        )

        assert query.language == "az"


class TestQueryAnalysis:
    """Test QueryAnalysis dataclass."""

    def test_create_full_analysis(self):
        """Test creating complete query analysis."""
        entities = [
            Entity(text="Bakı", type=EntityType.LOCATION),
            Entity(text="2024", type=EntityType.DATE),
        ]

        analysis = QueryAnalysis(
            intent=QueryIntent.FACTOID,
            entities=entities,
            confidence=0.85,
            keywords=["bakı", "xəbər"],
            is_local_content=True,
            requires_temporal_filter=True,
            metadata={"source": "test"},
        )

        assert analysis.intent == QueryIntent.FACTOID
        assert len(analysis.entities) == 2
        assert analysis.confidence == 0.85
        assert "bakı" in analysis.keywords
        assert analysis.is_local_content is True
        assert analysis.requires_temporal_filter is True
        assert analysis.metadata["source"] == "test"

    def test_analysis_defaults(self):
        """Test QueryAnalysis default values."""
        analysis = QueryAnalysis(intent=QueryIntent.UNKNOWN)

        assert analysis.entities == []
        assert analysis.confidence == 0.0
        assert analysis.keywords == []
        assert analysis.is_local_content is False
        assert analysis.requires_temporal_filter is False
        assert analysis.metadata == {}
