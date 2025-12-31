"""Prediction handler - future forecasts based on historical data."""

import logging
from datetime import datetime

from rag_module.message_templates import PREDICTION_MESSAGES
from rag_module.vector_store.protocols import IVectorStore

from ..protocols import SearchResult

logger = logging.getLogger(__name__)


class PredictionHandler:
    """Handle prediction queries.

    Currently returns guidance to use statistics instead.
    Future: Could implement trend analysis and forecasting.
    """

    def __init__(self, vector_store: IVectorStore):
        """Initialize prediction handler.

        Args:
            vector_store: Vector store instance (for future use)
        """
        self.vector_store = vector_store
        logger.info("Initialized PredictionHandler")

    def retrieve(
        self, query: str, entities: list, top_k: int = 10, language: str = "az"
    ) -> list[SearchResult]:
        """Handle prediction query.

        Args:
            query: User's prediction question
            entities: Extracted entities
            top_k: Not used
            language: Response language (az/en/ru)

        Returns:
            Static message guiding user to statistics
        """
        logger.info(
            f"Prediction query (redirecting to guidance): '{query[:50]}...'"
        )

        lang = language if language in PREDICTION_MESSAGES else "en"
        message = PREDICTION_MESSAGES[lang]

        return [
            SearchResult(
                doc_id="prediction_guidance",
                content=message,
                score=1.0,
                metadata={
                    "type": "prediction",
                    "language": lang,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        ]
