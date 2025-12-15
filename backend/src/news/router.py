"""Router for news endpoints."""

import logging
from datetime import datetime
from typing import Annotated

from database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pagination import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_postgres_service
from .schemas import CategoriesResponse, NewsItem, NewsListResponse
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
