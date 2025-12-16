"""FastAPI application for SearchNewsRAG."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from admin import setup_admin
from auth import router as auth_router
from chats import router as chat_router
from config import get_settings
from database import get_db_manager
from dependencies import get_container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logging_config import get_logger, setup_logging
from migrations import run_migrations_on_startup
from news import router as news_router
from users import router as users_router

settings = get_settings()
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    log_file=None,
)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler.

    Args:
        app: FastAPI application instance

    Yields:
        Control to the application
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

    container = get_container()

    yield

    logger.info("Shutting down SearchNewsRAG API...")
    container.cleanup()

    if settings.async_database_url:
        logger.info("Closing database connections...")
        db_manager = get_db_manager()
        await db_manager.close()


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


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Service status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
