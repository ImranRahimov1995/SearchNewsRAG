"""Shared dependency injection for all services."""

import logging
from typing import Annotated

from config import get_settings
from fastapi import Depends

from rag_module.vector_store import ChromaVectorStore
from rag_module.vector_store.embedding import LangChainEmbedding

logger = logging.getLogger(__name__)
settings = get_settings()


class ServiceContainer:
    """Container for shared application resources."""

    def __init__(self) -> None:
        """Initialize service container."""
        self._vector_store: ChromaVectorStore | None = None

    @property
    def vector_store(self) -> ChromaVectorStore:
        """Get or initialize vector store.

        Returns:
            Initialized ChromaVectorStore instance

        Raises:
            RuntimeError: If OpenAI API key is not configured
        """
        if self._vector_store is None:
            if not settings.openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY environment variable not set"
                )

            embedding = LangChainEmbedding(model="text-embedding-3-large")

            if settings.chroma_host and settings.chroma_port:
                logger.info(
                    f"Using ChromaDB client mode: {settings.chroma_host}:{settings.chroma_port}"
                )
                self._vector_store = ChromaVectorStore(
                    collection_name=settings.chroma_collection_name,
                    embedding=embedding,
                    chroma_host=settings.chroma_host,
                    chroma_port=settings.chroma_port,
                )
            else:
                logger.info(
                    f"Using ChromaDB embedded mode: {settings.chroma_db_path}"
                )
                self._vector_store = ChromaVectorStore(
                    collection_name=settings.chroma_collection_name,
                    embedding=embedding,
                    persist_directory=settings.chroma_db_path,
                )

            logger.info("ChromaVectorStore initialized")

        return self._vector_store

    def cleanup(self) -> None:
        """Cleanup service resources."""
        if self._vector_store is not None:
            logger.info("Cleaning up vector store")
            self._vector_store = None


_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    """Get global service container.

    Returns:
        ServiceContainer instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def get_vector_store(
    container: Annotated[ServiceContainer, Depends(get_container)],
) -> ChromaVectorStore:
    """Dependency injection for vector store.

    Args:
        container: Service container

    Returns:
        ChromaVectorStore instance
    """
    return container.vector_store
