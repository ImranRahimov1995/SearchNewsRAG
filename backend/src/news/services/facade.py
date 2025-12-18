"""Facade combining all news services for backward compatibility."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from .category import CategoryService
from .entity import EntityService
from .graph import GraphService
from .news_list import NewsListService
from .source import SourceService


class PostgresNewsService:
    """Facade service combining all news operations.

    This class maintains backward compatibility by delegating to
    specialized services that follow Single Responsibility Principle.
    """

    def __init__(self) -> None:
        """Initialize with specialized services."""
        self._news_list = NewsListService()
        self._category = CategoryService()
        self._entity = EntityService()
        self._source = SourceService()
        self._graph = GraphService()

    async def get_news_list(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get paginated news list from database."""
        return await self._news_list.get_news_list(
            session, source_name, category, limit, offset
        )

    async def get_total_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
    ) -> int:
        """Get total number of articles."""
        return await self._news_list.get_total_count(
            session, source_name, category
        )

    async def get_categories_with_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all categories with document counts."""
        return await self._category.get_categories_with_count(
            session, source_name
        )

    async def get_category_tree(
        self,
        session: AsyncSession,
        limit_per_category: int = 20,
    ) -> dict[str, Any]:
        """Get hierarchical category tree."""
        return await self._category.get_category_tree(
            session, limit_per_category
        )

    async def get_entity_list(
        self,
        session: AsyncSession,
        min_news_count: int = 2,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get list of entities with news connections."""
        return await self._entity.get_entity_list(
            session, min_news_count, limit
        )

    async def get_sources(
        self,
        session: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Get all available news sources."""
        return await self._source.get_sources(session)

    async def get_graph_data(
        self,
        session: AsyncSession,
        category: str | None = None,
        entity_name: str | None = None,
        limit: int = 30,
    ) -> dict[str, Any]:
        """Get graph visualization data."""
        return await self._graph.get_graph_data(
            session, category, entity_name, limit
        )

    async def get_entity_graph(
        self,
        session: AsyncSession,
        entity_id: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get graph of news connected by entities."""
        return await self._graph.get_entity_graph(session, entity_id, limit)

    async def get_news_by_ids(
        self,
        session: AsyncSession,
        news_ids: list[int],
    ) -> dict[str, Any]:
        """Get news graph by specific IDs."""
        return await self._graph.get_news_by_ids(session, news_ids)
