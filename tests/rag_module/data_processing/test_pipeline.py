"""Tests for document processing pipeline."""

import json
from unittest.mock import MagicMock

from rag_module.data_processing.analyzers import DummyAnalyzer
from rag_module.data_processing.chunkers import SentenceChunker
from rag_module.data_processing.cleaners import TelegramNewsCleaner
from rag_module.data_processing.loaders import TelegramJSONLoader
from rag_module.data_processing.pipeline import (
    DocumentProcessingPipeline,
    PipelineFactory,
)
from rag_module.data_processing.protocols import Document


class TestDocumentProcessingPipeline:
    """Test DocumentProcessingPipeline functionality."""

    def test_process_basic_flow(self, tmp_path):
        """Test basic pipeline processing flow."""
        test_data = [
            {"id": 1, "text": "Test message one", "date": "2025-11-28"},
            {"id": 2, "text": "Test message two", "date": "2025-11-27"},
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=DummyAnalyzer(),
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 2
        assert all(isinstance(doc, Document) for doc in results)

    def test_process_with_detail_field(self, tmp_path):
        """Test processing items with detail field."""
        test_data = [
            {
                "id": 1,
                "detail": "Detailed content here",
                "date": "2025-11-28",
            }
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=DummyAnalyzer(),
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 1
        assert "detailed content" in results[0].content

    def test_process_with_short_preview(self, tmp_path):
        """Test processing items with both text and detail."""
        test_data = [
            {
                "id": 1,
                "text": "Short preview",
                "detail": "Full detailed content",
                "date": "2025-11-28",
            }
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=DummyAnalyzer(),
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 1
        assert results[0].metadata["has_detail"] is True
        assert results[0].metadata["short_preview"] == "Short preview"
        assert "full detailed content" in results[0].content

    def test_process_without_analyzer(self, tmp_path):
        """Test processing without analyzer."""
        test_data = [{"id": 1, "text": "Test message", "date": "2025-11-28"}]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=None,
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 1
        assert "length" not in results[0].metadata
        assert "word_count" not in results[0].metadata

    def test_process_metadata_structure(self, tmp_path):
        """Test metadata structure in processed documents."""
        test_data = [
            {
                "id": 123,
                "text": "Test",
                "date": "2025-11-28",
                "url": "http://example.com",
            }
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=DummyAnalyzer(),
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test_source")

        metadata = results[0].metadata
        assert metadata["source"] == "test_source"
        assert metadata["url"] == "http://example.com"
        assert metadata["date"] == "2025-11-28"
        assert metadata["message_id"] == 123
        assert metadata["has_detail"] is False

    def test_process_skip_empty_content(self, tmp_path):
        """Test skipping items with empty content."""
        test_data = [
            {"id": 1, "text": "Valid content", "date": "2025-11-28"},
            {"id": 2, "text": "", "date": "2025-11-27"},
            {"id": 3, "text": "   ", "date": "2025-11-26"},
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=None,
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 1
        assert results[0].metadata["message_id"] == 1

    def test_process_handles_errors_gracefully(self, tmp_path):
        """Test pipeline handles processing errors gracefully."""
        test_data = [
            {"id": 1, "text": "Valid message", "date": "2025-11-28"},
            {"id": 2, "text": "Another valid", "date": "2025-11-27"},
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        mock_chunker = MagicMock()
        mock_chunker.chunk.side_effect = [
            ["chunk1"],
            Exception("Chunking failed"),
        ]

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=None,
            chunker=mock_chunker,
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 1

    def test_process_chunks_creation(self, tmp_path):
        """Test chunks are created correctly."""
        test_data = [
            {
                "id": 1,
                "text": "First sentence. Second sentence. Third sentence.",
                "date": "2025-11-28",
            }
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        pipeline = DocumentProcessingPipeline(
            loader=TelegramJSONLoader(),
            cleaner=TelegramNewsCleaner(),
            analyzer=None,
            chunker=SentenceChunker(max_sentences=1),
        )

        results = pipeline.process(str(file_path), data_source="test")

        assert len(results) == 1
        assert len(results[0].chunks) >= 1
        assert all(isinstance(chunk, str) for chunk in results[0].chunks)


class TestPipelineFactory:
    """Test PipelineFactory functionality."""

    def test_create_telegram_pipeline(self):
        """Test creating Telegram pipeline."""
        pipeline = PipelineFactory.create_telegram_pipeline()

        assert isinstance(pipeline, DocumentProcessingPipeline)
        assert isinstance(pipeline.loader, TelegramJSONLoader)
        assert isinstance(pipeline.cleaner, TelegramNewsCleaner)
        assert isinstance(pipeline.analyzer, DummyAnalyzer)
        assert isinstance(pipeline.chunker, SentenceChunker)

    def test_create_azerbaijani_pipeline(self):
        """Test creating Azerbaijani pipeline."""
        pipeline = PipelineFactory.create_azerbaijani_pipeline()

        assert isinstance(pipeline, DocumentProcessingPipeline)
        assert pipeline.analyzer is not None

    def test_create_azerbaijani_pipeline_with_llm(self):
        """Test creating Azerbaijani pipeline with LLM client."""
        pipeline = PipelineFactory.create_azerbaijani_pipeline(llm_client=None)

        assert isinstance(pipeline, DocumentProcessingPipeline)
        assert isinstance(pipeline.analyzer, DummyAnalyzer)

    def test_default_pipeline(self):
        """Test creating default pipeline."""
        pipeline = PipelineFactory.default_pipeline()

        assert isinstance(pipeline, DocumentProcessingPipeline)
        assert pipeline.analyzer is not None

    def test_default_pipeline_custom_params(self):
        """Test creating default pipeline with custom parameters."""
        pipeline = PipelineFactory.default_pipeline(chunk_size=256, overlap=25)

        assert isinstance(pipeline, DocumentProcessingPipeline)
        assert pipeline.chunker.chunk_size == 256
        assert pipeline.chunker.overlap == 25
