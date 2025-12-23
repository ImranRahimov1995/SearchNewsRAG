"""LLM-based query processor using OpenAI for Azerbaijani language.

Performs all query processing in a single API call:
- Language detection and translation
- Text cleaning and normalization
- Named Entity Recognition (NER)
- Intent classification (factoid or unknown)
"""

import json
import logging
from typing import Any

from openai import OpenAI

from rag_module.prompts import (
    QUERY_ANALYZER_SYSTEM_PROMPT,
    QUERY_ANALYZER_USER_PROMPT,
)

from .protocols import (
    Entity,
    EntityType,
    ProcessedQuery,
    QueryAnalysis,
    QueryIntent,
)

logger = logging.getLogger(__name__)


class LLMQueryProcessor:
    """OpenAI-based query processor for Azerbaijani news search.

    Performs complete query understanding in single LLM call:
    1. Language detection (az, en, ru, tr, etc.)
    2. Translation to Azerbaijani (if needed)
    3. Text cleaning and correction
    4. Named Entity Recognition (NER)
    5. Intent classification (factoid or unknown)
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
    ):
        """Initialize LLM query processor.

        Args:
            api_key: OpenAI API key (uses env var if None)
            model: OpenAI model name
            temperature: Generation temperature (lower = more deterministic)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

        logger.info(
            f"Initialized LLMQueryProcessor: model={model}, "
            f"temp={temperature}"
        )

    def process(self, query: str) -> tuple[ProcessedQuery, QueryAnalysis]:
        """Process query through LLM for complete understanding.

        Args:
            query: Raw user query

        Returns:
            Tuple of (processed_query, query_analysis)

        Raises:
            ValueError: If query is empty or LLM response cannot be parsed
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        logger.debug(f"Processing query: '{query}'")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": QUERY_ANALYZER_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": QUERY_ANALYZER_USER_PROMPT.format(
                            query=query
                        ),
                    },
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            result = self._parse_response(response, query)

            logger.info(
                f"Query processed: lang={result[0].language}, "
                f"intent={result[1].intent}, "
                f"entities={len(result[1].entities)}, "
                f"confidence={result[1].confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return self._fallback_processing(query)

    def _parse_response(
        self, response: Any, original_query: str
    ) -> tuple[ProcessedQuery, QueryAnalysis]:
        """Parse LLM JSON response into structured objects.

        Args:
            response: OpenAI API response
            original_query: Original user query

        Returns:
            Tuple of (processed_query, query_analysis)
        """
        content = response.choices[0].message.content
        data = json.loads(content)

        original_lang = data.get("original_language", "az")
        translated = data.get("translated_to_az", original_query)

        processed = ProcessedQuery(
            original=original_query,
            cleaned=data.get("cleaned", translated.lower()),
            corrected=data.get("corrected", data.get("cleaned", translated)),
            language=original_lang,
        )

        entities = []
        for ent_data in data.get("entities", []):
            try:
                entity = Entity(
                    text=ent_data["text"],
                    type=EntityType(ent_data["type"]),
                    normalized=ent_data.get("normalized"),
                    confidence=float(ent_data.get("confidence", 1.0)),
                )
                entities.append(entity)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid entity: {e}")
                continue

        intent_str = data.get("intent", "unknown").lower()
        if intent_str == "factoid":
            intent = QueryIntent.FACTOID
        else:
            intent = QueryIntent.UNKNOWN

        analysis = QueryAnalysis(
            intent=intent,
            entities=entities,
            confidence=float(data.get("confidence", 0.0)),
            keywords=data.get("keywords", []),
            is_local_content=False,
            requires_temporal_filter=False,
            metadata={
                "reasoning": data.get("reasoning", ""),
                "original_language": original_lang,
                "translated_to_az": translated,
            },
        )

        logger.debug(
            f"Parsed: lang={original_lang}, "
            f"corrected='{processed.corrected}', intent={analysis.intent}"
        )

        return processed, analysis

    def _fallback_processing(
        self, query: str
    ) -> tuple[ProcessedQuery, QueryAnalysis]:
        """Fallback processing when LLM fails.

        Args:
            query: Original query

        Returns:
            Basic processed query and analysis
        """
        logger.warning("Using fallback processing")

        cleaned = query.lower().strip()

        processed = ProcessedQuery(
            original=query,
            cleaned=cleaned,
            corrected=cleaned,
            language="az",
        )

        analysis = QueryAnalysis(
            intent=QueryIntent.UNKNOWN,
            entities=[],
            confidence=0.0,
            keywords=cleaned.split(),
            is_local_content=False,
            requires_temporal_filter=False,
            metadata={"error": "LLM processing failed"},
        )

        return processed, analysis
