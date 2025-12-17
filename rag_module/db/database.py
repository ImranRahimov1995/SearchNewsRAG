"""Database session factory for relational storage."""

from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(database_url: str) -> Callable[[], Session]:
    """Create session factory for the given database URL."""
    engine = _create_engine(database_url)
    factory: sessionmaker[Session] = sessionmaker(
        bind=engine, expire_on_commit=False, class_=Session
    )

    def _factory() -> Session:
        return factory()

    return _factory


def _create_engine(database_url: str) -> Engine:
    """Create SQLAlchemy engine."""
    return create_engine(database_url, future=True, pool_pre_ping=True)
