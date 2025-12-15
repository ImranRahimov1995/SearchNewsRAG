"""PostgreSQL-based news service."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rag_module.db.models import Article, Source


class PostgresNewsService:
    """Service for retrieving news from PostgreSQL database."""

    async def get_news_list(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get paginated news list from database.

        Args:
            session: Database session
            source_name: Filter by source name
            category: Filter by category
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of news articles with metadata
        """
        query = (
            select(Article)
            .join(Source)
            .order_by(Article.date.desc())
            .limit(limit)
            .offset(offset)
        )

        if source_name:
            query = query.where(Source.name == source_name)

        if category:
            query = query.where(Article.category == category)

        result = await session.execute(query)
        articles = result.scalars().all()

        return [
            {
                "id": article.id,
                "source_id": article.source_id,
                "url": article.url,
                "image_url": article.image_url,
                "date": article.date.isoformat() if article.date else None,
                "category": article.category,
                "short_preview": article.short_preview,
                "full_content": article.full_content,
                "summary": article.summary,
                "sentiment": article.sentiment,
                "sentiment_score": article.sentiment_score,
                "importance": article.importance,
                "is_breaking": article.is_breaking,
                "is_high_importance": article.is_high_importance,
                "created_at": article.created_at.isoformat(),
            }
            for article in articles
        ]

    async def get_categories_with_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all categories with document counts.

        Args:
            session: Database session
            source_name: Filter by source name

        Returns:
            List of categories with counts, sorted by count descending
        """
        query = (
            select(
                Article.category,
                func.count(Article.id).label("count"),
            )
            .join(Source)
            .where(Article.category.isnot(None))
            .group_by(Article.category)
            .order_by(func.count(Article.id).desc())
        )

        if source_name:
            query = query.where(Source.name == source_name)

        result = await session.execute(query)
        categories = result.all()

        return [
            {"category": cat.category, "count": cat.count}
            for cat in categories
        ]

    async def get_total_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
    ) -> int:
        """Get total number of articles.

        Args:
            session: Database session
            source_name: Filter by source name
            category: Filter by category

        Returns:
            Total count of articles matching filters
        """
        query = select(func.count(Article.id)).join(Source)

        if source_name:
            query = query.where(Source.name == source_name)

        if category:
            query = query.where(Article.category == category)

        result = await session.execute(query)
        return result.scalar_one()

    async def get_sources(
        self,
        session: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Get all available news sources.

        Args:
            session: Database session

        Returns:
            List of sources with metadata
        """
        query = select(Source).order_by(Source.name)

        result = await session.execute(query)
        sources = result.scalars().all()

        return [
            {
                "id": source.id,
                "name": source.name,
                "created_at": source.created_at.isoformat(),
            }
            for source in sources
        ]
