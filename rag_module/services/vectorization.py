"""Vectorization service for processing and storing documents."""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

from ..data_processing import (
    AsyncDocumentProcessingPipeline,
    Document,
    DocumentProcessingPipeline,
    TelegramJSONLoader,
)
from ..data_processing.analyzers import (
    AsyncOpenAINewsAnalyzer,
    OpenAINewsAnalyzer,
)
from ..data_processing.chunkers import LangChainRecursiveChunker
from ..data_processing.cleaners import TelegramNewsCleaner
from ..vector_store import ChromaVectorStore, VectorDocument
from ..vector_store.embedding import LangChainEmbedding

logger = logging.getLogger(__name__)


@dataclass
class VectorizationConfig:
    """Configuration for vectorization service.

    Attributes:
        analyzer_mode: Analyzer mode - 'async', 'sync', or 'none'
        api_key: OpenAI API key (optional, uses env var if None)
        model: OpenAI model name for analysis
        temperature: Generation temperature
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks
        max_concurrent: Max concurrent requests for async mode
        collection_name: ChromaDB collection name
        persist_directory: ChromaDB persistence directory
        embedding_model: OpenAI embedding model name
    """

    analyzer_mode: Literal["async", "sync", "none"] = "async"
    api_key: str | None = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    chunk_size: int = 600
    overlap: int = 100
    max_concurrent: int = 50
    collection_name: str = "news"
    persist_directory: str = "./chroma_db"
    embedding_model: str = "text-embedding-3-large"

    def validate(self) -> None:
        """Validate configuration parameters.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.analyzer_mode not in ("async", "sync", "none"):
            raise ValueError(
                "analyzer_mode must be 'async', 'sync', or 'none'"
            )
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.overlap < 0:
            raise ValueError("overlap cannot be negative")
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be less than chunk_size")
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")


@dataclass
class VectorizationResult:
    """Result of vectorization operation.

    Attributes:
        total_documents: Total number of documents processed
        total_chunks: Total number of chunks created
        vectorized_count: Number of chunks successfully vectorized
        failed_count: Number of failed chunks
        source_name: Name of the source
    """

    total_documents: int
    total_chunks: int
    vectorized_count: int
    failed_count: int
    source_name: str


class VectorizationService:
    """Service for processing documents and storing them in vector database.

    Orchestrates the complete pipeline from raw data to vectorized chunks:
    1. Load data from source (with optional slicing)
    2. Process through pipeline (clean → analyze → chunk)
    3. Convert to vector documents
    4. Store in vector database

    Supports both sync and async processing modes.
    """

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        config: VectorizationConfig,
    ):
        """Initialize vectorization service.

        Args:
            vector_store: Vector store for document storage
            config: Service configuration

        Raises:
            ValueError: If configuration is invalid
        """
        config.validate()
        self.vector_store = vector_store
        self.config = config

        logger.info(
            f"Initialized VectorizationService: "
            f"analyzer_mode={config.analyzer_mode}, model={config.model}, "
            f"chunk_size={config.chunk_size}, max_concurrent={config.max_concurrent}"
        )

    def _create_pipeline(
        self, start_index: int | None = None, end_index: int | None = None
    ) -> DocumentProcessingPipeline | AsyncDocumentProcessingPipeline:
        """Create processing pipeline based on config.

        Args:
            start_index: Start index for data slicing
            end_index: End index for data slicing

        Returns:
            Configured pipeline
        """
        if self.config.analyzer_mode == "async":
            return self._create_async_pipeline(start_index, end_index)
        elif self.config.analyzer_mode == "sync":
            return self._create_sync_pipeline(start_index, end_index)
        else:  # 'none'
            return self._create_pipeline_without_analyzer(
                start_index, end_index
            )

    def _create_async_pipeline(
        self, start_index: int | None = None, end_index: int | None = None
    ) -> AsyncDocumentProcessingPipeline:
        """Create async pipeline with LLM analyzer.

        Args:
            start_index: Start index for data slicing
            end_index: End index for data slicing

        Returns:
            Configured async pipeline
        """
        logger.info("Creating async pipeline with analyzer")
        return AsyncDocumentProcessingPipeline(
            loader=TelegramJSONLoader(
                start_index=start_index, end_index=end_index
            ),
            cleaner=TelegramNewsCleaner(),
            analyzer=AsyncOpenAINewsAnalyzer(
                api_key=self.config.api_key,
                model=self.config.model,
                temperature=self.config.temperature,
                max_concurrent=self.config.max_concurrent,
            ),
            chunker=LangChainRecursiveChunker(
                chunk_size=self.config.chunk_size,
                overlap=self.config.overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            ),
        )

    def _create_sync_pipeline(
        self, start_index: int | None = None, end_index: int | None = None
    ) -> DocumentProcessingPipeline:
        """Create sync pipeline with LLM analyzer.

        Args:
            start_index: Start index for data slicing
            end_index: End index for data slicing

        Returns:
            Configured sync pipeline
        """
        logger.info("Creating sync pipeline with analyzer")
        return DocumentProcessingPipeline(
            loader=TelegramJSONLoader(
                start_index=start_index, end_index=end_index
            ),
            cleaner=TelegramNewsCleaner(),
            analyzer=OpenAINewsAnalyzer(
                api_key=self.config.api_key,
                model=self.config.model,
                temperature=self.config.temperature,
            ),
            chunker=LangChainRecursiveChunker(
                chunk_size=self.config.chunk_size,
                overlap=self.config.overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            ),
        )

    def _create_pipeline_without_analyzer(
        self, start_index: int | None = None, end_index: int | None = None
    ) -> DocumentProcessingPipeline:
        """Create pipeline without LLM analyzer (faster, no metadata).

        Args:
            start_index: Start index for data slicing
            end_index: End index for data slicing

        Returns:
            Configured pipeline without analyzer
        """
        logger.info("Creating pipeline without analyzer")
        return DocumentProcessingPipeline(
            loader=TelegramJSONLoader(
                start_index=start_index, end_index=end_index
            ),
            cleaner=TelegramNewsCleaner(),
            analyzer=None,
            chunker=LangChainRecursiveChunker(
                chunk_size=self.config.chunk_size,
                overlap=self.config.overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            ),
        )

    def _convert_to_vector_documents(
        self, documents: list[Document], source_name: str
    ) -> list[VectorDocument]:
        """Convert processed documents to vector documents.

        Args:
            documents: Processed documents with chunks
            source_name: Source identifier for metadata

        Returns:
            List of vector documents ready for storage
        """
        vector_docs = []

        for doc in documents:
            if not doc.chunks:
                doc_id = doc.metadata.get("message_id", "unknown")
                logger.warning(f"Document {doc_id} has no chunks, skipping")
                continue

            doc_vector_docs = self._create_vector_docs_from_document(
                doc, source_name
            )
            vector_docs.extend(doc_vector_docs)

        logger.info(
            f"Converted {len(documents)} documents to "
            f"{len(vector_docs)} vector documents"
        )
        return vector_docs

    def _create_vector_docs_from_document(
        self, doc: Document, source_name: str
    ) -> list[VectorDocument]:
        """Create vector documents from a single document's chunks.

        Args:
            doc: Processed document with chunks
            source_name: Source identifier

        Returns:
            List of vector documents for this document
        """
        vector_docs = []

        for i, chunk in enumerate(doc.chunks):
            vector_doc = self._build_vector_document(
                doc, chunk, i, source_name
            )
            vector_docs.append(vector_doc)

        return vector_docs

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Normalize metadata for ChromaDB compatibility.

        ChromaDB only accepts str, int, float, bool, or None values.
        Converts lists to comma-separated strings.

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Normalized metadata dictionary
        """
        normalized: dict[str, Any] = {}

        for key, value in metadata.items():
            if value is None:
                normalized[key] = None
            elif isinstance(value, (str, int, float, bool)):
                normalized[key] = value
            elif isinstance(value, list):
                normalized[key] = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                continue
            else:
                normalized[key] = str(value)

        return normalized

    def _build_vector_document(
        self,
        doc: Document,
        chunk: str,
        chunk_index: int,
        source_name: str,
    ) -> VectorDocument:
        """Build a single vector document from chunk.

        Args:
            doc: Parent document
            chunk: Chunk text
            chunk_index: Index of this chunk
            source_name: Source identifier

        Returns:
            Vector document ready for storage
        """
        doc_id = doc.metadata.get("message_id", hash(doc.content))
        chunk_id = f"{source_name}_{doc_id}_chunk_{chunk_index}"

        base_metadata = self._normalize_metadata(doc.metadata)

        metadata = {
            **base_metadata,
            "source": source_name,
            "doc_id": doc_id,
            "chunk_index": chunk_index,
            "total_chunks": len(doc.chunks),
            "chunk_size": len(chunk),
            "full_content": doc.content,
        }

        return VectorDocument(
            id=chunk_id,
            content=chunk,
            metadata=metadata,
        )

    def vectorize(
        self,
        source: str | Path,
        source_name: str,
        start_index: int | None = None,
        end_index: int | None = None,
    ) -> VectorizationResult:
        """Process and vectorize documents from source.

        Args:
            source: Path to data source file (JSON)
            source_name: Identifier for the source (used in doc IDs)
            start_index: Start index for slicing (optional)
            end_index: End index for slicing (optional)

        Returns:
            Vectorization result with statistics

        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If processing fails
        """
        self._validate_source(source)

        logger.info(
            f"Starting vectorization: source={source}, "
            f"source_name={source_name}, slice=[{start_index}:{end_index}]"
        )

        pipeline = self._create_pipeline(start_index, end_index)
        vector_docs = self._execute_vectorization(
            pipeline, source, source_name, start_index, end_index
        )

        return self._create_result(vector_docs, source_name)

    def _validate_source(self, source: str | Path) -> None:
        """Validate source file exists.

        Args:
            source: Path to source file

        Raises:
            FileNotFoundError: If source doesn't exist
        """
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

    def _execute_vectorization(
        self,
        pipeline: DocumentProcessingPipeline | AsyncDocumentProcessingPipeline,
        source: str | Path,
        source_name: str,
        start_index: int | None,
        end_index: int | None,
    ) -> list[VectorDocument]:
        """Execute vectorization process.

        Args:
            pipeline: Processing pipeline
            source: Source file path
            source_name: Source identifier
            start_index: Start index for slicing
            end_index: End index for slicing

        Returns:
            List of vectorized documents
        """
        if self.config.analyzer_mode == "async":
            if not (
                isinstance(pipeline, AsyncDocumentProcessingPipeline)
                or hasattr(pipeline, "process_async")
            ):
                raise TypeError(
                    "Async mode requires AsyncDocumentProcessingPipeline"
                )
            async_pipeline = cast(AsyncDocumentProcessingPipeline, pipeline)
            return asyncio.run(
                self._vectorize_async(
                    async_pipeline,
                    Path(source),
                    source_name,
                    start_index,
                    end_index,
                )
            )
        if not (
            isinstance(pipeline, DocumentProcessingPipeline)
            or hasattr(pipeline, "process")
        ):
            raise TypeError("Sync mode requires DocumentProcessingPipeline")
        sync_pipeline = cast(DocumentProcessingPipeline, pipeline)
        return self._vectorize_sync(
            sync_pipeline, Path(source), source_name, start_index, end_index
        )

    def _vectorize_sync(
        self,
        pipeline: DocumentProcessingPipeline,
        source_path: Path,
        source_name: str,
        start_index: int | None,
        end_index: int | None,
    ) -> list[VectorDocument]:
        """Synchronous vectorization.

        Args:
            pipeline: Processing pipeline
            source_path: Path to source file
            source_name: Source identifier
            start_index: Start index for slicing
            end_index: End index for slicing

        Returns:
            List of vector documents
        """
        logger.info("Processing documents (sync mode)")

        documents = pipeline.process(str(source_path), source_name)

        vector_docs = self._convert_to_vector_documents(documents, source_name)
        self._store_vector_documents(vector_docs)

        return vector_docs

    async def _vectorize_async(
        self,
        pipeline: AsyncDocumentProcessingPipeline,
        source_path: Path,
        source_name: str,
        start_index: int | None,
        end_index: int | None,
    ) -> list[VectorDocument]:
        """Asynchronous vectorization.

        Args:
            pipeline: Async processing pipeline
            source_path: Path to source file
            source_name: Source identifier
            start_index: Start index for slicing
            end_index: End index for slicing

        Returns:
            List of vector documents
        """
        logger.info("Processing documents (async mode)")

        documents = await pipeline.process_async(str(source_path), source_name)

        vector_docs = self._convert_to_vector_documents(documents, source_name)
        self._store_vector_documents(vector_docs)

        return vector_docs

    def _store_vector_documents(
        self, vector_docs: list[VectorDocument]
    ) -> None:
        """Store vector documents in vector store.

        Args:
            vector_docs: Documents to store
        """
        logger.info(f"Adding {len(vector_docs)} documents to vector store")
        self.vector_store.add_batch(vector_docs)

    def _create_result(
        self, vector_docs: list[VectorDocument], source_name: str
    ) -> VectorizationResult:
        """Create result summary.

        Args:
            vector_docs: Vectorized documents
            source_name: Source identifier

        Returns:
            Vectorization result with statistics
        """
        total_documents = self._count_unique_documents(vector_docs)

        result = VectorizationResult(
            total_documents=total_documents,
            total_chunks=len(vector_docs),
            vectorized_count=len(vector_docs),
            failed_count=0,
            source_name=source_name,
        )

        logger.info(
            f"Vectorization complete: {result.total_documents} docs, "
            f"{result.total_chunks} chunks, source={source_name}"
        )

        return result

    def _count_unique_documents(
        self, vector_docs: list[VectorDocument]
    ) -> int:
        """Count unique documents from vector documents.

        Args:
            vector_docs: Vector documents

        Returns:
            Number of unique documents
        """
        doc_ids = set()
        for doc in vector_docs:
            doc_id = doc.metadata.get("doc_id", "unknown")
            doc_ids.add(doc_id)
        return len(doc_ids)

    @staticmethod
    def create_default(
        collection_name: str = "news",
        persist_directory: str = "./chroma_db",
        api_key: str | None = None,
        **config_kwargs: Any,
    ) -> "VectorizationService":
        """Create service with default configuration.

        Args:
            collection_name: ChromaDB collection name
            persist_directory: Directory for ChromaDB persistence
            api_key: OpenAI API key (optional)
            **config_kwargs: Additional parameters for VectorizationConfig

        Returns:
            Configured vectorization service
        """
        config = VectorizationConfig(
            api_key=api_key,
            collection_name=collection_name,
            persist_directory=persist_directory,
            **config_kwargs,
        )

        vector_store = VectorizationService._create_vector_store(
            config.collection_name,
            config.persist_directory,
            config.embedding_model,
        )

        logger.info(
            f"Creating default VectorizationService: "
            f"collection={collection_name}, analyzer_mode={config.analyzer_mode}"
        )

        return VectorizationService(
            vector_store=vector_store,
            config=config,
        )

    @staticmethod
    def _create_vector_store(
        collection_name: str,
        persist_directory: str,
        embedding_model: str,
    ) -> ChromaVectorStore:
        """Create vector store instance.

        Args:
            collection_name: Collection name
            persist_directory: Persistence directory
            embedding_model: OpenAI embedding model name

        Returns:
            Configured vector store
        """
        embedding = LangChainEmbedding(model=embedding_model)
        return ChromaVectorStore(
            collection_name=collection_name,
            embedding=embedding,
            persist_directory=persist_directory,
        )
