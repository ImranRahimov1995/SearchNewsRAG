"""Talk handler - conversational queries and greetings."""

import logging
from datetime import datetime

from rag_module.message_templates import TALK_MESSAGES

from ..protocols import SearchResult

logger = logging.getLogger(__name__)


class TalkHandler:
    """Handle conversational queries.

    Returns static multilingual messages without LLM processing.
    """

    def __init__(self):
        """Initialize talk handler."""
        logger.info("Initialized TalkHandler")

    def retrieve(
        self, query: str, entities: list, top_k: int = 10, language: str = "az"
    ) -> list[SearchResult]:
        """Handle conversational query.

        Args:
            query: User's message
            entities: Not used
            top_k: Not used
            language: Response language (az/en/ru)

        Returns:
            Static welcome message
        """
        logger.info(f"Talk query: '{query[:50]}...' (language: {language})")

        lang = language if language in TALK_MESSAGES else "en"
        message = TALK_MESSAGES[lang]

        return [
            SearchResult(
                doc_id="talk_response",
                content=message,
                score=1.0,
                metadata={
                    "type": "talk",
                    "language": lang,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        ]
