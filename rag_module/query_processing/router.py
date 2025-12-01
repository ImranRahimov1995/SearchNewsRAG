"""Query routing logic - maps intent to retrieval strategy."""

from settings import get_logger

from .protocols import QueryAnalysis, QueryIntent, RetrievalStrategy

logger = get_logger("query_router")


class QueryRouter:
    """Routes queries to appropriate retrieval strategies.

    Maps query intent and characteristics to optimal retrieval approach.
    Follows strategy pattern for extensibility.
    """

    INTENT_STRATEGY_MAP = {
        QueryIntent.FACTOID: RetrievalStrategy.SIMPLE_SEARCH,
        QueryIntent.DEFINITION: RetrievalStrategy.RAG_RETRIEVAL,
        QueryIntent.STATISTICAL: RetrievalStrategy.STATISTICAL_AGGREGATION,
        QueryIntent.ANALYTICAL: RetrievalStrategy.LLM_REASONING,
        QueryIntent.TASK_ORIENTED: RetrievalStrategy.TOOL_CALLING,
        QueryIntent.OPINION: RetrievalStrategy.LLM_REASONING,
        QueryIntent.LOCAL_AZ: RetrievalStrategy.LOCAL_SEARCH,
        QueryIntent.UNKNOWN: RetrievalStrategy.HYBRID_SEARCH,
    }

    def route(self, analysis: QueryAnalysis) -> RetrievalStrategy:
        """Determine optimal retrieval strategy for query.

        Args:
            analysis: Query analysis with intent and entities

        Returns:
            Recommended retrieval strategy
        """
        strategy = self.INTENT_STRATEGY_MAP.get(
            analysis.intent, RetrievalStrategy.HYBRID_SEARCH
        )

        strategy = self._refine_strategy(analysis, strategy)

        logger.info(
            f"Routed query: intent={analysis.intent} → strategy={strategy}"
        )

        return strategy

    def _refine_strategy(
        self, analysis: QueryAnalysis, base_strategy: RetrievalStrategy
    ) -> RetrievalStrategy:
        """Refine strategy based on query characteristics.

        Args:
            analysis: Query analysis
            base_strategy: Initial strategy from intent

        Returns:
            Refined strategy
        """
        if analysis.is_local_content:
            logger.debug("Local content detected - using LOCAL_SEARCH")
            return RetrievalStrategy.LOCAL_SEARCH

        if len(analysis.entities) > 3:
            logger.debug("Multiple entities - considering HYBRID_SEARCH")
            if base_strategy == RetrievalStrategy.SIMPLE_SEARCH:
                return RetrievalStrategy.HYBRID_SEARCH

        if (
            analysis.requires_temporal_filter
            and base_strategy != RetrievalStrategy.STATISTICAL_AGGREGATION
        ):
            logger.debug("Temporal filter needed - adjusting strategy")

        if analysis.confidence < 0.5:
            logger.warning(
                f"Low confidence ({analysis.confidence:.2f}) "
                f"- using HYBRID_SEARCH"
            )
            return RetrievalStrategy.HYBRID_SEARCH

        return base_strategy

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
