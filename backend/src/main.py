"""FastAPI application for SearchNewsRAG."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from chats import router as chat_router
from chats.dependencies import get_container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler.

    Args:
        app: FastAPI application instance

    Yields:
        Control to the application
    """
    logger.info("Starting SearchNewsRAG API...")

    container = get_container()
    try:
        container.qa_service
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")

    yield

    logger.info("Shutting down SearchNewsRAG API...")
    container.cleanup()


app = FastAPI(
    title="SearchNewsRAG API",
    description="RAG-powered semantic search for Azerbaijani news",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Service status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")  # nosec B104

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
