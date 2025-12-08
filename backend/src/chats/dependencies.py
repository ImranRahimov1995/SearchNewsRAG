"""Dependency injection for application services."""

import os
from typing import Annotated

from fastapi import Depends

from rag_module.services.qa_service import QuestionAnsweringService
from rag_module.vector_store import ChromaVectorStore
from rag_module.vector_store.embedding import LangChainEmbedding
from settings import get_logger

logger = get_logger("dependencies")


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
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY environment variable not set"
                )

            embedding = LangChainEmbedding(model="text-embedding-3-large")
            vector_store = ChromaVectorStore(
                collection_name="news_analyzed_0_5k_800_200_large",
                embedding=embedding,
            )

            self._qa_service = QuestionAnsweringService(
                vector_store=vector_store,
                llm_api_key=api_key,
                llm_model="gpt-4o-mini",
                temperature=0.3,
                top_k=5,
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
