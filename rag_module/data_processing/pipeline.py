"""Document processing pipeline orchestration."""

from dataclasses import dataclass
from typing import Any

from settings import get_logger

from .analyzers import AsyncOpenAINewsAnalyzer, DummyAnalyzer
from .chunkers import (
    FixedSizeChunker,
    LangChainRecursiveChunker,
    SentenceChunker,
)
from .cleaners import AzerbaijaniNewsCleaner, TelegramNewsCleaner
from .loaders import TelegramJSONLoader
from .protocols import (
    Document,
    IAsyncTextAnalyzer,
    IDataLoader,
    ITextAnalyzer,
    ITextChunker,
    ITextCleaner,
)

logger = get_logger("pipeline")


def _extract_content_from_item(item: dict[str, Any]) -> str:
    """Extract content text from item.

    Args:
        item: Raw data item

    Returns:
        Content text (detail or text field)
    """
    content = item.get("detail") or item.get("text", "")
    return str(content).strip() if content else ""


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
        content_text = _extract_content_from_item(item)
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
            analyzer=DummyAnalyzer(),
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
            analyzer=DummyAnalyzer(),
            chunker=LangChainRecursiveChunker(
                chunk_size=chunk_size,
                overlap=overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            ),
        )


@dataclass
class AsyncDocumentProcessingPipeline:
    """Async orchestration of document processing with concurrent analysis.

    Implements async processing pipeline for high-throughput batch operations.
    Uses async analyzer for concurrent metadata extraction with semaphore-based
    rate limiting.

    Processing stages:
        1. Load raw data from source
        2. Clean and normalize text (batch)
        3. Analyze and extract metadata (concurrent with rate limiting)
        4. Split into processable chunks (batch)

    Attributes:
        loader: Component for loading data
        cleaner: Component for text cleaning
        analyzer: Async component for metadata extraction
        chunker: Component for text splitting
    """

    loader: IDataLoader
    cleaner: ITextCleaner
    analyzer: IAsyncTextAnalyzer
    chunker: ITextChunker

    async def process_async(
        self, source: str, data_source: str | None = None
    ) -> list[Document]:
        """Process documents through async pipeline with concurrent analysis.

        Args:
            source: Path to data source file
            data_source: Name of data source (e.g., 'qafqazinfo', 'operativ')

        Returns:
            List of processed documents with content, metadata, and chunks

        Raises:
            FileNotFoundError: If source file not found
            ValueError: If data validation fails
        """
        logger.info(f"Starting async pipeline processing for: {source}")

        raw_data = self.loader.load(source)
        logger.info(f"Loaded {len(raw_data)} raw items")

        cleaned_items = self._clean_items(raw_data)
        metadata_results = await self._analyze_items_async(
            cleaned_items, data_source
        )
        documents = self._build_documents(
            cleaned_items, metadata_results, data_source
        )

        logger.info(
            f"Async pipeline complete: {len(documents)} documents processed"
        )
        return documents

    def _clean_items(
        self, raw_data: list[dict[str, Any]]
    ) -> list[tuple[int, dict[str, Any], str]]:
        """Clean and filter items from raw data.

        Args:
            raw_data: List of raw data items

        Returns:
            List of tuples (index, item, cleaned_text) for valid items
        """
        cleaned_items = []
        for idx, item in enumerate(raw_data):
            content_text = _extract_content_from_item(item)
            if not content_text:
                logger.warning(f"Item {idx}: no content available, skipping")
                continue

            cleaned_text = self.cleaner.clean(content_text)
            if not cleaned_text:
                logger.warning(
                    f"Item {idx}: empty text after cleaning, skipping"
                )
                continue

            cleaned_items.append((idx, item, cleaned_text))

        logger.info(
            f"Cleaned {len(cleaned_items)} items "
            f"({len(raw_data) - len(cleaned_items)} skipped)"
        )
        return cleaned_items

    async def _analyze_items_async(
        self,
        cleaned_items: list[tuple[int, dict[str, Any], str]],
        data_source: str | None,
    ) -> list[dict[str, Any]]:
        """Analyze items asynchronously with concurrent batch processing.

        Args:
            cleaned_items: List of tuples (index, item, cleaned_text)
            data_source: Name of data source

        Returns:
            List of metadata dictionaries from analysis
        """
        analysis_items: list[tuple[str, dict[str, Any] | None]] = [
            (
                cleaned_text,
                {
                    "date": item.get("date"),
                    "source": data_source,
                    "message_id": item.get("id"),
                },
            )
            for _, item, cleaned_text in cleaned_items
        ]

        logger.info(
            f"Starting async batch analysis for {len(analysis_items)} items"
        )
        metadata_results = await self.analyzer.analyze_batch_async(
            analysis_items
        )
        logger.info("Async batch analysis completed")
        return metadata_results

    def _build_documents(
        self,
        cleaned_items: list[tuple[int, dict[str, Any], str]],
        metadata_results: list[dict[str, Any]],
        data_source: str | None,
    ) -> list[Document]:
        """Build final documents from cleaned items and analysis results.

        Args:
            cleaned_items: List of tuples (index, item, cleaned_text)
            metadata_results: List of metadata from analysis
            data_source: Name of data source

        Returns:
            List of processed documents
        """
        documents = []
        for (idx, item, cleaned_text), analyzed_metadata in zip(
            cleaned_items, metadata_results
        ):
            try:
                base_metadata = {
                    "source": data_source,
                    "url": item.get("url"),
                    "date": item.get("date"),
                    "message_id": item.get("id"),
                    "has_detail": bool(item.get("detail")),
                }

                if item.get("detail") and item.get("text"):
                    base_metadata["short_preview"] = item.get("text")

                metadata = {**base_metadata, **analyzed_metadata}
                chunks = self.chunker.chunk(cleaned_text)

                documents.append(
                    Document(
                        content=cleaned_text, metadata=metadata, chunks=chunks
                    )
                )

                logger.debug(
                    f"Processed item {idx}: {len(chunks)} chunks, "
                    f"category={metadata.get('category')}, "
                    f"importance={metadata.get('importance')}"
                )

            except Exception as e:
                logger.error(f"Error building document for item {idx}: {e}")
                continue

        return documents


