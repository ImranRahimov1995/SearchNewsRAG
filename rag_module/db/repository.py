"""Repository for persisting news data to relational database."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rag_module.data_processing.protocols import Document

from .models import Article, Chunk, Entity, Keyword, Source, Subcategory, Topic


class NewsDataRepository:
    """Persist processed documents and analysis metadata."""

    def __init__(self, session_factory: Callable[[], Session]):
        """Initialize repository with session factory."""
        self.session_factory = session_factory

    def persist_documents(
        self, documents: list[Document], source_name: str
    ) -> None:
        """Persist processed documents, taxonomies, entities, and chunks."""
        if not documents:
            return
        with self.session_factory() as session:
            source = self._get_or_create_source(session, source_name)
            for document in documents:
                article = self._upsert_article(session, source, document)
                self._sync_subcategories(session, article, document)
                self._sync_topics(session, article, document)
                self._sync_keywords(session, article, document)
                self._sync_entities(session, article, document)
                self._sync_chunks(session, article, document, source_name)
            session.commit()

    def _get_or_create_source(self, session: Session, name: str) -> Source:
        """Get or create source by name."""
        existing = session.scalar(select(Source).where(Source.name == name))
        if existing:
            return cast(Source, existing)
        source = Source(name=name)
        session.add(source)
        session.flush()
        return source

    def _upsert_article(
        self, session: Session, source: Source, document: Document
    ) -> Article:
        """Insert or update article record."""
        doc_id = self._resolve_doc_id(document)
        message_id = self._safe_int(document.metadata.get("message_id"))
        existing = self._find_article(session, source.id, message_id, doc_id)
        if existing:
            self._update_article(existing, document)
            session.flush()
            return existing
        article = Article(
            source_id=source.id,
            doc_id=doc_id,
            message_id=message_id,
        )
        self._update_article(article, document)
        session.add(article)
        session.flush()
        return article

    def _find_article(
        self,
        session: Session,
        source_id: int,
        message_id: int | None,
        doc_id: int | None,
    ) -> Article | None:
        """Find article by unique keys."""
        if message_id is not None:
            message_article: Article | None = cast(
                Article | None,
                session.scalar(
                    select(Article).where(
                        Article.source_id == source_id,
                        Article.message_id == message_id,
                    )
                ),
            )
            return message_article
        if doc_id is not None:
            doc_article: Article | None = cast(
                Article | None,
                session.scalar(
                    select(Article).where(
                        Article.source_id == source_id,
                        Article.doc_id == doc_id,
                    )
                ),
            )
            return doc_article
        return None

    def _update_article(self, article: Article, document: Document) -> None:
        """Update article fields from document metadata."""
        metadata = document.metadata
        resolved_doc_id = self._safe_int(metadata.get("doc_id"))
        article.doc_id = article.doc_id or resolved_doc_id
        resolved_message_id = self._safe_int(metadata.get("message_id"))
        article.message_id = article.message_id or resolved_message_id
        article.url = metadata.get("url")
        article.date = self._parse_datetime(metadata.get("date"))
        article.has_detail = bool(metadata.get("has_detail"))
        article.short_preview = metadata.get("short_preview")
        article.full_content = document.content
        article.summary = metadata.get("summary")
        article.reasoning = metadata.get("reasoning")
        article.category = metadata.get("category")
        article.sentiment = metadata.get("sentiment")
        article.sentiment_score = self._safe_float(
            metadata.get("sentiment_score")
        )
        article.importance = self._safe_int(metadata.get("importance"))
        article.geographic_scope = metadata.get("geographic_scope")
        article.temporal_relevance = metadata.get("temporal_relevance")
        article.target_audience = self._join_list(
            metadata.get("target_audience")
        )
        article.is_breaking = bool(metadata.get("is_breaking"))
        article.is_high_importance = bool(metadata.get("is_high_importance"))
        article.is_local = bool(metadata.get("is_local"))
        article.is_positive = bool(metadata.get("is_positive"))
        article.is_negative = bool(metadata.get("is_negative"))
        article.llm_analysis_exists = bool(metadata.get("llm_analysis_exists"))
        article.analysis_error = bool(metadata.get("analysis_error"))

    def _sync_subcategories(
        self, session: Session, article: Article, document: Document
    ) -> None:
        """Attach subcategories to article."""
        subcategories = self._ensure_list(
            document.metadata.get("subcategories")
        )
        for name in subcategories:
            normalized = str(name).strip()
            if not normalized:
                continue
            item = self._get_or_create_subcategory(session, normalized)
            if item not in article.subcategories:
                article.subcategories.append(item)

    def _sync_topics(
        self, session: Session, article: Article, document: Document
    ) -> None:
        """Attach topics to article."""
        topics = self._ensure_list(document.metadata.get("topics"))
        for name in topics:
            normalized = str(name).strip()
            if not normalized:
                continue
            item = self._get_or_create_topic(session, normalized)
            if item not in article.topics:
                article.topics.append(item)

    def _sync_keywords(
        self, session: Session, article: Article, document: Document
    ) -> None:
        """Attach keywords to article."""
        keywords = self._ensure_list(document.metadata.get("keywords"))
        for name in keywords:
            normalized = str(name).strip()
            if not normalized:
                continue
            item = self._get_or_create_keyword(session, normalized)
            if item not in article.keywords:
                article.keywords.append(item)

    def _sync_entities(
        self, session: Session, article: Article, document: Document
    ) -> None:
        """Attach entities to article."""
        raw_entities = document.metadata.get("entities")
        if not raw_entities:
            return
        for entity_data in self._ensure_list(raw_entities):
            if not isinstance(entity_data, dict):
                continue
            entity = self._get_or_create_entity(session, entity_data)
            if entity not in article.entities:
                article.entities.append(entity)

    def _sync_chunks(
        self,
        session: Session,
        article: Article,
        document: Document,
        source_name: str,
    ) -> None:
        """Persist chunks for article."""
        for index, chunk_text in enumerate(document.chunks):
            chunk_id = self._build_chunk_id(document, source_name, index)
            existing = session.get(Chunk, chunk_id)
            if existing:
                existing.content = chunk_text
                existing.chunk_index = index
                existing.chunk_size = len(chunk_text)
                existing.total_chunks = len(document.chunks)
                continue
            chunk = Chunk(
                id=chunk_id,
                article_id=article.id,
                chunk_index=index,
                chunk_size=len(chunk_text),
                total_chunks=len(document.chunks),
                content=chunk_text,
            )
            session.add(chunk)

    def _get_or_create_subcategory(
        self, session: Session, name: str
    ) -> Subcategory:
        """Get or create subcategory."""
        existing = session.scalar(
            select(Subcategory).where(Subcategory.name == name)
        )
        if existing:
            return cast(Subcategory, existing)
        subcategory = Subcategory(name=name)
        session.add(subcategory)
        session.flush()
        return subcategory

    def _get_or_create_topic(self, session: Session, name: str) -> Topic:
        """Get or create topic."""
        existing = session.scalar(select(Topic).where(Topic.name == name))
        if existing:
            return cast(Topic, existing)
        topic = Topic(name=name)
        session.add(topic)
        session.flush()
        return topic

    def _get_or_create_keyword(self, session: Session, name: str) -> Keyword:
        """Get or create keyword."""
        existing = session.scalar(select(Keyword).where(Keyword.value == name))
        if existing:
            return cast(Keyword, existing)
        keyword = Keyword(value=name)
        session.add(keyword)
        session.flush()
        return keyword

    def _get_or_create_entity(
        self, session: Session, data: dict[str, Any]
    ) -> Entity:
        """Get or create entity using identity fields."""
        text = str(data.get("text", "")).strip()
        normalized = str(data.get("normalized", text)).strip()
        entity_type = data.get("type")
        role = data.get("role")
        confidence = self._safe_float(data.get("confidence"))
        existing = session.scalar(
            select(Entity).where(
                Entity.text == text,
                Entity.normalized == normalized,
                Entity.type == entity_type,
                Entity.role == role,
            )
        )
        if existing:
            entity_existing = cast(Entity, existing)
            if confidence is not None:
                entity_existing.confidence = confidence
            return entity_existing
        entity = Entity(
            text=text,
            normalized=normalized,
            type=entity_type,
            role=role,
            confidence=confidence,
        )
        session.add(entity)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            fallback = session.scalar(
                select(Entity).where(
                    Entity.text == text,
                    Entity.normalized == normalized,
                    Entity.type == entity_type,
                    Entity.role == role,
                )
            )
            if fallback is None:
                raise ValueError("Failed to persist entity after rollback")
            return cast(Entity, fallback)
        return entity

    def _build_chunk_id(
        self, document: Document, source_name: str, chunk_index: int
    ) -> str:
        """Build deterministic chunk identifier consistent with vector store."""
        doc_id = self._resolve_doc_id(document)
        return f"{source_name}_{doc_id}_chunk_{chunk_index}"

    def _resolve_doc_id(self, document: Document) -> int:
        """Resolve document identifier from metadata."""
        resolved = self._safe_int(document.metadata.get("message_id"))
        if resolved is not None:
            return resolved
        return hash(document.content)

    def _parse_datetime(self, value: Any) -> datetime | None:
        """Parse ISO datetime string to aware datetime."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return None

    def _join_list(self, value: Any) -> str | None:
        """Join list values into string."""
        if value is None:
            return None
        if isinstance(value, list):
            joined = [str(item).strip() for item in value if str(item).strip()]
            return ", ".join(joined) if joined else None
        return str(value)

    def _ensure_list(self, value: Any) -> list[Any]:
        """Ensure value is a list."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _safe_float(self, value: Any) -> float | None:
        """Convert value to float when possible."""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _safe_int(self, value: Any) -> int | None:
        """Convert value to int when possible."""
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
