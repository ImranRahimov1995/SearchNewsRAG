"""Tests for query processing pipeline."""

import pytest

from rag_module.query_processing.pipeline import (
    QueryPipeline,
    QueryProcessingResult,
)
from rag_module.query_processing.protocols import (
    ProcessedQuery,
    QueryAnalysis,
    QueryIntent,
    RetrievalStrategy,
)
from rag_module.query_processing.router import QueryRouter


class MockLLMProcessor:
    """Mock LLM processor for testing."""

    def process(self, query: str) -> tuple[ProcessedQuery, QueryAnalysis]:
        """Mock processing returning predefined results."""
        processed = ProcessedQuery(
            original=query,
            cleaned=query.lower(),
            corrected=query.lower(),
            language="az",
        )

        # Simple intent detection based on keywords
        intent = QueryIntent.FACTOID
        if "neçə" in query.lower() or "statistika" in query.lower():
            intent = QueryIntent.STATISTICAL
        elif "niyə" in query.lower() or "izah" in query.lower():
            intent = QueryIntent.ANALYTICAL

        analysis = QueryAnalysis(
            intent=intent,
            entities=[],
            confidence=0.8,
            keywords=query.lower().split(),
            is_local_content=False,
            requires_temporal_filter=False,
        )

        return processed, analysis


class TestQueryProcessingResult:
    """Test QueryProcessingResult functionality."""

    def test_get_search_query(self):
        """Test getting optimal search query."""
        result = QueryProcessingResult(
            raw_query="BAKI Harada?",
            processed=ProcessedQuery(
                original="BAKI Harada?",
                cleaned="baki harada",
                corrected="bakı harada",
            ),
            analysis=QueryAnalysis(intent=QueryIntent.FACTOID),
            strategy=RetrievalStrategy.SIMPLE_SEARCH,
        )

        assert result.get_search_query() == "bakı harada"

    def test_get_filter_hints(self):
        """Test getting filter hints."""
        result = QueryProcessingResult(
            raw_query="test",
            processed=ProcessedQuery(
                original="test", cleaned="test", corrected="test"
            ),
            analysis=QueryAnalysis(
                intent=QueryIntent.FACTOID,
                confidence=0.85,
                is_local_content=True,
                requires_temporal_filter=True,
            ),
            strategy=RetrievalStrategy.LOCAL_SEARCH,
        )

        hints = result.get_filter_hints()

        assert hints["use_temporal_filter"] is True
        assert hints["local_content_only"] is True
        assert hints["high_confidence"] is True

    def test_result_repr(self):
        """Test string representation."""
        result = QueryProcessingResult(
            raw_query="test",
            processed=ProcessedQuery(
                original="test", cleaned="test", corrected="test query"
            ),
            analysis=QueryAnalysis(
                intent=QueryIntent.FACTOID, confidence=0.75
            ),
            strategy=RetrievalStrategy.SIMPLE_SEARCH,
        )

        repr_str = repr(result)

        assert "test query" in repr_str
        assert "FACTOID" in repr_str  # Enum name, not value
        assert "0.75" in repr_str


class TestQueryPipeline:
    """Test QueryPipeline functionality."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization with defaults."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        assert pipeline.llm_processor is not None
        assert pipeline.router is not None

    def test_pipeline_with_custom_components(self):
        """Test pipeline with custom components."""
        mock_processor = MockLLMProcessor()
        router = QueryRouter()

        pipeline = QueryPipeline(llm_processor=mock_processor, router=router)

        assert pipeline.llm_processor == mock_processor
        assert pipeline.router == router

    def test_process_simple_query(self):
        """Test processing simple query."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        result = pipeline.process("Bakı harada yerləşir?")

        assert result.raw_query == "Bakı harada yerləşir?"
        assert result.processed.cleaned == "bakı harada yerləşir?"
        assert result.analysis.intent == QueryIntent.FACTOID
        assert result.strategy is not None

    def test_process_statistical_query(self):
        """Test processing statistical query."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        result = pipeline.process("Neçə nəfər iştirak etdi?")

        assert result.analysis.intent == QueryIntent.STATISTICAL
        assert result.strategy == RetrievalStrategy.STATISTICAL_AGGREGATION

    def test_process_analytical_query(self):
        """Test processing analytical query."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        result = pipeline.process("Niyə bu baş verdi?")

        assert result.analysis.intent == QueryIntent.ANALYTICAL
        assert result.strategy == RetrievalStrategy.LLM_REASONING

    def test_process_empty_query_raises(self):
        """Test processing empty query raises ValueError."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        with pytest.raises(ValueError, match="cannot be empty"):
            pipeline.process("")

    def test_process_whitespace_query_raises(self):
        """Test processing whitespace-only query raises."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        with pytest.raises(ValueError, match="cannot be empty"):
            pipeline.process("   ")

    def test_process_batch(self):
        """Test batch processing."""
        pipeline = QueryPipeline(llm_processor=MockLLMProcessor())

        queries = [
            "Bakı harada?",
            "Neçə nəfər?",
            "Niyə bu baş verdi?",
        ]

        results = pipeline.process_batch(queries)

        assert len(results) == 3
        assert all(isinstance(r, QueryProcessingResult) for r in results)
        assert results[0].analysis.intent == QueryIntent.FACTOID
        assert results[1].analysis.intent == QueryIntent.STATISTICAL
        assert results[2].analysis.intent == QueryIntent.ANALYTICAL

    def test_process_batch_with_errors(self):
        """Test batch processing handles errors gracefully."""

        class ErrorProcessor:
            def process(self, query: str):
                if "error" in query.lower():
                    raise ValueError("Test error")
                return MockLLMProcessor().process(query)

        pipeline = QueryPipeline(llm_processor=ErrorProcessor())

        queries = ["Good query", "ERROR query", "Another good"]

        results = pipeline.process_batch(queries)

        # Should skip the error query
        assert len(results) == 2
