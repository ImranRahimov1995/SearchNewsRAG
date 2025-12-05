"""LLM response generator - creates answers from retrieved news."""

import json
from typing import Any

from openai import OpenAI

from rag_module.prompts import (
    ANSWER_GENERATION_SYSTEM,
    ANSWER_GENERATION_USER,
    format_context_for_llm,
)
from settings import get_logger

from .protocols import SearchResult

logger = get_logger("llm_generator")


class LLMResponseGenerator:
    """Generate answers from retrieved news using LLM."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
    ):
        """Initialize LLM generator.

        Args:
            api_key: OpenAI API key
            model: Model to use
            temperature: Generation temperature
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

        logger.info(f"Initialized LLMResponseGenerator: model={model}")

    def generate(
        self,
        query: str,
        search_results: list[SearchResult],
        language: str = "az",
    ) -> dict[str, Any]:
        """Generate answer from search results.

        Args:
            query: Original user query
            search_results: Retrieved news articles
            language: Query language

        Returns:
            Dictionary with answer, sources, confidence, key_facts
        """
        if not search_results:
            return {
                "answer": "Təəssüf ki, bu mövzuda heç bir xəbər tapa bilmədim.",
                "sources": [],
                "confidence": "low",
                "language": language,
                "key_facts": [],
            }

        context = format_context_for_llm(search_results)

        user_prompt = ANSWER_GENERATION_USER.format(
            query=query, context=context
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ANSWER_GENERATION_SYSTEM},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            result: dict[str, Any] = json.loads(
                response.choices[0].message.content or "{}"
            )

            logger.info(
                f"Generated answer: confidence={result.get('confidence')}, "
                f"sources={len(result.get('sources', []))}"
            )

            return result

        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            return {
                "answer": f"Xəta baş verdi: {str(e)}",
                "sources": [],
                "confidence": "low",
                "language": language,
                "key_facts": [],
            }
