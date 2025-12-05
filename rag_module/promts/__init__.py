"""Prompts for various RAG module operations."""

from .news_analyzer_prompts import (
    ANALYZER_SYSTEM_PROMPT,
    ANALYZER_USER_PROMPT_TEMPLATE,
)
from .query_analyzer_prompts import (
    QUERY_ANALYZER_SYSTEM_PROMPT,
    QUERY_ANALYZER_USER_PROMPT,
)

__all__ = [
    "ANALYZER_SYSTEM_PROMPT",
    "ANALYZER_USER_PROMPT_TEMPLATE",
    "QUERY_ANALYZER_SYSTEM_PROMPT",
    "QUERY_ANALYZER_USER_PROMPT",
]
