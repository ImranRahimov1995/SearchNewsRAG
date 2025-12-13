"""SQLAlchemy models for news data."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class."""


class Source(Base):
    """News source such as Telegram channel."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    articles: Mapped[list["Article"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class Article(Base):
    """News article with analysis metadata."""

    __tablename__ = "news_articles"
    __table_args__ = (
        UniqueConstraint(
            "source_id", "message_id", name="uq_article_source_message"
        ),
        # Essential indexes for common queries
        Index("ix_article_date", "date"),
        Index("ix_article_category", "category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    doc_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512))
    image_url: Mapped[str | None] = mapped_column(String(512))
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    has_detail: Mapped[bool] = mapped_column(Boolean, default=False)
    short_preview: Mapped[str | None] = mapped_column(Text)
    full_content: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    reasoning: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(128))
    sentiment: Mapped[str | None] = mapped_column(String(64))
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    importance: Mapped[int | None] = mapped_column(Integer)
    geographic_scope: Mapped[str | None] = mapped_column(String(64))
    temporal_relevance: Mapped[str | None] = mapped_column(String(64))
    target_audience: Mapped[str | None] = mapped_column(String(256))
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False)
    is_high_importance: Mapped[bool] = mapped_column(Boolean, default=False)
    is_local: Mapped[bool] = mapped_column(Boolean, default=False)
    is_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    is_negative: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_analysis_exists: Mapped[bool] = mapped_column(Boolean, default=False)
    analysis_error: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped[Source] = relationship(back_populates="articles")
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    subcategories: Mapped[list["Subcategory"]] = relationship(
        secondary="article_subcategories", back_populates="articles"
    )
    topics: Mapped[list["Topic"]] = relationship(
        secondary="article_topics", back_populates="articles"
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        secondary="article_keywords", back_populates="articles"
    )
    entities: Mapped[list["Entity"]] = relationship(
        secondary="article_entities", back_populates="articles"
    )


class Chunk(Base):
    """Chunk of article used for vector store."""

    __tablename__ = "news_chunks"

    id: Mapped[str] = mapped_column(String(512), primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    chunk_size: Mapped[int] = mapped_column(Integer)
    total_chunks: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    article: Mapped[Article] = relationship(back_populates="chunks")


class Subcategory(Base):
    """Subcategory taxonomy item."""

    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    articles: Mapped[list[Article]] = relationship(
        secondary="article_subcategories", back_populates="subcategories"
    )


class Topic(Base):
    """Topic taxonomy item."""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    articles: Mapped[list[Article]] = relationship(
        secondary="article_topics", back_populates="topics"
    )


class Keyword(Base):
    """Keyword taxonomy item."""

    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(128), unique=True)
    articles: Mapped[list[Article]] = relationship(
        secondary="article_keywords", back_populates="keywords"
    )


class Entity(Base):
    """Named entity extracted from article."""

    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint(
            "text",
            "normalized",
            "type",
            "role",
            name="uq_entity_identity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(256))
    normalized: Mapped[str | None] = mapped_column(String(256))
    type: Mapped[str | None] = mapped_column(String(64))
    role: Mapped[str | None] = mapped_column(String(256))
    confidence: Mapped[float | None] = mapped_column(Float)
    articles: Mapped[list[Article]] = relationship(
        secondary="article_entities", back_populates="entities"
    )


class ArticleSubcategory(Base):
    """Bridge table for article subcategories."""

    __tablename__ = "article_subcategories"
    __table_args__ = (
        UniqueConstraint(
            "article_id", "subcategory_id", name="uq_article_subcategory"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"))
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"))


class ArticleTopic(Base):
    """Bridge table for article topics."""

    __tablename__ = "article_topics"
    __table_args__ = (
        UniqueConstraint("article_id", "topic_id", name="uq_article_topic"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))


class ArticleKeyword(Base):
    """Bridge table for article keywords."""

    __tablename__ = "article_keywords"
    __table_args__ = (
        UniqueConstraint(
            "article_id", "keyword_id", name="uq_article_keyword"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"))
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"))


class ArticleEntity(Base):
    """Bridge table for article entities."""

    __tablename__ = "article_entities"
    __table_args__ = (
        UniqueConstraint("article_id", "entity_id", name="uq_article_entity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("news_articles.id"))
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
