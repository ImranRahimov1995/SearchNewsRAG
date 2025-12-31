"""Tests for query routing logic."""

from rag_module.query_processing.protocols import (
    Entity,
    EntityType,
    QueryAnalysis,
    QueryIntent,
    RetrievalStrategy,
)
from rag_module.query_processing.router import QueryRouter


class TestQueryRouter:
    """Test QueryRouter functionality."""

    def test_factoid_routing(self):
        """Test routing for factoid queries."""
        router = QueryRouter()
        analysis = QueryAnalysis(intent=QueryIntent.FACTOID, confidence=0.9)

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.SIMPLE_SEARCH

    def test_statistical_routing(self):
        """Test routing for statistical queries."""
        router = QueryRouter()
        analysis = QueryAnalysis(
            intent=QueryIntent.STATISTICAL, confidence=0.85
        )

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.STATISTICS_QUERY

    def test_analytical_routing(self):
        """Test routing for analytical queries."""
        router = QueryRouter()
        analysis = QueryAnalysis(intent=QueryIntent.ANALYTICAL, confidence=0.8)

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.HYBRID_SEARCH

    def test_factoid_always_simple_search(self):
        """Test factoid queries always use simple search."""
        router = QueryRouter()
        analysis = QueryAnalysis(
            intent=QueryIntent.FACTOID,
            is_local_content=True,
            confidence=0.9,
        )

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.SIMPLE_SEARCH

    def test_factoid_with_low_confidence(self):
        """Test factoid with low confidence still uses simple search."""
        router = QueryRouter()
        analysis = QueryAnalysis(intent=QueryIntent.FACTOID, confidence=0.3)

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.SIMPLE_SEARCH

    def test_factoid_with_many_entities(self):
        """Test factoid with many entities still uses simple search."""
        router = QueryRouter()
        entities = [
            Entity(text=f"Entity{i}", type=EntityType.OTHER) for i in range(5)
        ]
        analysis = QueryAnalysis(
            intent=QueryIntent.FACTOID, entities=entities, confidence=0.9
        )

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.SIMPLE_SEARCH

    def test_unknown_intent_routing(self):
        """Test routing for unknown intent."""
        router = QueryRouter()
        analysis = QueryAnalysis(intent=QueryIntent.UNKNOWN, confidence=0.5)

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.HYBRID_SEARCH

    def test_task_oriented_routing(self):
        """Test routing for task-oriented queries."""
        router = QueryRouter()
        analysis = QueryAnalysis(
            intent=QueryIntent.TASK_ORIENTED, confidence=0.8
        )

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.HYBRID_SEARCH

    def test_definition_routing(self):
        """Test routing for definition queries."""
        router = QueryRouter()
        analysis = QueryAnalysis(
            intent=QueryIntent.DEFINITION, confidence=0.85
        )

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.HYBRID_SEARCH

    def test_opinion_routing(self):
        """Test routing for opinion queries."""
        router = QueryRouter()
        analysis = QueryAnalysis(intent=QueryIntent.OPINION, confidence=0.75)

        strategy = router.route(analysis)

        assert strategy == RetrievalStrategy.HYBRID_SEARCH

    def test_get_strategy_description(self):
        """Test getting strategy descriptions."""
        router = QueryRouter()

        desc = router.get_strategy_description(RetrievalStrategy.SIMPLE_SEARCH)
        assert "vector" in desc.lower() or "search" in desc.lower()

        desc = router.get_strategy_description(
            RetrievalStrategy.STATISTICAL_AGGREGATION
        )
        assert "aggregate" in desc.lower() or "statistics" in desc.lower()
