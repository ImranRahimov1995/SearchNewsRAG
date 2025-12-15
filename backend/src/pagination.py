"""Generic pagination utilities for all services."""

from typing import Any, Generic, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response style.

    Attributes:
        count: Total number of items
        next: URL to next page or None
        previous: URL to previous page or None
        results: List of items for current page
    """

    count: int = Field(..., ge=0, description="Total number of items")
    next: str | None = Field(None, description="URL to next page")
    previous: str | None = Field(None, description="URL to previous page")
    results: list[T] = Field(..., description="Items for current page")


def build_pagination_url(
    base_url: str,
    page: int,
    params: dict[str, Any],
) -> str:
    """Build pagination URL with query parameters.

    Args:
        base_url: Base endpoint URL
        page: Page number
        params: Query parameters to include

    Returns:
        Full URL with query string
    """
    query_params = {**params, "page": page}
    clean_params = {k: v for k, v in query_params.items() if v is not None}
    query_string = urlencode(clean_params)
    return f"{base_url}?{query_string}"


def paginate(
    items: list[T],
    page: int,
    page_size: int,
    base_url: str,
    query_params: dict[str, Any],
    total: int | None = None,
) -> dict[str, Any]:
    """Paginate items and build response.

    Args:
        items: Items for current page (or all items if total is None)
        page: Current page number (1-indexed)
        page_size: Items per page
        base_url: Base endpoint URL for building next/previous links
        query_params: Additional query parameters to preserve
        total: Total number of items across all pages (optional).
               If provided, items is treated as current page only.
               If None, items is treated as all items and will be sliced.

    Returns:
        Dictionary with count, next, previous, and results
    """
    if total is not None:
        # Database-paginated mode: items are already sliced for current page
        total_items = total
        page_items = items
    else:
        # In-memory pagination mode: slice items for current page
        total_items = len(items)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_items = items[start_index:end_index]

    total_pages = (
        (total_items + page_size - 1) // page_size if total_items > 0 else 0
    )

    if page < 1:
        page = 1

    has_next = page < total_pages
    has_previous = page > 1

    clean_params = {k: v for k, v in query_params.items() if k != "page"}

    next_url = (
        build_pagination_url(base_url, page + 1, clean_params)
        if has_next
        else None
    )
    previous_url = (
        build_pagination_url(base_url, page - 1, clean_params)
        if has_previous
        else None
    )

    return {
        "count": total_items,
        "next": next_url,
        "previous": previous_url,
        "results": page_items,
    }
