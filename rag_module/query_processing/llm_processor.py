"""LLM-based query processor using OpenAI GPT-3.5 for Azerbaijani language.

Performs all query processing in a single API call:
- Text cleaning and normalization
- Grammar and spelling correction
- Named Entity Recognition
- Intent classification
"""

import json
from typing import Any

from openai import OpenAI

from settings import get_logger

from .protocols import (
    Entity,
    EntityType,
    ProcessedQuery,
    QueryAnalysis,
    QueryIntent,
)

logger = get_logger("llm_query_processor")


class LLMQueryProcessor:
    """OpenAI GPT-3.5 based query processor for Azerbaijani.

    Performs complete query understanding in single LLM call:
    1. Text cleaning (lowercase, remove noise)
    2. Grammar/spelling correction for Azerbaijani
    3. Named Entity Recognition
    4. Intent classification
    """

    SYSTEM_PROMPT = """Sən Azərbaycan dilində sorğuları təhlil edən AI köməkçisisən.

Vəzifələrin:
1. Sorğunu təmizlə (kiçik hərflərə çevir, boşluqları normallaşdır)
2. Qrammatik və orfoqrafik səhvləri düzəlt
3. Named Entity Recognition (NER) - şəxs, təşkilat, yer, tarix, sənəd
4. Sorğunun növünü müəyyən et

Sorğu növləri:
- factoid: "kim", "nə", "harada", "nə vaxt" sualları
- definition: anlayış izahı istəyi
- statistical: "neçə", "faiz", "statistika", "dinamika"
- analytical: "niyə", "izah et", "səbəb"
- task_oriented: "yarat", "qur", "hesabla"
- opinion: subyektiv, fikir sorğusu
- local_az: Azərbaycan-spesifik (məsələn: "xalq bank", "asan imza")
- unknown: müəyyən edilə bilməyən

Entity növləri: person, organization, location, date, document, number, money, other

VACIB: Cavabı YALNIZ JSON formatında ver, başqa heç nə əlavə etmə!"""

    USER_PROMPT_TEMPLATE = """Sorğu: "{query}"

JSON cavab (mütləq bu strukturda):
{{
  "cleaned": "təmizlənmiş sorğu",
  "corrected": "düzəldilmiş sorğu",
  "language": "az",
  "intent": "intent_növü",
  "confidence": 0.0-1.0,
  "entities": [
    {{"text": "entity", "type": "növ", "normalized": "normallaşdırılmış", "confidence": 0.0-1.0}}
  ],
  "keywords": ["açar", "sözlər"],
  "is_local_content": true/false,
  "requires_temporal_filter": true/false,
  "reasoning": "qısa izahat"
}}"""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-3.5-turbo",
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
            ValueError: If LLM response cannot be parsed
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        logger.debug(f"Processing query: '{query}'")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": self.USER_PROMPT_TEMPLATE.format(
                            query=query
                        ),
                    },
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            result = self._parse_response(response, query)

            logger.info(
                f"Query processed: intent={result[1].intent}, "
                f"entities={len(result[1].entities)}, "
                f"confidence={result[1].confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Error processing query: {e}")
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

        processed = ProcessedQuery(
            original=original_query,
            cleaned=data.get("cleaned", original_query.lower()),
            corrected=data.get(
                "corrected", data.get("cleaned", original_query)
            ),
            language=data.get("language", "az"),
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

        try:
            intent = QueryIntent(data.get("intent", "unknown"))
        except ValueError:
            logger.warning(f"Unknown intent: {data.get('intent')}")
            intent = QueryIntent.UNKNOWN

        analysis = QueryAnalysis(
            intent=intent,
            entities=entities,
            confidence=float(data.get("confidence", 0.0)),
            keywords=data.get("keywords", []),
            is_local_content=bool(data.get("is_local_content", False)),
            requires_temporal_filter=bool(
                data.get("requires_temporal_filter", False)
            ),
            metadata={"reasoning": data.get("reasoning", "")},
        )

        logger.debug(
            f"Parsed: cleaned='{processed.cleaned}', "
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
