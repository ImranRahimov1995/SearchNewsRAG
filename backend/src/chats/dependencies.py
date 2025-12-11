"""Dependency injection for chat service."""

from typing import Annotated

from config import get_settings
from dependencies import get_vector_store
from fastapi import Depends

from rag_module.config import get_logger
from rag_module.services.qa_service import QuestionAnsweringService
from rag_module.vector_store import ChromaVectorStore

logger = get_logger("chats.dependencies")
settings = get_settings()


def get_qa_service(
    vector_store: Annotated[ChromaVectorStore, Depends(get_vector_store)],
) -> QuestionAnsweringService:
    """Dependency injection for QA service.

    Args:
        vector_store: Shared vector store instance

    Returns:
        QuestionAnsweringService instance
    """
    return QuestionAnsweringService(
        vector_store=vector_store,
        llm_api_key=settings.openai_api_key,
        llm_model="gpt-4o-mini",
        temperature=0.3,
        top_k=settings.rag_top_k,
    )
