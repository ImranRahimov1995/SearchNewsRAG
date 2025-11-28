"""Tests for text cleaners."""

from rag_module.baseclasses.data_processing.cleaners import (
    AzerbaijaniNewsCleaner,
    TelegramNewsCleaner,
)


class TestTelegramNewsCleaner:
    """Test TelegramNewsCleaner functionality."""

    def test_clean_markdown(self):
        """Test removing markdown formatting."""
        cleaner = TelegramNewsCleaner()
        text = "**Bold** and *italic* text with [link](http://example.com)"
        result = cleaner.clean(text)

        assert "**" not in result
        assert "*" not in result
        assert "[" not in result
        assert "bold" in result
        assert "italic" in result

    def test_clean_emojis(self):
        """Test removing emojis."""
        cleaner = TelegramNewsCleaner()
        text = "Hello 😊 World 🌍"
        result = cleaner.clean(text)

        assert "😊" not in result
        assert "🌍" not in result
        assert "hello" in result
        assert "world" in result

    def test_clean_whitespace(self):
        """Test normalizing whitespace."""
        cleaner = TelegramNewsCleaner()
        text = "Multiple    spaces\n\n\nand    lines"
        result = cleaner.clean(text)

        assert "    " not in result
        assert "\n\n\n" not in result

    def test_clean_empty_text(self):
        """Test cleaning empty text."""
        cleaner = TelegramNewsCleaner()
        result = cleaner.clean("")

        assert result == ""

    def test_clean_whitespace_only(self):
        """Test cleaning whitespace-only text."""
        cleaner = TelegramNewsCleaner()
        result = cleaner.clean("   \n\n   ")

        assert result == ""

    def test_clean_complex_message(self):
        """Test cleaning complex Telegram message."""
        cleaner = TelegramNewsCleaner()
        text = """
        **Breaking News!** 🔥

        Check this [article](http://example.com)

        Multiple    spaces   here
        """
        result = cleaner.clean(text)

        assert "**" not in result
        assert "🔥" not in result
        assert "[article]" not in result
        assert "breaking news" in result


class TestAzerbaijaniNewsCleaner:
    """Test AzerbaijaniNewsCleaner functionality."""

    def test_clean_basic_text(self):
        """Test basic text cleaning."""
        cleaner = AzerbaijaniNewsCleaner()
        text = "**Xəbər**: Bakıda hadisə baş verdi"
        result = cleaner.clean(text)

        assert "**" not in result
        assert "xəbər" in result
        assert "bakıda" in result

    def test_clean_azerbaijani_characters(self):
        """Test preserving Azerbaijani characters."""
        cleaner = AzerbaijaniNewsCleaner()
        text = "Mərkəzi Bank əməkdaşları görüş keçirdilər"
        result = cleaner.clean(text)

        assert "ə" in result
        assert "ı" in result
        assert "ü" in result

    def test_clean_with_date_context(self):
        """Test cleaning doesn't affect date context handling."""
        cleaner = AzerbaijaniNewsCleaner()
        text = "Dünən hadisə baş verdi"
        result = cleaner.clean(text)

        assert "dünən" in result

    def test_clean_empty_text(self):
        """Test cleaning empty text."""
        cleaner = AzerbaijaniNewsCleaner()
        result = cleaner.clean("")

        assert result == ""

    def test_clean_markdown_and_emojis(self):
        """Test removing markdown and emojis from Azerbaijani text."""
        cleaner = AzerbaijaniNewsCleaner()
        text = "**Təcili xəbər** 🚨: Bakıda əhəmiyyətli hadisə"
        result = cleaner.clean(text)

        assert "**" not in result
        assert "🚨" not in result
        assert "təcili" in result
        assert "bakıda" in result
