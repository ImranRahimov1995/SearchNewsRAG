"""Simple search handler - pure vector search without filters."""

from settings import get_logger

from rag_module.vector_store.protocols import IVectorStore

from ..protocols import SearchResult

logger = get_logger("simple_search_handler")


class SimpleSearchHandler:
    """Simple vector search handler.

    Performs pure semantic search without metadata filters or re-ranking.
    Returns top-k results based on vector similarity only.
    """

    def __init__(self, vector_store: IVectorStore):
        """Initialize simple search handler.

        Args:
            vector_store: Vector store instance for search
        """
        self.vector_store = vector_store

        logger.info("Initialized SimpleSearchHandler")

    def retrieve(
        self, query: str, entities: list, top_k: int = 10
    ) -> list[SearchResult]:
        """Retrieve documents using simple vector search.

        Args:
            query: Search query (already corrected/translated)
            entities: Extracted entities (NOT USED in simple search)
            top_k: Number of results to return

        Returns:
            List of search results sorted by similarity score
        """
        logger.info(f"Simple search: '{query[:50]}...' (top_k={top_k})")

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

        logger.debug(f"Found {len(search_results)} results")

        return search_results
