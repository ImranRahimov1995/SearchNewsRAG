"""Entity service implementation."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rag_module.db.models import ArticleEntity, Entity

from .protocols import IEntityService


class EntityService(IEntityService):
    """Service for entity operations."""

    async def get_entity_list(
        self,
        session: AsyncSession,
        min_news_count: int = 2,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get list of entities with their connected news."""
        query = (
            select(
                Entity.id,
                Entity.text,
                Entity.type,
                func.count(ArticleEntity.article_id).label("news_count"),
                func.array_agg(ArticleEntity.article_id).label("news_ids"),
            )
            .join(ArticleEntity, Entity.id == ArticleEntity.entity_id)
            .group_by(Entity.id, Entity.text, Entity.type)
            .having(func.count(ArticleEntity.article_id) >= min_news_count)
            .order_by(func.count(ArticleEntity.article_id).desc())
            .limit(limit)
        )

        result = await session.execute(query)
        entities = result.all()

        return {
            "entities": [
                {
                    "id": e.id,
                    "name": e.text,
                    "type": e.type,
                    "news_count": e.news_count,
                    "news_ids": e.news_ids or [],
                }
                for e in entities
            ],
            "total": len(entities),
        }
