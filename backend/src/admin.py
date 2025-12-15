from sqladmin import Admin, ModelView
from sqladmin.filters import (
    BooleanFilter,
    AllUniqueStringValuesFilter,
    StaticValuesFilter,
    ForeignKeyFilter,
    OperationColumnFilter,
)
from fastapi import FastAPI
from rag_module.db.models import (
    Source,
    Article,
    Chunk,
    Subcategory,
    Topic,
    Keyword,
    Entity,
    ArticleSubcategory,
    ArticleTopic,
    ArticleKeyword,
    ArticleEntity,
)
from src.database import get_db_manager


class SourceAdmin(ModelView, model=Source):
    name = "Source"
    icon = "fa-solid fa-database"
    column_list = ["id", "name", "created_at", "updated_at"]
    column_filters = [
        OperationColumnFilter("name"),
        OperationColumnFilter("created_at"),
    ]


class ArticleAdmin(ModelView, model=Article):
    name = "Article"
    icon = "fa-solid fa-newspaper"
    column_list = [
        "id", "source_id", "doc_id", "message_id", "url", "date",
        "category", "sentiment", "sentiment_score", "importance",
        "is_breaking", "is_high_importance", "created_at", "updated_at"
    ]
    column_filters = [
        ForeignKeyFilter("source_id", "name", Source),
        OperationColumnFilter("date"),
        OperationColumnFilter("category"),
        OperationColumnFilter("sentiment"),
    ]


class ChunkAdmin(ModelView, model=Chunk):
    name = "Chunk"
    icon = "fa-solid fa-layer-group"
    column_list = [
        "id", 
        "article_id", 
        "chunk_index", 
        "chunk_size",
        "total_chunks", 
        "content", 
        "created_at"
    ]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        OperationColumnFilter("chunk_index"),
    ]


class SubcategoryAdmin(ModelView, model=Subcategory):
    name = "Subcategory"
    icon = "fa-solid fa-tags"
    column_list = ["id", "name"]
    column_filters = [OperationColumnFilter("name")]


class TopicAdmin(ModelView, model=Topic):
    name = "Topic"
    icon = "fa-solid fa-lightbulb"
    column_list = ["id", "name"]
    column_filters = [OperationColumnFilter("name")]


class KeywordAdmin(ModelView, model=Keyword):
    name = "Keyword"
    icon = "fa-solid fa-key"
    column_list = ["id", "value"]
    column_filters = [OperationColumnFilter("value")]


class EntityAdmin(ModelView, model=Entity):
    name = "Entity"
    icon = "fa-solid fa-user-secret"
    column_list = ["id", "text", "normalized", "type", "role", "confidence"]
    column_filters = [
        OperationColumnFilter("text"),
        OperationColumnFilter("type"),
        OperationColumnFilter("role"),
    ]


class ArticleSubcategoryAdmin(ModelView, model=ArticleSubcategory):
    name = "Article Subcategory"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "subcategory_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("subcategory_id", "name", Subcategory),
    ]


class ArticleTopicAdmin(ModelView, model=ArticleTopic):
    name = "Article Topic"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "topic_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("topic_id", "name", Topic),
    ]


class ArticleKeywordAdmin(ModelView, model=ArticleKeyword):
    name = "Article Keyword"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "keyword_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("keyword_id", "value", Keyword),
    ]


class ArticleEntityAdmin(ModelView, model=ArticleEntity):
    name = "Article Entity"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "entity_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("entity_id", "text", Entity),
    ]


def setup_admin(app: FastAPI) -> None:
    """Configure SQLAdmin for FastAPI app."""
    db_manager = get_db_manager()
    admin = Admin(app, db_manager.engine)

    admin.add_view(SourceAdmin)
    admin.add_view(ArticleAdmin)
    admin.add_view(ChunkAdmin)
    admin.add_view(SubcategoryAdmin)
    admin.add_view(TopicAdmin)
    admin.add_view(KeywordAdmin)
    admin.add_view(EntityAdmin)
    admin.add_view(ArticleSubcategoryAdmin)
    admin.add_view(ArticleTopicAdmin)
    admin.add_view(ArticleKeywordAdmin)
    admin.add_view(ArticleEntityAdmin)
