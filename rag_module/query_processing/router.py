"""Query routing logic - maps intent to retrieval strategy."""

import logging

from .protocols import QueryAnalysis, QueryIntent, RetrievalStrategy

logger = logging.getLogger(__name__)


class QueryRouter:
    """Routes queries to appropriate retrieval strategies.

    Maps query intents to specific retrieval strategies.
    """

    def route(self, analysis: QueryAnalysis) -> RetrievalStrategy:
        """Determine optimal retrieval strategy for query.

        Args:
            analysis: Query analysis with intent and entities

        Returns:
            Recommended retrieval strategy
        """
        intent_mapping = {
            QueryIntent.FACTOID: RetrievalStrategy.SIMPLE_SEARCH,
            QueryIntent.STATISTICS: RetrievalStrategy.STATISTICS_QUERY,
            QueryIntent.PREDICTION: RetrievalStrategy.PREDICTION_QUERY,
            QueryIntent.TALK: RetrievalStrategy.STATIC_RESPONSE,
            QueryIntent.ATTACKING: RetrievalStrategy.REJECT,
            QueryIntent.STATISTICAL: RetrievalStrategy.STATISTICS_QUERY,
            QueryIntent.ANALYTICAL: RetrievalStrategy.HYBRID_SEARCH,
        }

        strategy = intent_mapping.get(
            analysis.intent, RetrievalStrategy.HYBRID_SEARCH
        )

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
            RetrievalStrategy.STATISTICS_QUERY: (
                "SQL-based statistical analysis and aggregation"
            ),
            RetrievalStrategy.PREDICTION_QUERY: (
                "Generate predictions based on historical data"
            ),
            RetrievalStrategy.STATIC_RESPONSE: (
                "Return pre-defined response without search"
            ),
            RetrievalStrategy.REJECT: (
                "Reject malicious or inappropriate request"
            ),
        }

        return descriptions.get(strategy, "Unknown strategy")
