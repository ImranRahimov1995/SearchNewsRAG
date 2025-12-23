"""FastAPI application for SearchNewsRAG."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from admin import setup_admin
from auth.router import router as auth_router
from chats.router import router as chat_router
from config import get_settings
from database import get_db_manager
from dependencies import get_container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from migrations import run_migrations_on_startup
from news.router import router as news_router
from prometheus_fastapi_instrumentator import Instrumentator
from users.router import router as users_router

from fastapi_logging_config import UVICORN_LOG_CONFIG

settings = get_settings()
logger = logging.getLogger(__name__)


async def startup_handler() -> None:
    """Execute startup tasks.

    Handles:
    - Database migrations
    - Superuser creation
    - Container initialization
    """
    logger.info(
        "Starting SearchNewsRAG API",
        extra={
            "environment": settings.environment,
            "chroma_mode": "client" if settings.chroma_host else "embedded",
        },
    )

    try:
        await run_migrations_on_startup()
    except Exception as e:
        logger.error(f"Migration failed during startup: {e}", exc_info=True)

    try:
        from users.superuser import create_superuser_if_not_exists

        await create_superuser_if_not_exists()
    except Exception as e:
        logger.error(
            f"Superuser creation failed during startup: {e}", exc_info=True
        )


async def shutdown_handler() -> None:
    """Execute shutdown tasks.

    Handles:
    - Container cleanup
    - Database connection cleanup
    """
    logger.info("Shutting down SearchNewsRAG API...")

    container = get_container()
    container.cleanup()

    if settings.async_database_url:
        logger.info("Closing database connections...")
        db_manager = get_db_manager()
        await db_manager.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler.

    Args:
        app: FastAPI application instance

    Yields:
        Control to the application
    """
    await startup_handler()
    yield
    await shutdown_handler()


app = FastAPI(
    title="SearchNewsRAG API",
    description="RAG-powered semantic search for Azerbaijani news",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

setup_admin(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(news_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Service status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        log_config=UVICORN_LOG_CONFIG,
    )
