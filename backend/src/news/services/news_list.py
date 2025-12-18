"""News list service implementation."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rag_module.db.models import Article, Source

from .protocols import INewsListService


class NewsListService(INewsListService):
    """Service for retrieving paginated news lists."""

    async def get_news_list(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get paginated news list from database."""
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
            query = query.where(Article.category == category.lower().strip())

        result = await session.execute(query)
        articles = result.scalars().all()

        return [self._serialize_article(article) for article in articles]

    async def get_total_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
        category: str | None = None,
    ) -> int:
        """Get total number of articles."""
        query = select(func.count(Article.id)).join(Source)

        if source_name:
            query = query.where(Source.name == source_name)

        if category:
            query = query.where(Article.category == category.lower().strip())

        result = await session.execute(query)
        return result.scalar_one()

    def _serialize_article(self, article: Article) -> dict[str, Any]:
        """Serialize article to dictionary."""
        return {
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
