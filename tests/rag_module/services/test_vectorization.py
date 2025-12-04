"""Tests for vectorization service."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from rag_module.data_processing import Document
from rag_module.services.vectorization import (
    VectorizationConfig,
    VectorizationResult,
    VectorizationService,
)
from rag_module.vector_store import VectorDocument


@pytest.fixture
def mock_vector_store():
    """Create mock vector store."""
    store = Mock()
    store.add_batch.return_value = ["id1", "id2", "id3"]
    return store


@pytest.fixture
def default_config():
    """Create default configuration."""
    return VectorizationConfig()


@pytest.fixture
def sample_documents():
    """Create sample processed documents."""
    return [
        Document(
            content="Full content 1",
            metadata={
                "message_id": "1",
                "title": "News 1",
                "category": "politics",
                "llm_analysis_exists": True,
            },
            chunks=[
                "Chunk 1 part 1",
                "Chunk 1 part 2",
            ],
        ),
        Document(
            content="Full content 2",
            metadata={
                "message_id": "2",
                "title": "News 2",
                "category": "economy",
                "llm_analysis_exists": True,
            },
            chunks=[
                "Chunk 2 part 1",
            ],
        ),
    ]


@pytest.fixture
def temp_json_file(tmp_path):
    """Create temporary JSON file."""
    json_file = tmp_path / "test_data.json"
    json_file.write_text('[{"id": 1, "text": "Test content"}]')
    return json_file


class TestVectorizationConfig:
    """Test VectorizationConfig dataclass."""

    def test_create_config_with_defaults(self):
        """Test creating config with default values."""
        config = VectorizationConfig()

        assert config.analyzer_mode == "async"
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.1
        assert config.chunk_size == 600
        assert config.overlap == 100
        assert config.max_concurrent == 50
        assert config.collection_name == "news"
        assert config.persist_directory == "./chroma_db"
        assert config.embedding_model == "text-embedding-3-small"

    def test_create_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = VectorizationConfig(
            analyzer_mode="sync",
            model="gpt-4",
            chunk_size=800,
            overlap=150,
            max_concurrent=100,
        )

        assert config.analyzer_mode == "sync"
        assert config.model == "gpt-4"
        assert config.chunk_size == 800
        assert config.overlap == 150
        assert config.max_concurrent == 100

    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        config = VectorizationConfig()
        config.validate()

    def test_validate_invalid_analyzer_mode(self):
        """Test validation fails with invalid analyzer_mode."""
        config = VectorizationConfig(analyzer_mode="invalid")

        with pytest.raises(
            ValueError,
            match="analyzer_mode must be 'async', 'sync', or 'none'",
        ):
            config.validate()

    def test_validate_invalid_chunk_size(self):
        """Test validation fails with invalid chunk_size."""
        config = VectorizationConfig(chunk_size=0)

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            config.validate()

    def test_validate_negative_overlap(self):
        """Test validation fails with negative overlap."""
        config = VectorizationConfig(overlap=-1)

        with pytest.raises(ValueError, match="overlap cannot be negative"):
            config.validate()

    def test_validate_overlap_exceeds_chunk_size(self):
        """Test validation fails when overlap >= chunk_size."""
        config = VectorizationConfig(chunk_size=100, overlap=100)

        with pytest.raises(
            ValueError, match="overlap must be less than chunk_size"
        ):
            config.validate()

    def test_validate_invalid_max_concurrent(self):
        """Test validation fails with invalid max_concurrent."""
        config = VectorizationConfig(max_concurrent=0)

        with pytest.raises(
            ValueError, match="max_concurrent must be positive"
        ):
            config.validate()

    def test_validate_invalid_temperature(self):
        """Test validation fails with invalid temperature."""
        config = VectorizationConfig(temperature=3.0)

        with pytest.raises(
            ValueError, match="temperature must be between 0 and 2"
        ):
            config.validate()


class TestVectorizationService:
    """Test VectorizationService functionality."""

    def test_init(self, mock_vector_store, default_config):
        """Test service initialization."""
        service = VectorizationService(
            vector_store=mock_vector_store,
            config=default_config,
        )

        assert service.vector_store == mock_vector_store
        assert service.config == default_config

    def test_init_validates_config(self, mock_vector_store):
        """Test initialization validates configuration."""
        invalid_config = VectorizationConfig(chunk_size=-1)

        with pytest.raises(ValueError):
            VectorizationService(
                vector_store=mock_vector_store,
                config=invalid_config,
            )

    def test_convert_to_vector_documents(
        self, mock_vector_store, default_config, sample_documents
    ):
        """Test conversion of documents to vector documents."""
        service = VectorizationService(
            vector_store=mock_vector_store, config=default_config
        )

        vector_docs = service._convert_to_vector_documents(
            sample_documents, "test_source"
        )

        assert len(vector_docs) == 3

        assert vector_docs[0].id == "test_source_1_chunk_0"
        assert vector_docs[0].content == "Chunk 1 part 1"
        assert vector_docs[0].metadata["source"] == "test_source"
        assert vector_docs[0].metadata["doc_id"] == "1"
        assert vector_docs[0].metadata["chunk_index"] == 0
        assert vector_docs[0].metadata["total_chunks"] == 2
        assert vector_docs[0].metadata["category"] == "politics"

        assert vector_docs[1].id == "test_source_1_chunk_1"
        assert vector_docs[1].content == "Chunk 1 part 2"

        assert vector_docs[2].id == "test_source_2_chunk_0"
        assert vector_docs[2].content == "Chunk 2 part 1"
        assert vector_docs[2].metadata["total_chunks"] == 1

    def test_convert_skips_documents_without_chunks(
        self, mock_vector_store, default_config
    ):
        """Test that documents without chunks are skipped."""
        service = VectorizationService(
            vector_store=mock_vector_store, config=default_config
        )

        documents = [
            Document(
                content="Content",
                metadata={"message_id": "1"},
                chunks=[],
            )
        ]

        vector_docs = service._convert_to_vector_documents(
            documents, "test_source"
        )

        assert len(vector_docs) == 0

    def test_create_result(self, mock_vector_store, default_config):
        """Test result creation."""
        service = VectorizationService(
            vector_store=mock_vector_store, config=default_config
        )

        vector_docs = [
            VectorDocument(
                id="src_1_chunk_0",
                content="Chunk 1",
                metadata={"doc_id": "1"},
            ),
            VectorDocument(
                id="src_1_chunk_1",
                content="Chunk 2",
                metadata={"doc_id": "1"},
            ),
            VectorDocument(
                id="src_2_chunk_0",
                content="Chunk 3",
                metadata={"doc_id": "2"},
            ),
        ]

        result = service._create_result(vector_docs, "test_source")

        assert isinstance(result, VectorizationResult)
        assert result.total_documents == 2
        assert result.total_chunks == 3
        assert result.vectorized_count == 3
        assert result.failed_count == 0
        assert result.source_name == "test_source"

    def test_vectorize_sync_mode(self, mock_vector_store, temp_json_file):
        """Test synchronous vectorization."""
        config = VectorizationConfig(analyzer_mode="sync")
        service = VectorizationService(
            vector_store=mock_vector_store, config=config
        )

        # Mock the pipeline
        mock_pipeline = Mock()
        mock_pipeline.process.return_value = [
            Document(
                content="Content",
                metadata={"message_id": "1", "title": "Test"},
                chunks=["Chunk 1"],
            )
        ]

        with patch.object(
            service, "_create_sync_pipeline", return_value=mock_pipeline
        ):
            result = service.vectorize(
                source=temp_json_file,
                source_name="test_source",
                start_index=0,
                end_index=10,
            )

        assert isinstance(result, VectorizationResult)
        assert result.total_documents == 1
        assert result.total_chunks == 1
        assert result.source_name == "test_source"

        mock_pipeline.process.assert_called_once()
        mock_vector_store.add_batch.assert_called_once()

    def test_vectorize_async_mode(self, mock_vector_store, temp_json_file):
        """Test asynchronous vectorization."""
        config = VectorizationConfig(analyzer_mode="async")
        service = VectorizationService(
            vector_store=mock_vector_store, config=config
        )

        # Mock the async pipeline
        mock_pipeline = AsyncMock()
        mock_pipeline.process_async.return_value = [
            Document(
                content="Content",
                metadata={"message_id": "1", "title": "Test"},
                chunks=["Chunk 1"],
            )
        ]

        with patch.object(
            service, "_create_async_pipeline", return_value=mock_pipeline
        ):
            result = service.vectorize(
                source=temp_json_file,
                source_name="test_source",
            )

        assert isinstance(result, VectorizationResult)
        assert result.total_documents == 1
        assert result.total_chunks == 1

        mock_pipeline.process_async.assert_called_once()
        mock_vector_store.add_batch.assert_called_once()

    def test_vectorize_file_not_found(self, mock_vector_store, default_config):
        """Test error when source file doesn't exist."""
        service = VectorizationService(
            vector_store=mock_vector_store, config=default_config
        )

        with pytest.raises(FileNotFoundError):
            service.vectorize(
                source="nonexistent.json", source_name="test_source"
            )

    @patch("rag_module.services.vectorization.LangChainEmbedding")
    @patch("rag_module.services.vectorization.ChromaVectorStore")
    def test_create_default(self, mock_store_class, mock_embedding_class):
        """Test creating service with default configuration."""
        mock_embedding = Mock()
        mock_embedding_class.return_value = mock_embedding

        mock_store = Mock()
        mock_store_class.return_value = mock_store

        service = VectorizationService.create_default(
            collection_name="test_collection",
            persist_directory="./test_db",
            api_key="test-key",
            analyzer_mode="async",
            model="gpt-4",
            chunk_size=800,
        )

        assert isinstance(service, VectorizationService)
        assert service.config.analyzer_mode == "async"
        assert service.config.model == "gpt-4"
        assert service.config.chunk_size == 800
        assert service.config.collection_name == "test_collection"
        assert service.config.persist_directory == "./test_db"

        mock_embedding_class.assert_called_once_with(
            model="text-embedding-3-small"
        )
        mock_store_class.assert_called_once_with(
            collection_name="test_collection",
            embedding=mock_embedding,
            persist_directory="./test_db",
        )

    def test_vectorize_with_slicing(self, mock_vector_store, temp_json_file):
        """Test vectorization with start and end indices."""
        config = VectorizationConfig(analyzer_mode="sync")
        service = VectorizationService(
            vector_store=mock_vector_store, config=config
        )

        # Mock the pipeline
        mock_pipeline = Mock()
        mock_pipeline.process.return_value = [
            Document(
                content="Content",
                metadata={"message_id": "1"},
                chunks=["Chunk"],
            )
        ]

        with patch.object(
            service, "_create_sync_pipeline", return_value=mock_pipeline
        ):
            result = service.vectorize(
                source=temp_json_file,
                source_name="test_source",
                start_index=5,
                end_index=15,
            )

        mock_pipeline.process.assert_called_once()
        assert result.total_documents == 1


class TestVectorizationResult:
    """Test VectorizationResult dataclass."""

    def test_create_result(self):
        """Test creating VectorizationResult."""
        result = VectorizationResult(
            total_documents=10,
            total_chunks=50,
            vectorized_count=48,
            failed_count=2,
            source_name="test_source",
        )

        assert result.total_documents == 10
        assert result.total_chunks == 50
        assert result.vectorized_count == 48
        assert result.failed_count == 2
        assert result.source_name == "test_source"
