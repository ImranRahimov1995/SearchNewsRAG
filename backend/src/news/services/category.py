"""Category service implementation."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from rag_module.db.models import Article, Source

from .protocols import ICategoryService


class CategoryService(ICategoryService):
    """Service for category operations."""

    async def get_categories_with_count(
        self,
        session: AsyncSession,
        source_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all categories with document counts."""
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

    async def get_category_tree(
        self,
        session: AsyncSession,
        limit_per_category: int = 20,
    ) -> dict[str, Any]:
        """Get hierarchical category tree with subcategories and news."""
        query = (
            select(Article)
            .options(
                selectinload(Article.subcategories),
                selectinload(Article.entities),
            )
            .where(Article.category.isnot(None))
            .order_by(Article.date.desc())
        )

        result = await session.execute(query)
        articles = result.scalars().all()

        category_map: dict[str, dict[str, Any]] = {}

        for article in articles:
            cat_name = article.category or "Uncategorized"

            if cat_name not in category_map:
                category_map[cat_name] = {
                    "name": cat_name,
                    "count": 0,
                    "subcategories": {},
                    "news": [],
                }

            category_map[cat_name]["count"] += 1

            entity_ids = (
                [e.id for e in article.entities] if article.entities else []
            )

            news_item = {
                "id": article.id,
                "title": (article.short_preview or article.full_content or "")[
                    :100
                ],
                "date": (
                    article.date.strftime("%Y-%m-%d %H:%M")
                    if article.date
                    else None
                ),
                "importance": article.importance,
                "entity_ids": entity_ids,
            }

            if article.subcategories:
                for subcat in article.subcategories:
                    if (
                        subcat.name
                        not in category_map[cat_name]["subcategories"]
                    ):
                        category_map[cat_name]["subcategories"][
                            subcat.name
                        ] = {
                            "name": subcat.name,
                            "news": [],
                        }
                    subcat_news = category_map[cat_name]["subcategories"][
                        subcat.name
                    ]["news"]
                    if len(subcat_news) < limit_per_category:
                        subcat_news.append(news_item)
            else:
                if len(category_map[cat_name]["news"]) < limit_per_category:
                    category_map[cat_name]["news"].append(news_item)

        categories = []
        for cat_data in sorted(
            category_map.values(), key=lambda x: x["count"], reverse=True
        ):
            categories.append(
                {
                    "name": cat_data["name"],
                    "count": cat_data["count"],
                    "subcategories": list(cat_data["subcategories"].values()),
                    "news": cat_data["news"],
                }
            )

        return {
            "categories": categories,
            "total_news": len(articles),
        }
