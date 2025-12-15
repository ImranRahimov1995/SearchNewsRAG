"""Dependencies for news module."""

from typing import Annotated

from dependencies import get_vector_store
from fastapi import Depends

from rag_module.vector_store import ChromaVectorStore

from .services import ChromaNewsService, PostgresNewsService


def get_chroma_service(
    vector_store: Annotated[ChromaVectorStore, Depends(get_vector_store)],
) -> ChromaNewsService:
    """Get ChromaDB news service instance.

    Args:
        vector_store: Shared vector store instance

    Returns:
        Initialized ChromaNewsService instance
    """
    return ChromaNewsService(vector_store=vector_store)


def get_postgres_service() -> PostgresNewsService:
    """Get PostgreSQL news service instance.

    Returns:
        PostgresNewsService instance
    """
    return PostgresNewsService()
