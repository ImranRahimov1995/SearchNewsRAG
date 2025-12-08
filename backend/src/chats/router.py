"""Chat router for RAG-powered question answering."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from rag_module.services.qa_service import QAResponse, QuestionAnsweringService
from settings import get_logger

from .dependencies import get_qa_service
from .schemas import AskRequest, AskResponse

logger = get_logger("chat_router")

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/ask", response_model=AskResponse, status_code=status.HTTP_200_OK
)
async def ask(
    request: AskRequest,
    qa_service: Annotated[QuestionAnsweringService, Depends(get_qa_service)],
) -> dict[str, Any]:
    """Answer user question using RAG pipeline.

    Args:
        request: Question and retrieval parameters
        qa_service: Injected QA service instance

    Returns:
        Complete answer with sources and metadata

    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Processing query: '{request.query[:100]}'")

        response: QAResponse = qa_service.answer(
            query=request.query, top_k=request.top_k
        )

        logger.info(
            f"Query processed: confidence={response.confidence}, "
            f"sources={len(response.sources)}"
        )

        return response.to_dict()

    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}",
        ) from e
