"""Graph visualization service implementation."""

import math
import random
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from rag_module.db.models import Article, ArticleEntity, Entity

from .protocols import IGraphService


class GraphService(IGraphService):
    """Service for graph visualization operations."""

    async def get_graph_data(
        self,
        session: AsyncSession,
        category: str | None = None,
        entity_name: str | None = None,
        limit: int = 30,
    ) -> dict[str, Any]:
        """Get graph visualization data for news network."""
        query = (
            select(Article)
            .options(
                selectinload(Article.entities),
                selectinload(Article.source),
            )
            .order_by(Article.date.desc())
            .limit(limit)
        )

        if category:
            query = query.where(Article.category == category.lower().strip())

        if entity_name:
            entity_subquery = (
                select(ArticleEntity.article_id)
                .join(Entity)
                .where(Entity.text == entity_name)
            )
            query = query.where(Article.id.in_(entity_subquery))

        result = await session.execute(query)
        articles = list(result.scalars().all())

        nodes, entity_to_articles = self._build_nodes(articles)
        edges = self._build_edges_by_entities(entity_to_articles)
        filtered_entities = {
            eid for eid, aids in entity_to_articles.items() if len(aids) >= 2
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "total_news": len(articles),
            "total_entities": len(filtered_entities),
        }

    async def get_entity_graph(
        self,
        session: AsyncSession,
        entity_id: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get graph of news connected by shared entities."""
        news_ids: list[int] = []
        if entity_id:
            article_ids_query = select(ArticleEntity.article_id).where(
                ArticleEntity.entity_id == entity_id
            )
            article_ids_result = await session.execute(article_ids_query)
            news_ids = [row[0] for row in article_ids_result.all()]

        query = (
            select(Article)
            .options(
                selectinload(Article.entities),
                selectinload(Article.source),
            )
            .order_by(Article.date.desc())
            .limit(limit)
        )

        if news_ids:
            query = query.where(Article.id.in_(news_ids))

        result = await session.execute(query)
        articles = list(result.scalars().all())

        return self._build_entity_connected_graph(articles)

    async def get_news_by_ids(
        self,
        session: AsyncSession,
        news_ids: list[int],
    ) -> dict[str, Any]:
        """Get news graph by specific IDs connected by shared entities."""
        query = (
            select(Article)
            .options(
                selectinload(Article.entities),
                selectinload(Article.source),
            )
            .where(Article.id.in_(news_ids))
            .order_by(Article.date.desc())
        )

        result = await session.execute(query)
        articles = list(result.scalars().all())

        return self._build_entity_connected_graph(articles)

    def _build_nodes(
        self, articles: list[Article]
    ) -> tuple[list[dict[str, Any]], dict[int, list[int]]]:
        """Build graph nodes from articles."""
        nodes: list[dict[str, Any]] = []
        entity_to_articles: dict[int, list[int]] = {}

        total = len(articles)
        cols = max(3, int(math.ceil(math.sqrt(total))))

        for idx, article in enumerate(articles):
            x_pct, y_pct = self._calculate_position(idx, cols, total)
            node = self._create_node(article, x_pct, y_pct)
            nodes.append(node)

            if article.entities:
                for entity in article.entities:
                    if entity.id not in entity_to_articles:
                        entity_to_articles[entity.id] = []
                    entity_to_articles[entity.id].append(article.id)

        return nodes, entity_to_articles

    def _build_edges_by_entities(
        self, entity_to_articles: dict[int, list[int]]
    ) -> list[dict[str, Any]]:
        """Build edges based on shared entities."""
        edges: list[dict[str, Any]] = []
        edge_set: set[tuple[int, int]] = set()

        for article_ids in entity_to_articles.values():
            if len(article_ids) < 2:
                continue
            for i, aid1 in enumerate(article_ids):
                for aid2 in article_ids[i + 1 :]:
                    pair = (min(aid1, aid2), max(aid1, aid2))
                    if pair not in edge_set:
                        edge_set.add(pair)
                        edges.append(
                            {
                                "id": f"edge-{pair[0]}-{pair[1]}",
                                "from": f"news-{pair[0]}",
                                "to": f"news-{pair[1]}",
                                "label": None,
                                "strength": 2,
                            }
                        )

        return edges

    def _build_entity_connected_graph(
        self, articles: list[Article]
    ) -> dict[str, Any]:
        """Build graph with nodes connected by shared entities."""
        nodes: list[dict[str, Any]] = []
        article_entities: dict[int, set[int]] = {}
        entity_id_to_name: dict[int, str] = {}

        total = len(articles)
        cols = max(3, int(math.ceil(math.sqrt(total))))

        for idx, article in enumerate(articles):
            x_pct, y_pct = self._calculate_position(idx, cols, total)
            node = self._create_node(article, x_pct, y_pct)
            nodes.append(node)

            entity_ids = (
                {e.id for e in article.entities} if article.entities else set()
            )
            article_entities[article.id] = entity_ids

            if article.entities:
                for e in article.entities:
                    entity_id_to_name[e.id] = e.text

        edges = self._build_labeled_edges(
            list(articles), article_entities, entity_id_to_name
        )

        total_entities = (
            len(set().union(*article_entities.values()))
            if article_entities
            else 0
        )

        return {
            "nodes": nodes,
            "edges": edges,
            "total_news": len(articles),
            "total_entities": total_entities,
        }

    def _build_labeled_edges(
        self,
        articles: list[Article],
        article_entities: dict[int, set[int]],
        entity_id_to_name: dict[int, str],
    ) -> list[dict[str, Any]]:
        """Build edges with entity name labels."""
        edges: list[dict[str, Any]] = []

        for i in range(len(articles)):
            for j in range(i + 1, len(articles)):
                a1, a2 = articles[i], articles[j]
                shared = article_entities.get(
                    a1.id, set()
                ) & article_entities.get(a2.id, set())
                if shared:
                    shared_names = [
                        entity_id_to_name.get(eid, "")
                        for eid in list(shared)[:3]
                    ]
                    label = ", ".join([n for n in shared_names if n])
                    edges.append(
                        {
                            "id": f"edge-{a1.id}-{a2.id}",
                            "from": f"news-{a1.id}",
                            "to": f"news-{a2.id}",
                            "label": label or f"{len(shared)} shared",
                            "strength": min(3, len(shared)),
                        }
                    )

        return edges

    def _calculate_position(
        self, idx: int, cols: int, total: int
    ) -> tuple[float, float]:
        """Calculate node position with jitter."""
        row = idx // cols
        col = idx % cols
        x_pct = 10 + (col * 80 / max(1, cols - 1)) if cols > 1 else 50
        y_pct = (
            10 + (row * 80 / max(1, (total - 1) // cols))
            if total > cols
            else 50
        )

        jitter_x = random.uniform(-3, 3)  # nosec B311
        jitter_y = random.uniform(-3, 3)  # nosec B311
        x_pct = max(5, min(95, x_pct + jitter_x))
        y_pct = max(5, min(95, y_pct + jitter_y))

        return x_pct, y_pct

    def _create_node(
        self, article: Article, x_pct: float, y_pct: float
    ) -> dict[str, Any]:
        """Create a graph node from article."""
        entity_names = (
            [e.text for e in article.entities[:5]] if article.entities else []
        )

        return {
            "id": f"news-{article.id}",
            "kind": "event" if article.is_high_importance else "news",
            "title": (
                article.summary
                or article.short_preview
                or article.full_content
                or ""
            )[:80],
            "subtitle": (article.full_content or article.short_preview or ""),
            "meta": {
                "source": article.source.name if article.source else None,
                "date": (
                    article.date.strftime("%Y-%m-%d %H:%M")
                    if article.date
                    else None
                ),
                "sentiment": article.sentiment,
                "importance": article.importance,
                "tags": [article.category] if article.category else [],
                "entities": entity_names,
                "category": article.category,
                "url": article.url,
            },
            "pos": {"xPct": round(x_pct, 1), "yPct": round(y_pct, 1)},
        }
