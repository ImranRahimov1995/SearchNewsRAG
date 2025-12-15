"""Router for news endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pagination import paginate

from .dependencies import get_news_service
from .schemas import (
    CategoriesResponse,
    DateFilter,
    NewsListResponse,
    SortOrder,
)
from .service import ChromaNewsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(
    service: Annotated[ChromaNewsService, Depends(get_news_service)],
) -> dict:
    """Get all news categories with document counts.

    Args:
        service: Injected news service instance

    Returns:
        List of categories with their document counts

    Raises:
        HTTPException: If failed to retrieve categories
    """
    try:
        logger.info("Fetching categories statistics")

        result = service.get_categories()

        logger.info(
            f"Categories retrieved: {len(result['categories'])} categories, "
            f"{result['total_documents']} total documents"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}",
        ) from e


@router.get("/", response_model=NewsListResponse)
async def get_news(
    request: Request,
    service: Annotated[ChromaNewsService, Depends(get_news_service)],
    date_filter: DateFilter = Query(
        DateFilter.ALL, description="Filter by date range"
    ),
    sort_order: SortOrder = Query(
        SortOrder.DESC, description="Sort order by date"
    ),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(
        20, ge=1, le=100, description="Items per page (max 100)"
    ),
) -> dict:
    """Get news filtered by date and sorted with pagination.

    Args:
        request: FastAPI request object for building URLs
        service: Injected news service instance
        date_filter: Date filter (today, week, month, all)
        sort_order: Sort order (desc, asc)
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated list with count, next, previous, and results

    Raises:
        HTTPException: If failed to retrieve news
    """
    try:
        logger.info(
            f"Fetching news: filter={date_filter}, sort={sort_order}, "
            f"page={page}, page_size={page_size}"
        )

        all_news = service.get_news(
            date_filter=date_filter,
            sort_order=sort_order,
        )

        base_url = str(request.url_for("get_news"))
        query_params = {
            "date_filter": date_filter.value,
            "sort_order": sort_order.value,
            "page_size": page_size,
        }

        paginated = paginate(
            items=all_news,
            page=page,
            page_size=page_size,
            base_url=base_url,
            query_params=query_params,
        )

        response = {
            "count": paginated["count"],
            "next": paginated["next"],
            "previous": paginated["previous"],
            "results": {"news": paginated["results"]},
        }

        logger.info(
            f"News retrieved: {len(paginated['results'])} items "
            f"(page {page}, total {paginated['count']})"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to fetch news: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news: {str(e)}",
        ) from e
