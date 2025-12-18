"""Protocol definitions for news services."""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class INewsListService(ABC):
    """Interface for news list operations."""

    @abstractmethod
    async def get_news_list(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get paginated news list."""

    @abstractmethod
    async def get_total_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
    ) -> int:
        """Get total count of articles."""


class ICategoryService(ABC):
    """Interface for category operations."""

    @abstractmethod
    async def get_categories_with_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all categories with counts."""

    @abstractmethod
    async def get_category_tree(
        self,
        session: AsyncSession,
        limit_per_category: int = 20,
    ) -> dict[str, Any]:
        """Get hierarchical category tree."""


class IEntityService(ABC):
    """Interface for entity operations."""

    @abstractmethod
    async def get_entity_list(
        self,
        session: AsyncSession,
        min_news_count: int = 2,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get list of entities with news connections."""


class ISourceService(ABC):
    """Interface for source operations."""

    @abstractmethod
    async def get_sources(
        self,
        session: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Get all available news sources."""


class IGraphService(ABC):
    """Interface for graph visualization operations."""

    @abstractmethod
    async def get_graph_data(
        self,
        session: AsyncSession,
        category: str | None = None,
        entity_name: str | None = None,
        limit: int = 30,
    ) -> dict[str, Any]:
        """Get graph visualization data."""

    @abstractmethod
    async def get_entity_graph(
        self,
        session: AsyncSession,
        entity_id: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get graph of news connected by entities."""

    @abstractmethod
    async def get_news_by_ids(
        self,
        session: AsyncSession,
        news_ids: list[int],
    ) -> dict[str, Any]:
        """Get news graph by specific IDs."""
