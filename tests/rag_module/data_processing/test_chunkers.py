"""Tests for text chunkers."""

from rag_module.data_processing.chunkers import (
    FixedSizeChunker,
    LangChainRecursiveChunker,
    SentenceChunker,
)


class TestSentenceChunker:
    """Test SentenceChunker functionality."""

    def test_chunk_single_sentence(self):
        """Test chunking single sentence."""
        chunker = SentenceChunker(max_sentences=1)
        text = "This is one sentence."
        result = chunker.chunk(text)

        assert len(result) == 1
        assert "This is one sentence" in result[0]

    def test_chunk_multiple_sentences(self):
        """Test chunking multiple sentences."""
        chunker = SentenceChunker(max_sentences=2)
        text = (
            "First sentence. Second sentence. Third sentence. Fourth sentence."
        )
        result = chunker.chunk(text)

        assert len(result) == 2
        assert "First sentence" in result[0]
        assert "Second sentence" in result[0]
        assert "Third sentence" in result[1]
        assert "Fourth sentence" in result[1]

    def test_chunk_with_max_sentences_three(self):
        """Test chunking with 3 sentences per chunk."""
        chunker = SentenceChunker(max_sentences=3)
        text = "One. Two. Three. Four. Five."
        result = chunker.chunk(text)

        assert len(result) == 2

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = SentenceChunker(max_sentences=2)
        result = chunker.chunk("")

        assert result == []

    def test_chunk_single_long_sentence(self):
        """Test chunking single long sentence."""
        chunker = SentenceChunker(max_sentences=2)
        text = "This is a very long sentence without any punctuation marks"
        result = chunker.chunk(text)

        assert len(result) == 1
        assert result[0] == text

    def test_chunk_different_punctuation(self):
        """Test chunking with different punctuation marks."""
        chunker = SentenceChunker(max_sentences=1)
        text = "Question? Exclamation! Statement."
        result = chunker.chunk(text)

        assert len(result) == 3


class TestFixedSizeChunker:
    """Test FixedSizeChunker functionality."""

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=10)
        text = "Short text"
        result = chunker.chunk(text)

        assert len(result) == 1
        assert result[0] == text

    def test_chunk_long_text(self):
        """Test chunking text longer than chunk size."""
        chunker = FixedSizeChunker(chunk_size=20, overlap=5)
        text = "A" * 50
        result = chunker.chunk(text)

        assert len(result) > 1
        assert all(len(chunk) <= 20 for chunk in result)

    def test_chunk_with_overlap(self):
        """Test chunking with overlap."""
        chunker = FixedSizeChunker(chunk_size=10, overlap=3)
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = chunker.chunk(text)

        assert len(result) > 1

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=10)
        result = chunker.chunk("")

        assert result == []

    def test_chunk_exact_size(self):
        """Test chunking text exactly chunk size."""
        chunker = FixedSizeChunker(chunk_size=10, overlap=0)
        text = "A" * 10
        result = chunker.chunk(text)

        assert len(result) == 1
        assert result[0] == text

    def test_chunk_no_overlap(self):
        """Test chunking without overlap."""
        chunker = FixedSizeChunker(chunk_size=10, overlap=0)
        text = "A" * 25
        result = chunker.chunk(text)

        assert len(result) == 3


class TestLangChainRecursiveChunker:
    """Test LangChainRecursiveChunker functionality."""

    def test_chunk_basic_text(self):
        """Test chunking basic text."""
        chunker = LangChainRecursiveChunker(chunk_size=100, overlap=10)
        text = "This is a test. This is another sentence."
        result = chunker.chunk(text)

        assert isinstance(result, list)
        assert len(result) >= 1

    def test_chunk_with_paragraphs(self):
        """Test chunking text with paragraphs."""
        chunker = LangChainRecursiveChunker(
            chunk_size=50, overlap=10, separators=["\n\n", "\n", ". "]
        )
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        result = chunker.chunk(text)

        assert isinstance(result, list)
        assert len(result) >= 1

    def test_chunk_long_text(self):
        """Test chunking long text."""
        chunker = LangChainRecursiveChunker(chunk_size=100, overlap=20)
        text = "Word " * 200
        result = chunker.chunk(text)

        assert len(result) > 1
        assert all(isinstance(chunk, str) for chunk in result)

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = LangChainRecursiveChunker(chunk_size=100, overlap=10)
        result = chunker.chunk("")

        assert isinstance(result, list)

    def test_chunk_with_custom_separators(self):
        """Test chunking with custom separators."""
        chunker = LangChainRecursiveChunker(
            chunk_size=50, overlap=5, separators=["\n", ". ", " "]
        )
        text = "Sentence one. Sentence two.\nNew line. Another one."
        result = chunker.chunk(text)

        assert isinstance(result, list)
        assert len(result) >= 1

    def test_chunk_returns_strings(self):
        """Test chunker returns list of strings."""
        chunker = LangChainRecursiveChunker(chunk_size=100, overlap=10)
        text = "Test text for chunking"
        result = chunker.chunk(text)

        assert isinstance(result, list)
        assert all(isinstance(chunk, str) for chunk in result)

    def test_chunk_azerbaijani_text(self):
        """Test chunking Azerbaijani text."""
        chunker = LangChainRecursiveChunker(
            chunk_size=100, overlap=10, separators=["\n\n", "\n", ". ", " "]
        )
        text = "Bakıda hadisə baş verdi. Mərkəzi Bank məlumat verdi."
        result = chunker.chunk(text)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all("ı" in chunk or "ə" in chunk for chunk in result if chunk)
