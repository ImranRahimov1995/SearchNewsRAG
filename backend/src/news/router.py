"""Router for news endpoints."""

import logging
from datetime import datetime
from typing import Annotated

from database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pagination import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_postgres_service
from .schemas import (
    CategoriesResponse,
    CategoryTreeResponse,
    EntityListResponse,
    GraphResponse,
    NewsItem,
    NewsListResponse,
)
from .services import PostgresNewsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    source: str | None = Query(None, description="Filter by source name"),
) -> dict:
    """Get all news categories with document counts from PostgreSQL.

    Args:
        session: Database session
        service: PostgreSQL news service
        source: Optional source name filter

    Returns:
        List of categories with their document counts

    Raises:
        HTTPException: If failed to retrieve categories
    """
    try:
        logger.info(f"Fetching categories from DB, source={source}")

        categories = await service.get_categories_with_count(
            session, source_name=source
        )
        total = sum(cat["count"] for cat in categories)

        logger.info(
            f"Categories retrieved: {len(categories)} categories, {total} total documents"
        )

        return {"categories": categories, "total_documents": total}

    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}",
        ) from e


def _map_news_item(item: dict) -> NewsItem:
    """Map DB dict to NewsItem schema.

    Args:
        item: Raw DB dict

    Returns:
        NewsItem instance
    """
    date_val = item.get("date")
    date_obj: datetime | None = None
    if isinstance(date_val, str):
        try:
            date_obj = datetime.fromisoformat(date_val)
        except Exception:
            date_obj = None
    elif isinstance(date_val, datetime):
        date_obj = date_val

    return NewsItem(
        id=str(item["id"]),
        content=item.get("full_content") or item.get("short_preview") or "",
        category=item.get("category"),
        date=date_obj,
        importance=item.get("importance"),
    )


@router.get("/", response_model=NewsListResponse)
async def get_news(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    source: str | None = Query(None, description="Filter by source name"),
    category: str | None = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(
        20, ge=1, le=100, description="Items per page (max 100)"
    ),
) -> dict:
    """Get paginated news list from PostgreSQL.

    Args:
        request: FastAPI request object for building URLs
        session: Database session
        service: PostgreSQL news service
        source: Optional source name filter
        category: Optional category filter
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated list with count, next, previous, and results

    Raises:
        HTTPException: If failed to retrieve news
    """
    try:
        logger.info(
            f"Fetching news: source={source}, category={category}, "
            f"page={page}, page_size={page_size}"
        )

        offset = (page - 1) * page_size
        news = await service.get_news_list(
            session,
            source_name=source,
            category=category,
            limit=page_size,
            offset=offset,
        )

        total = await service.get_total_count(
            session, source_name=source, category=category
        )

        base_url = str(request.url_for("get_news"))
        query_params: dict[str, str | int] = {"page_size": page_size}
        if source:
            query_params["source"] = source
        if category:
            query_params["category"] = category

        mapped_news = [_map_news_item(n) for n in news]

        paginated = paginate(
            items=mapped_news,
            page=page,
            page_size=page_size,
            base_url=base_url,
            query_params=query_params,
            total=total,
        )

        response = {
            "count": paginated["count"],
            "next": paginated["next"],
            "previous": paginated["previous"],
            "results": {"news": paginated["results"]},
        }

        logger.info(
            f"News retrieved: {len(mapped_news)} items (page {page}, total {total})"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to fetch news: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news: {str(e)}",
        ) from e


@router.get("/graph", response_model=GraphResponse)
async def get_news_graph(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    category: str | None = Query(None, description="Filter by category"),
    entity: str | None = Query(None, description="Filter by entity name"),
    limit: int = Query(
        30, ge=5, le=100, description="Max news items in graph"
    ),
) -> dict:
    """Get news graph data for visualization.

    Returns nodes (news articles + entities) and edges (connections).

    Args:
        session: Database session
        service: PostgreSQL news service
        category: Optional category filter
        entity: Optional entity name filter
        limit: Maximum number of news items

    Returns:
        Graph data with nodes and edges for visualization

    Raises:
        HTTPException: If failed to retrieve graph data
    """
    try:
        logger.info(
            f"Fetching graph data: category={category}, entity={entity}, limit={limit}"
        )

        graph_data = await service.get_graph_data(
            session,
            category=category,
            entity_name=entity,
            limit=limit,
        )

        logger.info(
            f"Graph data retrieved: {graph_data['total_news']} news, "
            f"{graph_data['total_entities']} entities"
        )

        return graph_data

    except Exception as e:
        logger.error(f"Failed to fetch graph data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve graph data: {str(e)}",
        ) from e


