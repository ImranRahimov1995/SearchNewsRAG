"""Tests for text analyzers."""

from rag_module.baseclasses.data_processing.analyzers import (
    DummyAnalyzer,
    NewsClassifier,
)


class TestDummyAnalyzer:
    """Test DummyAnalyzer functionality."""

    def test_analyze_basic_text(self):
        """Test analyzing basic text statistics."""
        analyzer = DummyAnalyzer()
        text = "This is a test message with several words"
        context = {"source": "test", "date": "2025-11-28"}

        result = analyzer.analyze(text, context)

        assert "length" in result
        assert "word_count" in result
        assert result["length"] == len(text)
        assert result["word_count"] == 8

    def test_analyze_empty_text(self):
        """Test analyzing empty text."""
        analyzer = DummyAnalyzer()
        text = ""
        context = {}

        result = analyzer.analyze(text, context)

        assert result["length"] == 0
        assert result["word_count"] == 0

    def test_analyze_single_word(self):
        """Test analyzing single word."""
        analyzer = DummyAnalyzer()
        text = "word"
        context = {}

        result = analyzer.analyze(text, context)

        assert result["length"] == 4
        assert result["word_count"] == 1

    def test_analyze_multiline_text(self):
        """Test analyzing multiline text."""
        analyzer = DummyAnalyzer()
        text = "Line one\nLine two\nLine three"
        context = {}

        result = analyzer.analyze(text, context)

        assert result["word_count"] == 6
        assert result["length"] == len(text)

    def test_analyze_returns_only_stats(self):
        """Test analyzer returns only length and word_count."""
        analyzer = DummyAnalyzer()
        text = "Test text"
        context = {"source": "test", "extra": "data"}

        result = analyzer.analyze(text, context)

        assert len(result) == 2
        assert "length" in result
        assert "word_count" in result
        assert "source" not in result
        assert "extra" not in result


class TestNewsClassifier:
    """Test NewsClassifier functionality."""

    def test_classifier_without_llm(self):
        """Test classifier without LLM returns base stats."""
        classifier = NewsClassifier(llm_client=None)
        text = "Test news article"
        context = {"source": "test"}

        result = classifier.analyze(text, context)

        assert "length" in result
        assert "word_count" in result
        assert result["importance"] is None
        assert result["category"] is None
        assert result["tags"] is None

    def test_classifier_with_llm_mock(self):
        """Test classifier with LLM client (mock)."""

        class MockLLM:
            pass

        classifier = NewsClassifier(llm_client=MockLLM())
        text = "Important political news"
        context = {}

        result = classifier.analyze(text, context)

        assert "length" in result
        assert "word_count" in result
        assert "category" in result
        assert "importance" in result
        assert "tags" in result
        assert "confidence" in result

    def test_classifier_base_metadata_included(self):
        """Test classifier includes base metadata."""
        classifier = NewsClassifier(llm_client=None)
        text = "A" * 100
        context = {}

        result = classifier.analyze(text, context)

        assert result["length"] == 100
        assert result["word_count"] == 1

    def test_classifier_initialization_without_llm(self):
        """Test classifier can be initialized without LLM."""
        classifier = NewsClassifier()

        assert classifier.llm is None
        assert classifier.fallback is not None

    def test_classifier_initialization_with_llm(self):
        """Test classifier can be initialized with LLM."""

        class MockLLM:
            pass

        llm = MockLLM()
        classifier = NewsClassifier(llm_client=llm)

        assert classifier.llm is llm

    def test_classifier_empty_text(self):
        """Test classifier with empty text."""
        classifier = NewsClassifier(llm_client=None)
        text = ""
        context = {}

        result = classifier.analyze(text, context)

        assert result["length"] == 0
        assert result["word_count"] == 0
        assert result["importance"] is None
