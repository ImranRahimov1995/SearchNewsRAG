"""LLM-based news content analyzer for metadata extraction.

Provides both async and sync implementations for analyzing Azerbaijani news
articles using OpenAI Chat Completions API. Extracts comprehensive metadata
including categories, entities, sentiment, and importance scores.

Async version supports concurrent analysis with semaphore-based rate limiting.
"""

import asyncio
import json
from typing import Any, cast

from openai import AsyncOpenAI, OpenAI

from rag_module.data_processing.analyzers.base import BaseTextAnalyzer
from rag_module.promts.news_analyzer_prompts import (
    ANALYZER_SYSTEM_PROMPT as SYSTEM_PROMPT,
)
from rag_module.promts.news_analyzer_prompts import (
    ANALYZER_USER_PROMPT_TEMPLATE as USER_PROMPT_TEMPLATE,
)
from settings import get_logger

logger = get_logger("news_analyzer")


def parse_entities(
    entities_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Parse and validate entity data.

    Args:
        entities_data: Raw entity data from LLM

    Returns:
        Validated list of entity dictionaries
    """
    entities = []
    for entity in entities_data:
        if not isinstance(entity, dict):
            continue

        if "text" not in entity or "type" not in entity:
            continue

        entities.append(
            {
                "text": entity["text"],
                "type": entity["type"],
                "normalized": entity.get("normalized", entity["text"]),
                "role": entity.get("role"),
                "confidence": entity.get("confidence", 0.8),
            }
        )

    return entities


def build_metadata_from_llm_response(
    data: dict[str, Any], context: dict[str, Any] | None
) -> dict[str, Any]:
    """Build metadata dictionary from LLM response data.

    Args:
        data: Parsed JSON data from LLM
        context: Optional context information

    Returns:
        Structured metadata dictionary
    """
    entities = parse_entities(data.get("entities", []))

    metadata = {
        "category": data.get("category", "other"),
        "subcategories": data.get("subcategories", []),
        "topics": data.get("topics", []),
        "keywords": data.get("keywords", []),
        "entities": entities,
        "sentiment": data.get("sentiment", "neutral"),
        "sentiment_score": data.get("sentiment_score", 0.0),
        "importance": data.get("importance", 5),
        "geographic_scope": data.get("geographic_scope", "unknown"),
        "temporal_relevance": data.get("temporal_relevance", "current"),
        "target_audience": data.get("target_audience", []),
        "summary": data.get("summary", ""),
        "reasoning": data.get("reasoning", ""),
        "llm_analysis_exists": True,
        "analysis_error": False,
        "entity_count": len(entities),
        "keyword_count": len(data.get("keywords", [])),
        "topic_count": len(data.get("topics", [])),
    }

    if context:
        metadata["source"] = context.get("source")
        metadata["date"] = context.get("date")
        if "url" in context:
            metadata["url"] = context["url"]

    metadata["is_breaking"] = data.get("temporal_relevance") == "breaking"
    metadata["is_high_importance"] = data.get("importance", 5) >= 8
    metadata["is_local"] = data.get("geographic_scope") == "local"
    metadata["is_positive"] = data.get("sentiment") == "positive"
    metadata["is_negative"] = data.get("sentiment") == "negative"

    return metadata


def build_fallback_metadata(
    text: str, context: dict[str, Any] | None
) -> dict[str, Any]:
    """Build fallback metadata with basic statistics when LLM fails.

    Args:
        text: Original text content
        context: Optional context information

    Returns:
        Basic metadata dictionary with default values
    """
    logger.warning("Using fallback analysis with basic statistics")

    metadata = {
        "category": "other",
        "subcategories": [],
        "topics": [],
        "keywords": [],
        "entities": [],
        "sentiment": "neutral",
        "sentiment_score": 0.0,
        "importance": 5,
        "geographic_scope": "unknown",
        "temporal_relevance": "current",
        "target_audience": [],
        "summary": "",
        "reasoning": "Fallback analysis - LLM unavailable",
        "llm_analysis_exists": False,
        "analysis_error": True,
        "word_count": len(text.split()),
        "length": len(text),
        "entity_count": 0,
        "keyword_count": 0,
        "topic_count": 0,
        "is_breaking": False,
        "is_high_importance": False,
        "is_local": False,
        "is_positive": False,
        "is_negative": False,
    }

    if context:
        metadata["source"] = context.get("source")
        metadata["date"] = context.get("date")
        if "url" in context:
            metadata["url"] = context["url"]

    return metadata


class OpenAINewsAnalyzer(BaseTextAnalyzer):
    """Synchronous OpenAI-based news content analyzer for Azerbaijani.

    Performs comprehensive content analysis:
    1. Category classification (politics, economy, society, etc.)
    2. Named Entity Recognition (people, organizations, locations)
    3. Key topics and keywords extraction
    4. Sentiment analysis
    5. Importance scoring
    6. Geographic and temporal metadata

    Falls back to basic analysis when LLM is unavailable.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_content_length: int = 4000,
    ):
        """Initialize the synchronous news content analyzer.

        Args:
            api_key: OpenAI API key (optional, uses OPENAI_API_KEY env var if not provided)
            model: Model to use for analysis (default: gpt-4o-mini)
            temperature: Temperature for generation (default: 0.1)
            max_content_length: Maximum content length in characters
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_content_length = max_content_length

        logger.info(
            f"OpenAINewsAnalyzer initialized: model={model}, "
            f"temperature={temperature}"
        )

    def analyze(
        self, text: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analyze news content and extract comprehensive metadata.

        Args:
            text: Full news article text
            context: Optional context with source, date, url, etc.

        Returns:
            Dictionary with extracted metadata including:
            - category, subcategories, topics, keywords
            - entities (people, organizations, locations, etc.)
            - sentiment, importance, geographic_scope
            - Various boolean flags for filtering
            - Basic statistics (word_count, entity_count, etc.)

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Content cannot be empty")

        try:
            content = text[: self.max_content_length]

            user_prompt = USER_PROMPT_TEMPLATE.format(content=content)

            logger.debug(f"Analyzing content: {len(content)} chars")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
            )

            result = self._parse_response(response, context)

            logger.info(
                f"Content analyzed: category={result.get('category')}, "
                f"importance={result.get('importance')}, "
                f"entities={result.get('entity_count')}"
            )

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return build_fallback_metadata(text, context)

    def _parse_response(
        self, response: Any, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Parse OpenAI API response and extract structured metadata.

        Args:
            response: OpenAI API response object
            context: Optional context information

        Returns:
            Structured metadata dictionary
        """
        content = response.choices[0].message.content

        try:

            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return build_fallback_metadata(
                response.choices[0].message.content, context
            )

        return build_metadata_from_llm_response(data, context)


