"""Source service implementation."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rag_module.db.models import Source

from .protocols import ISourceService


class SourceService(ISourceService):
    """Service for source operations."""

    async def get_sources(
        self,
        session: AsyncSession,
    ) -> list[dict[str, Any]]:
        """Get all available news sources."""
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
