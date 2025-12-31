"""Attacking handler - detect and reject malicious requests."""

import logging
from datetime import datetime

from rag_module.message_templates import ATTACKING_MESSAGES

from ..protocols import SearchResult

logger = logging.getLogger(__name__)


class AttackingHandler:
    """Handle malicious or attacking queries.

    Logs suspicious activity and returns warning message.
    """

    def __init__(self):
        """Initialize attacking handler."""
        logger.info("Initialized AttackingHandler")

    def retrieve(
        self, query: str, entities: list, top_k: int = 10, language: str = "az"
    ) -> list[SearchResult]:
        """Handle malicious query.

        Args:
            query: Suspicious user query
            entities: Not used
            top_k: Not used
            language: Response language (az/en/ru)

        Returns:
            Warning message
        """
        logger.warning(
            f"SECURITY: Attacking query detected: '{query[:100]}...' "
            f"(language: {language})"
        )

        lang = language if language in ATTACKING_MESSAGES else "en"
        message = ATTACKING_MESSAGES[lang]

        return [
            SearchResult(
                doc_id="security_warning",
                content=message,
                score=1.0,
                metadata={
                    "type": "attacking",
                    "language": lang,
                    "timestamp": datetime.now().isoformat(),
                    "query_sample": query[:50],
                },
            )
        ]
