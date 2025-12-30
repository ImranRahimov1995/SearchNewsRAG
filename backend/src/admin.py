from auth.services.admin_auth_service import AdminAuthBackend
from config import get_settings
from database import get_db_manager
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.filters import ForeignKeyFilter, OperationColumnFilter
from starlette.middleware.sessions import SessionMiddleware
from users.admin import (
    GroupAdmin,
    OTPAdmin,
    PermissionAdmin,
    ProfileAdmin,
    UserAdmin,
)

from rag_module.db.models import (
    Article,
    ArticleEntity,
    ArticleKeyword,
    ArticleSubcategory,
    ArticleTopic,
    Chunk,
    Entity,
    Keyword,
    Source,
    Subcategory,
    Topic,
)


class SourceAdmin(ModelView, model=Source):
    """Admin view for Source model."""

    name = "Source"
    icon = "fa-solid fa-database"
    column_list = ["id", "name", "created_at", "updated_at"]
    column_filters = [
        OperationColumnFilter("name"),
        OperationColumnFilter("created_at"),
    ]


class ArticleAdmin(ModelView, model=Article):
    """Admin view for Article model."""

    name = "Article"
    icon = "fa-solid fa-newspaper"
    column_list = [
        "id",
        "source_id",
        "doc_id",
        "message_id",
        "full_content",
        "has_detail",
        "url",
        "date",
        "category",
        "sentiment",
        "sentiment_score",
        "importance",
        "is_breaking",
        "is_high_importance",
        "created_at",
        "updated_at",
    ]
    column_filters = [
        ForeignKeyFilter("source_id", "name", Source),
        OperationColumnFilter("date"),
        OperationColumnFilter("category"),
        OperationColumnFilter("sentiment"),
    ]


class ChunkAdmin(ModelView, model=Chunk):
    """Admin view for Chunk model."""

    name = "Chunk"
    icon = "fa-solid fa-layer-group"
    column_list = [
        "id",
        "article_id",
        "chunk_index",
        "chunk_size",
        "total_chunks",
        "content",
        "created_at",
    ]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        OperationColumnFilter("chunk_index"),
    ]


class SubcategoryAdmin(ModelView, model=Subcategory):
    """Admin view for Subcategory model."""

    name = "Subcategory"
    icon = "fa-solid fa-tags"
    column_list = ["id", "name"]
    column_filters = [OperationColumnFilter("name")]


class TopicAdmin(ModelView, model=Topic):
    """Admin view for Topic model."""

    name = "Topic"
    icon = "fa-solid fa-lightbulb"
    column_list = ["id", "name"]
    column_filters = [OperationColumnFilter("name")]


class KeywordAdmin(ModelView, model=Keyword):
    """Admin view for Keyword model."""

    name = "Keyword"
    icon = "fa-solid fa-key"
    column_list = ["id", "value"]
    column_filters = [OperationColumnFilter("value")]


class EntityAdmin(ModelView, model=Entity):
    """Admin view for Entity model."""

    name = "Entity"
    icon = "fa-solid fa-user-secret"
    column_list = ["id", "text", "normalized", "type", "role", "confidence"]
    column_filters = [
        OperationColumnFilter("text"),
        OperationColumnFilter("type"),
        OperationColumnFilter("role"),
    ]


class ArticleSubcategoryAdmin(ModelView, model=ArticleSubcategory):
    """Admin view for ArticleSubcategory association model."""

    name = "Article Subcategory"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "subcategory_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("subcategory_id", "name", Subcategory),
    ]


class ArticleTopicAdmin(ModelView, model=ArticleTopic):
    """Admin view for ArticleTopic association model."""

    name = "Article Topic"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "topic_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("topic_id", "name", Topic),
    ]


class ArticleKeywordAdmin(ModelView, model=ArticleKeyword):
    """Admin view for ArticleKeyword association model."""

    name = "Article Keyword"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "keyword_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("keyword_id", "value", Keyword),
    ]


class ArticleEntityAdmin(ModelView, model=ArticleEntity):
    """Admin view for ArticleEntity association model."""

    name = "Article Entity"
    icon = "fa-solid fa-link"
    column_list = ["id", "article_id", "entity_id"]
    column_filters = [
        ForeignKeyFilter("article_id", "id", Article),
        ForeignKeyFilter("entity_id", "text", Entity),
    ]


def setup_admin(app: FastAPI) -> None:
    """Configure SQLAdmin with superuser authentication."""
    settings = get_settings()
    db_manager = get_db_manager()

    app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret_key)

    authentication_backend = AdminAuthBackend(
        secret_key=settings.jwt_secret_key
    )
    admin = Admin(
        app, db_manager.engine, authentication_backend=authentication_backend
    )

    # User management views
    admin.add_view(UserAdmin)
    admin.add_view(GroupAdmin)
    admin.add_view(PermissionAdmin)
    admin.add_view(ProfileAdmin)
    admin.add_view(OTPAdmin)

    # News views
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