class AsyncPipelineFactory:
    """Factory for creating pre-configured async pipelines."""

    @staticmethod
    def create_openai_pipeline(
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        chunk_size: int = 600,
        overlap: int = 100,
        max_concurrent: int = 50,
    ) -> AsyncDocumentProcessingPipeline:
        """Create async pipeline with OpenAI news analyzer.

        Args:
            api_key: OpenAI API key (optional, uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-4o-mini)
            temperature: Temperature for generation (default: 0.1)
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            max_concurrent: Max concurrent API requests (default: 50)

        Returns:
            Async pipeline configured with OpenAI analyzer
        """

        logger.info(
            f"Creating async OpenAI pipeline: "
            f"model={model}, max_concurrent={max_concurrent}"
        )

        return AsyncDocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=AzerbaijaniNewsCleaner(),
            analyzer=AsyncOpenAINewsAnalyzer(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_concurrent=max_concurrent,
            ),
            chunker=FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
        )

    @staticmethod
    def create_default_pipeline(
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        chunk_size: int = 600,
        overlap: int = 100,
        max_concurrent: int = 50,
    ) -> AsyncDocumentProcessingPipeline:
        """Create default async pipeline with LangChain recursive chunking.

        Args:
            api_key: OpenAI API key (optional, uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-4o-mini)
            temperature: Temperature for generation (default: 0.1)
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            max_concurrent: Max concurrent API requests (default: 50)

        Returns:
            Async pipeline with LangChain recursive chunker and OpenAI analyzer
        """

        logger.info(
            f"Creating default async pipeline: "
            f"model={model}, max_concurrent={max_concurrent}"
        )

        return AsyncDocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=AsyncOpenAINewsAnalyzer(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_concurrent=max_concurrent,
            ),
            chunker=LangChainRecursiveChunker(
                chunk_size=chunk_size,
                overlap=overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            ),
        )
