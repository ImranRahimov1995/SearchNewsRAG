"""Vectorization service v2 with relational persistence support."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rag_module.config import get_database_url, get_logger

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
from ..db import Base, NewsDataRepository, create_session_factory
from ..vector_store import ChromaVectorStore, VectorDocument
from ..vector_store.embedding import LangChainEmbedding
from .vectorization import VectorizationConfig, VectorizationService

logger = get_logger("vectorization_service_v2")


@dataclass
class VectorizationConfigV2(VectorizationConfig):
    """Configuration for vectorization service v2 with DB persistence."""

    db_url: str | None = None
    persist_db: bool = True


class VectorizationServiceV2(VectorizationService):
    """Extended vectorization service with optional relational persistence."""

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        config: VectorizationConfigV2,
        data_repository: NewsDataRepository | None = None,
    ):
        config.validate()
        super().__init__(vector_store=vector_store, config=config)
        self.config: VectorizationConfigV2 = config
        self.data_repository = data_repository

    def _create_pipeline(
        self, start_index: int | None = None, end_index: int | None = None
    ) -> DocumentProcessingPipeline | AsyncDocumentProcessingPipeline:
        if self.config.analyzer_mode == "async":
            return self._create_async_pipeline(start_index, end_index)
        if self.config.analyzer_mode == "sync":
            return self._create_sync_pipeline(start_index, end_index)
        return self._create_pipeline_without_analyzer(start_index, end_index)

    def _create_async_pipeline(
        self, start_index: int | None = None, end_index: int | None = None
    ) -> AsyncDocumentProcessingPipeline:
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

    def _vectorize_sync(
        self,
        pipeline: DocumentProcessingPipeline,
        source_path: Path,
        source_name: str,
        start_index: int | None,
        end_index: int | None,
    ) -> list[VectorDocument]:
        logger.info("Processing documents (sync mode)")

        documents = pipeline.process(str(source_path), source_name)

        vector_docs = self._convert_to_vector_documents(documents, source_name)
        self._store_vector_documents(vector_docs)
        self._persist_documents(documents, source_name)

        return vector_docs

    async def _vectorize_async(
        self,
        pipeline: AsyncDocumentProcessingPipeline,
        source_path: Path,
        source_name: str,
        start_index: int | None,
        end_index: int | None,
    ) -> list[VectorDocument]:
        logger.info("Processing documents (async mode)")

        documents = await pipeline.process_async(str(source_path), source_name)

        vector_docs = self._convert_to_vector_documents(documents, source_name)
        self._store_vector_documents(vector_docs)
        self._persist_documents(documents, source_name)

        return vector_docs

    def _persist_documents(
        self, documents: list[Document], source_name: str
    ) -> None:
        if not self.config.persist_db:
            return
        if not self.data_repository:
            return
        self.data_repository.persist_documents(documents, source_name)

    @classmethod
    def create_default(
        cls,
        collection_name: str = "news",
        persist_directory: str = "./chroma_db",
        api_key: str | None = None,
        db_url: str | None = None,
        persist_db: bool | None = None,
        data_repository: NewsDataRepository | None = None,
        **config_kwargs: Any,
    ) -> "VectorizationServiceV2":
        config = VectorizationConfigV2(
            api_key=api_key,
            collection_name=collection_name,
            persist_directory=persist_directory,
            db_url=db_url,
            persist_db=persist_db if persist_db is not None else True,
            **config_kwargs,
        )

        vector_store = cls._create_vector_store(
            config.collection_name,
            config.persist_directory,
            config.embedding_model,
        )

        repository = data_repository
        resolved_db_url = config.db_url or get_database_url()

        if repository is None and config.persist_db and resolved_db_url:
            session_factory = create_session_factory(resolved_db_url)
            with session_factory() as session:
                engine = session.get_bind()
                if engine:
                    Base.metadata.create_all(engine)
            repository = NewsDataRepository(session_factory)

        logger.info(
            "Creating default VectorizationServiceV2: "
            f"collection={collection_name}, analyzer_mode={config.analyzer_mode}"
        )

        return cls(
            vector_store=vector_store,
            config=config,
            data_repository=repository,
        )

    @staticmethod
    def _create_vector_store(
        collection_name: str,
        persist_directory: str,
        embedding_model: str,
    ) -> ChromaVectorStore:
        embedding = LangChainEmbedding(model=embedding_model)
        return ChromaVectorStore(
            collection_name=collection_name,
            embedding=embedding,
            persist_directory=persist_directory,
        )
