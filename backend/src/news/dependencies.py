"""Dependencies for news module."""

from typing import Annotated

from dependencies import get_vector_store
from fastapi import Depends

from rag_module.vector_store import ChromaVectorStore

from .service import NewsService


def get_news_service(
    vector_store: Annotated[ChromaVectorStore, Depends(get_vector_store)],
) -> NewsService:
    """Get news service instance.

    Args:
        vector_store: Shared vector store instance

    Returns:
        Initialized NewsService instance
    """
    return NewsService(vector_store=vector_store)
