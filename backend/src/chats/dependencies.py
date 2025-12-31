"""Dependency injection for chat service."""

import logging
from typing import Annotated

from cache import get_redis_cache
from config import get_settings
from dependencies import get_vector_store
from fastapi import Depends

from rag_module.cache import RedisCache
from rag_module.services.qa_service import QuestionAnsweringService
from rag_module.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)
settings = get_settings()


def get_qa_service(
    vector_store: Annotated[ChromaVectorStore, Depends(get_vector_store)],
    cache: Annotated[RedisCache, Depends(get_redis_cache)],
) -> QuestionAnsweringService:
    """Dependency injection for QA service.

    Args:
        vector_store: Shared vector store instance
        cache: Redis cache instance

    Returns:
        QuestionAnsweringService instance
    """
    return QuestionAnsweringService(
        vector_store=vector_store,
        llm_api_key=settings.openai_api_key,
        llm_model="gpt-4o-mini",
        temperature=0.3,
        top_k=settings.rag_top_k,
        cache=cache,
        cache_ttl=settings.cache_ttl,
        database_url=settings.database_url,
    )
