"""Database migration runner for production deployments."""

import asyncio
import logging
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from config import get_settings
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


def get_alembic_config() -> Config:
    """Get Alembic configuration.

    Returns:
        Alembic config object
    """
    backend_dir = Path(__file__).parent.parent
    alembic_ini = backend_dir / "alembic.ini"
    if not alembic_ini.exists():
        alembic_ini = backend_dir.parent / "alembic.ini"
    if not alembic_ini.exists():
        raise FileNotFoundError(
            f"alembic.ini not found at {backend_dir / 'alembic.ini'} or {backend_dir.parent / 'alembic.ini'}"
        )
    config = Config(str(alembic_ini))
    migrations_dir = backend_dir / "migrations"
    if not migrations_dir.exists():
        migrations_dir = backend_dir.parent / "migrations"
    config.set_main_option("script_location", str(migrations_dir))
    return config


def run_migrations_upgrade(revision: str = "head") -> None:
    """Run database migrations to upgrade to specified revision.

    Args:
        revision: Target revision (default: 'head' for latest)
    """
    try:
        logger.info(f"Running migrations to {revision}...")
        config = get_alembic_config()
        command.upgrade(config, revision)
        logger.info("✅ Migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise


def run_migrations_downgrade(revision: str = "-1") -> None:
    """Downgrade database to specified revision.

    Args:
        revision: Target revision (default: '-1' for one step back)
    """
    try:
        logger.warning(f"Downgrading migrations to {revision}...")
        config = get_alembic_config()
        command.downgrade(config, revision)
        logger.info("✅ Downgrade completed successfully")
    except Exception as e:
        logger.error(f"❌ Downgrade failed: {e}", exc_info=True)
        raise


def get_current_revision() -> str | None:
    """Get current database revision.

    Returns:
        Current revision ID or None if not initialized
    """
    try:
        config = get_alembic_config()
        settings = get_settings()
        if settings.async_database_url:
            db_url = settings.async_database_url.replace(
                "postgresql+asyncpg://", "postgresql+psycopg://"
            )
            config.set_main_option("sqlalchemy.url", db_url)

        def get_revision(connection):
            context = MigrationContext.configure(connection)
            return context.get_current_revision()

        engine = create_engine(config.get_main_option("sqlalchemy.url"))
        with engine.connect() as connection:
            return get_revision(connection)
    except Exception as e:
        logger.error(f"Failed to get current revision: {e}")
        return None


def check_migrations_pending() -> bool:
    """Check if there are pending migrations.

    Returns:
        True if migrations are pending, False otherwise
    """
    try:
        config = get_alembic_config()
        script = ScriptDirectory.from_config(config)
        current = get_current_revision()
        head = script.get_current_head()
        logger.info(f"Current revision: {current}")
        logger.info(f"Head revision: {head}")
        return current != head
    except Exception as e:
        logger.error(f"Failed to check migrations: {e}")
        return False


async def run_migrations_on_startup() -> None:
    """Run migrations on application startup.

    This function is called during FastAPI lifespan to ensure
    database is up-to-date before handling requests.
    """
    logger.info("Checking database migrations...")
    if check_migrations_pending():
        logger.info("Pending migrations found, upgrading database...")
        await asyncio.to_thread(run_migrations_upgrade)
    else:
        logger.info("Database is up-to-date, no migrations needed")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    if len(sys.argv) > 1:
        command_name = sys.argv[1]
        if command_name == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            run_migrations_upgrade(revision)
        elif command_name == "downgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
            run_migrations_downgrade(revision)
        elif command_name == "current":
            current = get_current_revision()
            print(f"Current revision: {current}")
        elif command_name == "pending":
            pending = check_migrations_pending()
            print(f"Pending migrations: {pending}")
        else:
            print(
                "Usage: python -m backend.src.migrations [upgrade|downgrade|current|pending]"
            )
    else:
        run_migrations_upgrade()
