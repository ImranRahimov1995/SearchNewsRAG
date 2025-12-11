"""Schemas for news endpoints."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DateFilter(str, Enum):
    """Date filter options."""

    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    ALL = "all"


class SortOrder(str, Enum):
    """Sort order options."""

    DESC = "desc"
    ASC = "asc"


class CategoryStats(BaseModel):
    """Statistics for a news category."""

    category: str = Field(..., description="Category name")
    count: int = Field(..., ge=0, description="Number of documents")


class CategoriesResponse(BaseModel):
    """Response with all categories and their counts."""

    categories: list[CategoryStats] = Field(
        ..., description="List of categories with document counts"
    )
    total_documents: int = Field(
        ...,
        ge=0,
        description="Total number of documents across all categories",
    )


class NewsItem(BaseModel):
    """Single news item."""

    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="News content")
    category: str | None = Field(None, description="News category")
    date: datetime | None = Field(None, description="Publication date")
    importance: int | None = Field(None, description="Importance score")


class NewsResponse(BaseModel):
    """Response wrapper for news list."""

    news: list[NewsItem] = Field(..., description="List of news items")


class NewsListResponse(BaseModel):
    """Paginated news response matching Django REST style."""

    count: int = Field(..., ge=0, description="Total number of items")
    next: str | None = Field(None, description="URL to next page")
    previous: str | None = Field(None, description="URL to previous page")
    results: NewsResponse = Field(..., description="News items")
