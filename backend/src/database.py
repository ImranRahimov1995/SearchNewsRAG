"""Database connection and session management."""

from collections.abc import AsyncGenerator

from config import get_settings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

settings = get_settings()


class DatabaseManager:
    """Manager for async database connections."""

    def __init__(self, database_url: str) -> None:
        """Initialize database manager.

        Args:
            database_url: PostgreSQL connection URL
        """
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._database_url = database_url

    @property
    def engine(self) -> AsyncEngine:
        """Get or create async database engine.

        Returns:
            SQLAlchemy async engine instance
        """
        if self._engine is None:
            self._engine = create_async_engine(
                self._database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create async session factory.

        Returns:
            SQLAlchemy async session maker
        """
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create async database session.

        Yields:
            SQLAlchemy async session

        Raises:
            RuntimeError: If database connection fails
        """
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database connections."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance.

    Returns:
        DatabaseManager singleton instance

    Raises:
        RuntimeError: If DATABASE_URL is not configured
    """
    global _db_manager

    if _db_manager is None:
        if not settings.async_database_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        _db_manager = DatabaseManager(settings.async_database_url)

    return _db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session.

    Yields:
        SQLAlchemy async session
    """
    db_manager = get_db_manager()
    async for session in db_manager.get_session():
        yield session