@router.get("/category-tree", response_model=CategoryTreeResponse)
async def get_category_tree(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    limit_per_category: int = Query(
        20, ge=5, le=50, description="Max news per category"
    ),
) -> dict:
    """Get hierarchical category tree with subcategories and news.

    Args:
        session: Database session
        service: PostgreSQL news service
        limit_per_category: Maximum news items per category

    Returns:
        Category tree structure

    Raises:
        HTTPException: If failed to retrieve category tree
    """
    try:
        logger.info(
            f"Fetching category tree, limit_per_category={limit_per_category}"
        )

        tree_data = await service.get_category_tree(
            session, limit_per_category
        )

        logger.info(
            f"Category tree retrieved: {len(tree_data['categories'])} categories"
        )

        return tree_data

    except Exception as e:
        logger.error(f"Failed to fetch category tree: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve category tree: {str(e)}",
        ) from e


@router.get("/entities", response_model=EntityListResponse)
async def get_entities(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    min_news: int = Query(
        2, ge=1, le=10, description="Min news count to include entity"
    ),
    limit: int = Query(
        100, ge=10, le=500, description="Max entities to return"
    ),
) -> dict:
    """Get list of entities with their connected news counts.

    Args:
        session: Database session
        service: PostgreSQL news service
        min_news: Minimum news count to include entity
        limit: Maximum entities to return

    Returns:
        Entity list with news connections

    Raises:
        HTTPException: If failed to retrieve entities
    """
    try:
        logger.info(f"Fetching entities, min_news={min_news}, limit={limit}")

        entity_data = await service.get_entity_list(session, min_news, limit)

        logger.info(f"Entities retrieved: {entity_data['total']} entities")

        return entity_data

    except Exception as e:
        logger.error(f"Failed to fetch entities: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve entities: {str(e)}",
        ) from e


@router.get("/entity-graph", response_model=GraphResponse)
async def get_entity_graph(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    entity_id: int | None = Query(None, description="Filter by entity ID"),
    limit: int = Query(50, ge=5, le=100, description="Max news items"),
) -> dict:
    """Get graph of news connected by shared entities.

    Args:
        session: Database session
        service: PostgreSQL news service
        entity_id: Optional entity ID to filter news
        limit: Maximum news items

    Returns:
        Graph with news connected by shared entities

    Raises:
        HTTPException: If failed to retrieve entity graph
    """
    try:
        logger.info(
            f"Fetching entity graph, entity_id={entity_id}, limit={limit}"
        )

        graph_data = await service.get_entity_graph(
            session,
            entity_id=entity_id,
            limit=limit,
        )

        logger.info(
            f"Entity graph retrieved: {graph_data['total_news']} news, "
            f"{graph_data['total_entities']} entities"
        )

        return graph_data

    except Exception as e:
        logger.error(f"Failed to fetch entity graph: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve entity graph: {str(e)}",
        ) from e


@router.get("/by-ids", response_model=GraphResponse)
async def get_news_by_ids(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[PostgresNewsService, Depends(get_postgres_service)],
    ids: str = Query(..., description="Comma-separated news IDs"),
) -> dict:
    """Get graph of news by specific IDs.

    Args:
        session: Database session
        service: PostgreSQL news service
        ids: Comma-separated news IDs

    Returns:
        Graph with specified news items

    Raises:
        HTTPException: If failed to retrieve news
    """
    try:
        news_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
        logger.info(
            f"Fetching news by ids: {news_ids[:5]}... (total: {len(news_ids)})"
        )

        graph_data = await service.get_news_by_ids(session, news_ids)

        logger.info(f"News by ids retrieved: {graph_data['total_news']} news")

        return graph_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid IDs format: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Failed to fetch news by ids: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news: {str(e)}",
        ) from e
