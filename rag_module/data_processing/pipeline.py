"""Document processing pipeline orchestration."""

from dataclasses import dataclass
from typing import Any

from settings import get_logger

from .analyzers import DummyAnalyzer, NewsClassifier
from .chunkers import (
    FixedSizeChunker,
    LangChainRecursiveChunker,
    SentenceChunker,
)
from .cleaners import AzerbaijaniNewsCleaner, TelegramNewsCleaner
from .loaders import TelegramJSONLoader
from .protocols import (
    Document,
    IDataLoader,
    ITextAnalyzer,
    ITextChunker,
    ITextCleaner,
)

logger = get_logger("pipeline")


@dataclass
class DocumentProcessingPipeline:
    """Orchestrates document processing through configurable stages.

    Implements dependency inversion principle by depending on interfaces
    rather than concrete implementations. Allows flexible composition of
    processing components.

    Processing stages:
        1. Load raw data from source
        2. Clean and normalize text
        3. Analyze and extract metadata
        4. Split into processable chunks

    Attributes:
        loader: Component for loading data
        cleaner: Component for text cleaning
        analyzer: Component for metadata extraction
        chunker: Component for text splitting
    """

    loader: IDataLoader
    cleaner: ITextCleaner
    analyzer: ITextAnalyzer | None
    chunker: ITextChunker

    def process(
        self, source: str, data_source: str | None = None
    ) -> list[Document]:
        """Process documents through entire pipeline.

        Args:
            source: Path to data source file
            data_source: Name of data source (e.g., 'qafqazinfo', 'operativ')

        Returns:
            List of processed documents with content, metadata, and chunks

        Raises:
            FileNotFoundError: If source file not found
            ValueError: If data validation fails
        """
        logger.info(f"Starting pipeline processing for: {source}")

        raw_data = self.loader.load(source)
        logger.info(f"Loaded {len(raw_data)} raw items")

        documents = []

        for idx, item in enumerate(raw_data):
            try:
                document = self._process_single_item(item, idx, data_source)
                if document:
                    documents.append(document)

            except Exception as e:
                logger.error(f"Error processing item {idx}: {e}")
                continue

        logger.info(f"Pipeline complete: {len(documents)} documents processed")
        return documents

    def _process_single_item(
        self, item: dict[str, Any], idx: int, data_source: str | None
    ) -> Document | None:
        """Process a single item through the pipeline.

        Args:
            item: Raw data item
            idx: Item index for logging
            data_source: Name of data source

        Returns:
            Processed document or None if item should be skipped
        """
        content_text = self._extract_content(item)
        if not content_text:
            logger.warning(f"Item {idx}: no content available, skipping")
            return None

        cleaned_text = self.cleaner.clean(content_text)
        if not cleaned_text:
            logger.warning(f"Item {idx}: empty text after cleaning, skipping")
            return None

        metadata = self._build_metadata(item, cleaned_text, data_source)
        chunks = self.chunker.chunk(cleaned_text)

        logger.debug(
            f"Processed item {idx}: {len(chunks)} chunks, "
            f"category={metadata.get('category')}, "
            f"importance={metadata.get('importance')}"
        )

        return Document(content=cleaned_text, metadata=metadata, chunks=chunks)

    def _extract_content(self, item: dict[str, Any]) -> str:
        """Extract content text from item.

        Args:
            item: Raw data item

        Returns:
            Content text (detail or text field)
        """
        content = item.get("detail") or item.get("text", "")
        return str(content).strip() if content else ""

    def _build_metadata(
        self,
        item: dict[str, Any],
        cleaned_text: str,
        data_source: str | None,
    ) -> dict[str, Any]:
        """Build metadata dictionary for document.

        Args:
            item: Raw data item
            cleaned_text: Cleaned content text
            data_source: Name of data source

        Returns:
            Complete metadata dictionary
        """
        base_metadata = {
            "source": data_source,
            "url": item.get("url"),
            "date": item.get("date"),
            "message_id": item.get("id"),
            "has_detail": bool(item.get("detail")),
        }

        if item.get("detail") and item.get("text"):
            base_metadata["short_preview"] = item.get("text")

        if self.analyzer is not None:
            analysis_context = {
                "date": item.get("date"),
                "source": data_source,
                "message_id": item.get("id"),
            }
            analyzed_metadata = self.analyzer.analyze(
                cleaned_text, analysis_context
            )
            return {**base_metadata, **analyzed_metadata}

        return base_metadata


class PipelineFactory:
    """Factory for creating pre-configured pipelines."""

    @staticmethod
    def create_telegram_pipeline() -> DocumentProcessingPipeline:
        """Create pipeline optimized for Telegram news messages.

        Returns:
            Pipeline configured with Telegram-specific components
        """
        logger.info("Creating Telegram news pipeline")

        return DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=DummyAnalyzer(),
            chunker=SentenceChunker(max_sentences=3),
        )

    @staticmethod
    def create_azerbaijani_pipeline(
        llm_client=None,
    ) -> DocumentProcessingPipeline:
        """Create pipeline for Azerbaijani news with date context.

        Args:
            llm_client: Optional LLM client for advanced classification

        Returns:
            Pipeline configured for Azerbaijani news processing
        """
        logger.info("Creating Azerbaijani news pipeline")

        return DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=AzerbaijaniNewsCleaner(),
            analyzer=NewsClassifier(llm_client=llm_client),
            chunker=FixedSizeChunker(chunk_size=512, overlap=50),
        )

    @staticmethod
    def default_pipeline(
        chunk_size: int = 512,
        overlap: int = 50,
    ) -> DocumentProcessingPipeline:
        """Create pipeline with LangChain recursive chunking.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            Pipeline with LangChain RecursiveCharacterTextSplitter
        """
        logger.info(
            "Creating default with LangChain recursive chunker pipeline"
        )

        return DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=NewsClassifier(llm_client=None),
            chunker=LangChainRecursiveChunker(
                chunk_size=chunk_size,
                overlap=overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            ),
        )
