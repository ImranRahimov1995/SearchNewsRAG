"""Service for news operations."""

import logging
from collections import Counter
from typing import Any

from rag_module.vector_store import ChromaVectorStore

from .filters import calculate_date_threshold
from .schemas import DateFilter, SortOrder
from .utils import parse_date, sort_by_date

logger = logging.getLogger(__name__)


class ChromaNewsService:
    """Service for retrieving news data from vector store."""

    def __init__(self, vector_store: ChromaVectorStore) -> None:
        """Initialize news service.

        Args:
            vector_store: ChromaDB vector store instance
        """
        self._vector_store = vector_store
        self._collection = vector_store._collection

    def get_categories(self) -> dict[str, Any]:
        """Get all categories with document counts.

        Returns:
            Dictionary with categories list and total count

        Raises:
            RuntimeError: If failed to retrieve categories
        """
        try:
            logger.info("Retrieving categories from vector store")

            results = self._collection.get(include=["metadatas"])

            if not results or not results.get("metadatas"):
                logger.warning("No documents found")
                return {"categories": [], "total_documents": 0}

            metadatas = results.get("metadatas", [])
            if not metadatas:
                return {"categories": [], "total_documents": 0}

            categories = [
                meta.get("category", "unknown")
                for meta in metadatas
                if meta and isinstance(meta, dict)
            ]

            category_counts = Counter(categories)
            categories_list = [
                {"category": cat, "count": cnt}
                for cat, cnt in sorted(
                    category_counts.items(), key=lambda x: x[1], reverse=True
                )
            ]

            logger.info(
                f"Retrieved {len(categories_list)} categories "
                f"from {len(metadatas)} documents"
            )

            return {
                "categories": categories_list,
                "total_documents": len(metadatas),
            }

        except Exception as e:
            logger.error(f"Failed to retrieve categories: {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve categories: {e}") from e

    def get_news(
        self,
        date_filter: DateFilter = DateFilter.ALL,
        sort_order: SortOrder = SortOrder.DESC,
    ) -> list[dict[str, Any]]:
        """Get news filtered by date and sorted.

        Args:
            date_filter: Date filter option
            sort_order: Sort order for results

        Returns:
            List of news items

        Raises:
            RuntimeError: If failed to retrieve news
        """
        try:
            logger.info(
                f"Retrieving news: filter={date_filter}, sort={sort_order}"
            )

            results = self._collection.get(include=["metadatas", "documents"])

            if not results or not results.get("metadatas"):
                logger.info("No documents found")
                return []

            metadatas = results.get("metadatas", [])
            documents = results.get("documents", [])
            ids = results.get("ids", [])

            if not metadatas or not documents or not ids:
                return []

            threshold = calculate_date_threshold(date_filter)

            news_items = []
            for i, meta in enumerate(metadatas):
                if not isinstance(meta, dict):
                    continue

                if threshold:
                    date_value = meta.get("date")
                    if isinstance(date_value, str):
                        doc_date = parse_date(date_value)
                        if not doc_date or doc_date < threshold:
                            continue
                    else:
                        continue

                news_items.append(
                    {
                        "id": ids[i] if i < len(ids) else "",
                        "content": documents[i] if i < len(documents) else "",
                        "category": meta.get("category"),
                        "date": meta.get("date"),
                        "importance": meta.get("importance"),
                    }
                )

            sorted_news = sort_by_date(
                news_items, descending=(sort_order == SortOrder.DESC)
            )

            logger.info(
                f"Retrieved {len(sorted_news)} news items "
                f"(filtered from {len(metadatas)} total)"
            )

            return sorted_news

        except Exception as e:
            logger.error(f"Failed to retrieve news: {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve news: {e}") from e
