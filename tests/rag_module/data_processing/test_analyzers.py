"""Tests for text analyzers."""

from rag_module.data_processing.analyzers import DummyAnalyzer


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

        assert len(result) == 3
        assert "length" in result
        assert "word_count" in result
        assert "llm_analysis_exists" in result
        assert result["llm_analysis_exists"] is False
        assert "source" not in result
        assert "extra" not in result
