"""Query routing logic - maps intent to retrieval strategy."""

from settings import get_logger

from .protocols import QueryAnalysis, QueryIntent, RetrievalStrategy

logger = get_logger("query_router")


class QueryRouter:
    """Routes queries to appropriate retrieval strategies.

    Simplified routing: only FACTOID → SIMPLE_SEARCH, everything else → UNKNOWN.
    """

    def route(self, analysis: QueryAnalysis) -> RetrievalStrategy:
        """Determine optimal retrieval strategy for query.

        Args:
            analysis: Query analysis with intent and entities

        Returns:
            Recommended retrieval strategy (SIMPLE_SEARCH or HYBRID_SEARCH)
        """
        if analysis.intent == QueryIntent.FACTOID:
            strategy = RetrievalStrategy.SIMPLE_SEARCH
        else:
            strategy = RetrievalStrategy.HYBRID_SEARCH

        logger.info(
            f"Routed query: intent={analysis.intent} → strategy={strategy}"
        )

        return strategy

    def get_strategy_description(self, strategy: RetrievalStrategy) -> str:
        """Get human-readable strategy description.

        Args:
            strategy: Retrieval strategy

        Returns:
            Description of what the strategy does
        """
        descriptions = {
            RetrievalStrategy.SIMPLE_SEARCH: (
                "Basic vector/keyword search in document database"
            ),
            RetrievalStrategy.STATISTICAL_AGGREGATION: (
                "Aggregate and count data, compute statistics"
            ),
            RetrievalStrategy.RAG_RETRIEVAL: (
                "Retrieve relevant documents and generate answer"
            ),
            RetrievalStrategy.TOOL_CALLING: (
                "Execute specific tool or function"
            ),
            RetrievalStrategy.LLM_REASONING: (
                "Pure LLM generation with reasoning"
            ),
            RetrievalStrategy.HYBRID_SEARCH: (
                "Combine multiple search strategies"
            ),
            RetrievalStrategy.LOCAL_SEARCH: (
                "Search in Azerbaijan-specific data sources"
            ),
        }

        return descriptions.get(strategy, "Unknown strategy")
