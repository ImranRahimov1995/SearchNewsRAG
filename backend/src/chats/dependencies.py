"""Dependency injection for application services."""

from typing import Annotated

from config import get_settings
from fastapi import Depends

from rag_module.config import get_logger
from rag_module.services.qa_service import QuestionAnsweringService
from rag_module.vector_store import ChromaVectorStore
from rag_module.vector_store.embedding import LangChainEmbedding

logger = get_logger("dependencies")
settings = get_settings()


class ServiceContainer:
    """Container for application services."""

    def __init__(self) -> None:
        """Initialize service container."""
        self._qa_service: QuestionAnsweringService | None = None

    @property
    def qa_service(self) -> QuestionAnsweringService:
        """Get or initialize QA service.

        Returns:
            Initialized QuestionAnsweringService instance

        Raises:
            RuntimeError: If OpenAI API key is not configured
        """
        if self._qa_service is None:
            if not settings.openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY environment variable not set"
                )

            embedding = LangChainEmbedding(model="text-embedding-3-large")

            if settings.chroma_host and settings.chroma_port:
                logger.info(
                    f"Using ChromaDB client mode: {settings.chroma_host}:{settings.chroma_port}"
                )
                vector_store = ChromaVectorStore(
                    collection_name=settings.chroma_collection_name,
                    embedding=embedding,
                    chroma_host=settings.chroma_host,
                    chroma_port=settings.chroma_port,
                )
            else:
                logger.info(
                    f"Using ChromaDB embedded mode: {settings.chroma_db_path}"
                )
                vector_store = ChromaVectorStore(
                    collection_name=settings.chroma_collection_name,
                    embedding=embedding,
                    persist_directory=settings.chroma_db_path,
                )

            self._qa_service = QuestionAnsweringService(
                vector_store=vector_store,
                llm_api_key=settings.openai_api_key,
                llm_model="gpt-4o-mini",
                temperature=0.3,
                top_k=settings.rag_top_k,
            )

            logger.info("QuestionAnsweringService initialized")

        return self._qa_service

    def cleanup(self) -> None:
        """Cleanup service resources."""
        if self._qa_service is not None:
            logger.info("Cleaning up QA service")
            self._qa_service = None


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


def get_qa_service(
    container: Annotated[ServiceContainer, Depends(get_container)],
) -> QuestionAnsweringService:
    """Dependency injection for QA service.

    Args:
        container: Service container

    Returns:
        QuestionAnsweringService instance
    """
    return container.qa_service
