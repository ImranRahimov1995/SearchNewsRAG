"""Relational persistence layer for news data."""

from .database import create_session_factory
from .models import (
    Article,
    ArticleEntity,
    ArticleKeyword,
    ArticleSubcategory,
    ArticleTopic,
    Base,
    Chunk,
    Entity,
    Keyword,
    Source,
    Subcategory,
    Topic,
)
from .repository import NewsDataRepository

__all__ = [
    "create_session_factory",
    "NewsDataRepository",
    "Base",
    "Source",
    "Article",
    "Chunk",
    "Entity",
    "Keyword",
    "Subcategory",
    "Topic",
    "ArticleEntity",
    "ArticleKeyword",
    "ArticleSubcategory",
    "ArticleTopic",
]