class AsyncOpenAINewsAnalyzer:
    """Async OpenAI-based news content analyzer with rate limiting.

    Supports concurrent analysis with semaphore-based concurrency control
    (max 50 concurrent requests). Ideal for batch processing large datasets.

    Uses same analysis logic as OpenAINewsAnalyzer but with async API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_content_length: int = 4000,
        max_concurrent: int = 50,
    ):
        """Initialize the async news content analyzer.

        Args:
            api_key: OpenAI API key (optional, uses OPENAI_API_KEY env var if not provided)
            model: Model to use for analysis (default: gpt-4o-mini)
            temperature: Temperature for generation (default: 0.1)
            max_content_length: Maximum content length in characters
            max_concurrent: Maximum concurrent requests (default: 50)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_content_length = max_content_length
        self.semaphore = asyncio.Semaphore(max_concurrent)

        logger.info(
            f"AsyncOpenAINewsAnalyzer initialized: model={model}, "
            f"max_concurrent={max_concurrent}"
        )

    async def analyze_async(
        self, text: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analyze news content asynchronously.

        Args:
            text: Full news article text
            context: Optional context with source, date, url, etc.

        Returns:
            Dictionary with extracted metadata

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Content cannot be empty")

        async with self.semaphore:
            try:
                content = text[: self.max_content_length]

                user_prompt = USER_PROMPT_TEMPLATE.format(content=content)

                logger.debug(f"Analyzing content async: {len(content)} chars")

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                )

                result = self._parse_response(response, context)

                logger.info(
                    f"Content analyzed: category={result.get('category')}, "
                    f"importance={result.get('importance')}"
                )

                return result

            except Exception as e:
                logger.error(f"Async analysis failed: {e}")
                return build_fallback_metadata(text, context)

    async def analyze_batch_async(
        self, items: list[tuple[str, dict[str, Any] | None]]
    ) -> list[dict[str, Any]]:
        """Analyze multiple news articles concurrently.

        Args:
            items: List of (text, context) tuples

        Returns:
            List of metadata dictionaries for each item
        """
        logger.info(f"Starting batch async analysis: {len(items)} items")

        tasks = [self.analyze_async(text, context) for text, context in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results: list[dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch item {i} failed: {result}")
                text, context = items[i]
                processed_results.append(
                    build_fallback_metadata(text, context)
                )
            else:
                processed_results.append(cast(dict[str, Any], result))

        logger.info(f"Batch async analysis completed: {len(results)} items")
        return processed_results

    def _parse_response(
        self, response: Any, context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Parse OpenAI API response and extract structured metadata.

        Args:
            response: OpenAI API response object
            context: Optional context information

        Returns:
            Structured metadata dictionary
        """
        content = response.choices[0].message.content

        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return build_fallback_metadata(
                response.choices[0].message.content, context
            )

        return build_metadata_from_llm_response(data, context)
