"""Unknown query handler - fallback to simple search."""

from settings import get_logger

from rag_module.vector_store.protocols import IVectorStore

from ..protocols import SearchResult

logger = get_logger("unknown_handler")


class UnknownHandler:
    """Handler for unknown/unclear queries.

    Falls back to simple vector search when query intent is unclear.
    Same as SimpleSearchHandler but with different logging.
    """

    def __init__(self, vector_store: IVectorStore):
        """Initialize unknown query handler.

        Args:
            vector_store: Vector store instance for search
        """
        self.vector_store = vector_store

        logger.info("Initialized UnknownHandler")

    def retrieve(
        self, query: str, entities: list, top_k: int = 10
    ) -> list[SearchResult]:
        """Retrieve documents for unknown query type.

        Falls back to simple vector search.

        Args:
            query: Search query
            entities: Extracted entities (ignored)
            top_k: Number of results to return

        Returns:
            List of search results
        """
        logger.warning(
            f"Unknown query intent, using fallback search: '{query[:50]}...'"
        )

        results = self.vector_store.search(
            query=query, top_k=top_k, filters=None
        )

        search_results = []
        for r in results:
            search_results.append(
                SearchResult(
                    doc_id=r.document.metadata.get("doc_id", "unknown"),
                    content=r.document.metadata.get("full_content", r.document.content),
                    score=r.score,
                    metadata=r.document.metadata,
                )
            )

        logger.debug(f"Fallback search found {len(search_results)} results")

        return search_results
