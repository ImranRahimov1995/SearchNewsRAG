"""Query processing pipeline - orchestrates all query understanding steps."""

from dataclasses import dataclass

from rag_module.config import get_logger

from .llm_processor import LLMQueryProcessor
from .protocols import ProcessedQuery, QueryAnalysis, RetrievalStrategy
from .router import QueryRouter

logger = get_logger("query_pipeline")


@dataclass
class QueryProcessingResult:
    """Complete query processing result.

    Contains all information needed for retrieval and generation:
    - Original and processed query text
    - Intent and entity analysis
    - Recommended retrieval strategy
    """

    raw_query: str

    processed: ProcessedQuery

    analysis: QueryAnalysis

    strategy: RetrievalStrategy

    def get_search_query(self) -> str:
        """Get optimal query text for search.

        Returns corrected query for best search results.

        Returns:
            Corrected query text
        """
        return self.processed.corrected

    def get_filter_hints(self) -> dict[str, bool]:
        """Get filtering hints for retrieval.

        Returns:
            Dictionary with filter recommendations
        """
        return {
            "use_temporal_filter": self.analysis.requires_temporal_filter,
            "local_content_only": self.analysis.is_local_content,
            "high_confidence": self.analysis.confidence > 0.7,
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"QueryProcessingResult(\n"
            f"  query='{self.processed.corrected}',\n"
            f"  intent={self.analysis.intent},\n"
            f"  strategy={self.strategy},\n"
            f"  confidence={self.analysis.confidence:.2f},\n"
            f"  entities={len(self.analysis.entities)}\n"
            f")"
        )


class QueryPipeline:
    """Complete query understanding pipeline.

    Orchestrates the full query processing flow:
    1. LLM processing (clean, correct, NER, classify)
    2. Strategy routing
    3. Result packaging

    This is the main entry point for query processing.
    """

    def __init__(
        self,
        llm_processor: LLMQueryProcessor | None = None,
        router: QueryRouter | None = None,
    ):
        """Initialize query pipeline.

        Args:
            llm_processor: LLM processor instance (creates default if None)
            router: Query router instance (creates default if None)
        """
        self.llm_processor = llm_processor or LLMQueryProcessor()
        self.router = router or QueryRouter()

        logger.info("Initialized QueryPipeline")

    def process(self, query: str) -> QueryProcessingResult:
        """Process user query through complete pipeline.

        This is the main method - takes raw query, returns everything
        needed for retrieval and generation.

        Args:
            query: Raw user query string

        Returns:
            Complete processing result with strategy

        Raises:
            ValueError: If query is empty or invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        logger.info(f"Processing query: '{query[:100]}'")

        processed, analysis = self.llm_processor.process(query)

        logger.debug(
            f"LLM processing complete: "
            f"corrected='{processed.corrected}', "
            f"intent={analysis.intent}"
        )

        strategy = self.router.route(analysis)

        logger.debug(f"Routed to strategy: {strategy}")

        result = QueryProcessingResult(
            raw_query=query,
            processed=processed,
            analysis=analysis,
            strategy=strategy,
        )

        logger.info(
            f"Query processing complete: "
            f"intent={analysis.intent}, "
            f"strategy={strategy}, "
            f"confidence={analysis.confidence:.2f}"
        )

        return result

    def process_batch(self, queries: list[str]) -> list[QueryProcessingResult]:
        """Process multiple queries in batch.

        Args:
            queries: List of raw query strings

        Returns:
            List of processing results
        """
        logger.info(f"Processing batch of {len(queries)} queries")

        results = []
        for query in queries:
            try:
                result = self.process(query)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                continue

        logger.info(
            f"Batch processing complete: {len(results)}/{len(queries)}"
        )

        return results
