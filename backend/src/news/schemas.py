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


class GraphNodeMeta(BaseModel):
    """Metadata for a graph node."""

    source: str | None = Field(None, description="News source")
    date: str | None = Field(None, description="Publication date")
    sentiment: str | None = Field(
        None, description="Sentiment: positive/negative/neutral"
    )
    importance: int | None = Field(None, description="Importance score 1-10")
    tags: list[str] = Field(default_factory=list, description="Tags/keywords")
    entities: list[str] = Field(
        default_factory=list, description="Related entities"
    )
    category: str | None = Field(None, description="News category")
    url: str | None = Field(None, description="Original news URL")


class GraphNode(BaseModel):
    """Node in the news graph."""

    id: str = Field(..., description="Unique node identifier")
    kind: str = Field(..., description="Node type: entity/news/event")
    title: str = Field(..., description="Node title")
    subtitle: str | None = Field(None, description="Node subtitle")
    meta: GraphNodeMeta = Field(
        default_factory=GraphNodeMeta, description="Node metadata"
    )
    pos: dict[str, float] = Field(
        default_factory=lambda: {"xPct": 50, "yPct": 50},
        description="Position as percentage {xPct, yPct}",
    )


class GraphEdge(BaseModel):
    """Edge connecting two nodes in the graph."""

    id: str = Field(..., description="Unique edge identifier")
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")
    label: str | None = Field(None, description="Edge label")
    strength: int = Field(2, ge=1, le=3, description="Connection strength 1-3")

    class Config:
        """Pydantic config for field aliasing."""

        populate_by_name = True


class GraphResponse(BaseModel):
    """Response containing graph data for visualization."""

    nodes: list[GraphNode] = Field(..., description="List of graph nodes")
    edges: list[GraphEdge] = Field(
        ..., description="List of edges connecting nodes"
    )
    total_news: int = Field(0, description="Total news count in graph")
    total_entities: int = Field(0, description="Total entity count in graph")


class NewsInCategory(BaseModel):
    """News item within category tree."""

    id: int
    title: str
    date: str | None = None
    importance: int | None = None
    entity_ids: list[int] = Field(default_factory=list)


class SubcategoryNode(BaseModel):
    """Subcategory with its news."""

    name: str
    news: list[NewsInCategory] = Field(default_factory=list)


class CategoryNode(BaseModel):
    """Category with subcategories and news."""

    name: str
    count: int
    subcategories: list[SubcategoryNode] = Field(default_factory=list)
    news: list[NewsInCategory] = Field(default_factory=list)


class CategoryTreeResponse(BaseModel):
    """Hierarchical category tree response."""

    categories: list[CategoryNode] = Field(default_factory=list)
    total_news: int = 0


class EntityItem(BaseModel):
    """Entity with connected news count."""

    id: int
    name: str
    type: str | None = None
    news_count: int = 0
    news_ids: list[int] = Field(default_factory=list)


class EntityListResponse(BaseModel):
    """List of entities with their connections."""

    entities: list[EntityItem] = Field(default_factory=list)
    total: int = 0


class EntityGraphRequest(BaseModel):
    """Request for entity-based graph."""

    entity_id: int | None = None
    category: str | None = None
    limit: int = 50
