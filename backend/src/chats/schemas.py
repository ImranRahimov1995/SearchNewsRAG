"""Pydantic schemas for chat API."""

from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request model for chat ask endpoint."""

    query: str = Field(
        ..., min_length=1, description="User question in any language"
    )
    top_k: int | None = Field(
        None, ge=1, le=20, description="Number of documents to retrieve"
    )


class AskResponse(BaseModel):
    """Response model for chat ask endpoint."""

    query: str
    language: str
    intent: str
    answer: str
    sources: list[dict[str, Any]]
    confidence: str
    key_facts: list[str]
    retrieved_documents: list[dict[str, Any]]
    total_found: int
    handler_used: str
