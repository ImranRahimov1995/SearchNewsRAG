"""Retrieval pipeline - coordinates query processing and search."""

from dataclasses import dataclass

from settings import get_logger

from rag_module.query_processing import QueryPipeline, QueryProcessingResult
from rag_module.query_processing.protocols import RetrievalStrategy
from rag_module.vector_store.protocols import IVectorStore

from .handlers import SimpleSearchHandler, UnknownHandler
from .protocols import SearchResult

logger = get_logger("retrieval_pipeline")


@dataclass
class RetrievalResult:
    """Complete retrieval result.

    Contains query analysis and search results.
    """

    query_result: QueryProcessingResult
    search_results: list[SearchResult]
    handler_used: str

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses.

        Returns:
            Dictionary with all retrieval information
        """
        return {
            "query": {
                "original": self.query_result.raw_query,
                "corrected": self.query_result.processed.corrected,
                "language": self.query_result.processed.language,
                "intent": self.query_result.analysis.intent.value,
                "confidence": self.query_result.analysis.confidence,
                "entities": [
                    {
                        "text": e.text,
                        "type": e.type.value,
                        "normalized": e.normalized,
                    }
                    for e in self.query_result.analysis.entities
                ],
                "translated": self.query_result.analysis.metadata.get(
                    "translated_to_az", self.query_result.raw_query
                ),
            },
            "results": [
                {
                    "doc_id": r.doc_id,
                    "content": r.content[:200],
                    "full_content": r.content,
                    "score": r.score,
                    "category": r.metadata.get("category"),
                    "importance": r.metadata.get("importance"),
                }
                for r in self.search_results
            ],
            "handler_used": self.handler_used,
            "total_found": len(self.search_results),
        }


class RetrievalPipeline:
    """Complete retrieval pipeline.

    Coordinates:
    1. Query processing (understanding, translation, NER)
    2. Strategy routing
    3. Handler execution
    4. Result formatting
    """

    def __init__(
        self,
        vector_store: IVectorStore,
        query_pipeline: QueryPipeline | None = None,
    ):
        """Initialize retrieval pipeline.

        Args:
            vector_store: Vector store for search
            query_pipeline: Query processing pipeline (creates default if None)
        """
        self.query_pipeline = query_pipeline or QueryPipeline()

        self.simple_handler = SimpleSearchHandler(vector_store)
        self.unknown_handler = UnknownHandler(vector_store)

        logger.info("Initialized RetrievalPipeline")

    def search(self, query: str, top_k: int = 10) -> RetrievalResult:
        """Execute complete search pipeline.

        Args:
            query: User query (any language)
            top_k: Number of results to return

        Returns:
            Complete retrieval result
        """
        logger.info(f"Processing query: '{query[:100]}'")

        query_result = self.query_pipeline.process(query)

        search_query = query_result.get_search_query()
        entities = query_result.analysis.entities

        if query_result.strategy == RetrievalStrategy.SIMPLE_SEARCH:
            handler_name = "SimpleSearchHandler"
            search_results = self.simple_handler.retrieve(
                search_query, entities, top_k
            )
        else:
            handler_name = "UnknownHandler"
            search_results = self.unknown_handler.retrieve(
                search_query, entities, top_k
            )

        result = RetrievalResult(
            query_result=query_result,
            search_results=search_results,
            handler_used=handler_name,
        )

        logger.info(
            f"Search complete: handler={handler_name}, found={len(search_results)}"
        )

        return result
