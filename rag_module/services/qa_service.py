"""Question Answering Service - complete RAG pipeline."""

import logging
from dataclasses import dataclass, field
from typing import Any

from rag_module.query_processing import QueryPipeline
from rag_module.retrieval import LLMResponseGenerator, RetrievalPipeline
from rag_module.retrieval.protocols import SearchResult
from rag_module.vector_store.protocols import IVectorStore

logger = logging.getLogger(__name__)


@dataclass
class SourceInfo:
    """Source information with metadata."""

    id: str
    name: str = "Unknown"
    url: str | None = None


@dataclass
class QAResponse:
    """Complete QA response with all metadata."""

    query: str
    language: str
    intent: str
    answer: str
    sources: list[SourceInfo]
    confidence: str
    key_facts: list[str] = field(default_factory=list)
    search_results: list[SearchResult] = field(default_factory=list)
    total_found: int = 0
    handler_used: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses.

        Returns:
            Complete response dictionary
        """
        return {
            "query": self.query,
            "language": self.language,
            "intent": self.intent,
            "answer": self.answer,
            "sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "url": s.url,
                }
                for s in self.sources
            ],
            "confidence": self.confidence,
            "key_facts": self.key_facts,
            "retrieved_documents": [
                {
                    "doc_id": r.doc_id,
                    "score": r.score,
                    "category": r.metadata.get("category"),
                    "importance": r.metadata.get("importance"),
                    "source": r.metadata.get("source"),
                    "url": r.metadata.get("url"),
                    "preview": r.content[:200],
                }
                for r in self.search_results
            ],
            "total_found": self.total_found,
            "handler_used": self.handler_used,
        }


class QuestionAnsweringService:
    """Complete RAG service - retrieval + LLM generation.

    Full pipeline:
    1. Query Processing (language, translation, NER, intent)
    2. Document Retrieval (vector search)
    3. Answer Generation (LLM with retrieved context)
    """

    def __init__(
        self,
        vector_store: IVectorStore,
        llm_api_key: str,
        llm_model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        top_k: int = 5,
    ):
        """Initialize QA service.

        Args:
            vector_store: Vector store for search
            llm_api_key: OpenAI API key
            llm_model: LLM model to use
            temperature: Generation temperature
            top_k: Number of documents to retrieve
        """
        self.retrieval_pipeline = RetrievalPipeline(
            vector_store=vector_store, query_pipeline=QueryPipeline()
        )

        self.llm_generator = LLMResponseGenerator(
            api_key=llm_api_key, model=llm_model, temperature=temperature
        )

        self.top_k = top_k

        logger.info(
            f"Initialized QuestionAnsweringService: model={llm_model}, top_k={top_k}"
        )

    def answer(self, query: str, top_k: int | None = None) -> QAResponse:
        """Answer question using RAG pipeline.

        Args:
            query: User question (any language)
            top_k: Number of documents to retrieve (uses default if None)

        Returns:
            Complete QA response with answer and sources
        """
        k = top_k or self.top_k

        logger.info(f"Processing question: '{query[:100]}'")

        retrieval_result = self.retrieval_pipeline.search(query, top_k=k)

        original_language = (
            retrieval_result.query_result.analysis.metadata.get(
                "original_language",
                retrieval_result.query_result.processed.language,
            )
        )

        llm_response = self.llm_generator.generate(
            query=query,
            search_results=retrieval_result.search_results,
            language=original_language,
        )

        sources = self._extract_sources(
            llm_response.get("sources", []), retrieval_result.search_results
        )

        response = QAResponse(
            query=query,
            language=original_language,
            intent=retrieval_result.query_result.analysis.intent.value,
            answer=llm_response.get("answer", "Cavab yaradıla bilmədi"),
            sources=sources,
            confidence=llm_response.get("confidence", "low"),
            key_facts=llm_response.get("key_facts", []),
            search_results=retrieval_result.search_results,
            total_found=len(retrieval_result.search_results),
            handler_used=retrieval_result.handler_used,
        )

        logger.info(
            f"QA complete: confidence={response.confidence}, "
            f"sources={len(response.sources)}, docs={response.total_found}"
        )

        return response

    def answer_batch(self, queries: list[str]) -> list[QAResponse]:
        """Answer multiple questions in batch.

        Args:
            queries: List of user questions

        Returns:
            List of QA responses
        """
        logger.info(f"Processing batch: {len(queries)} questions")

        responses = []
        for query in queries:
            try:
                response = self.answer(query)
                responses.append(response)
            except Exception as e:
                logger.error(f"Failed to process '{query}': {e}")
                responses.append(
                    QAResponse(
                        query=query,
                        language="unknown",
                        intent="unknown",
                        answer=f"Xəta: {str(e)}",
                        sources=[],
                        confidence="low",
                        search_results=[],
                        total_found=0,
                        handler_used="error",
                    )
                )

        logger.info(
            f"Batch complete: {len(responses)}/{len(queries)} successful"
        )

        return responses

    def _extract_sources(
        self, llm_sources: list[dict], search_results: list[SearchResult]
    ) -> list[SourceInfo]:
        """Extract and enrich source information.

        Args:
            llm_sources: Sources from LLM response
            search_results: Original search results

        Returns:
            List of enriched source information
        """
        sources = []
        results_by_id = {r.doc_id: r for r in search_results}

        for src in llm_sources:
            doc_id = src.get("id", "")
            result = results_by_id.get(doc_id)

            if result:
                sources.append(
                    SourceInfo(
                        id=doc_id,
                        name=src.get("name")
                        or result.metadata.get("source", "Unknown"),
                        url=src.get("url") or result.metadata.get("url"),
                    )
                )
            else:
                sources.append(
                    SourceInfo(
                        id=doc_id,
                        name=src.get("name", "Unknown"),
                        url=src.get("url"),
                    )
                )

        return sources
