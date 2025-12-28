"""News services package."""

from .category import CategoryService
from .chroma import ChromaNewsService
from .entity import EntityService
from .facade import PostgresNewsService
from .graph import GraphService
from .news_list import NewsListService
from .protocols import (
    ICategoryService,
    IEntityService,
    IGraphService,
    INewsListService,
    ISourceService,
)
from .source import SourceService
from .update_news import NewsUpdateConfig, NewsUpdateOrchestrator

__all__ = [
    "CategoryService",
    "ChromaNewsService",
    "EntityService",
    "GraphService",
    "ICategoryService",
    "IEntityService",
    "IGraphService",
    "INewsListService",
    "ISourceService",
    "NewsListService",
    "PostgresNewsService",
    "SourceService",
    "NewsUpdateOrchestrator",
    "NewsUpdateConfig",
]
