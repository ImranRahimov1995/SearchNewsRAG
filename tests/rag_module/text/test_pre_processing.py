"""
Comprehensive tests for processing module.
"""

from rag_module.text.pre_processing import (
    AzerbaijaniDateTimeProcessor,
    ContextAwareProcessingPipeline,
    EmojiRemover,
    MarkdownCleaner,
    TextProcessingPipeline,
    TextStandardizer,
    WhitespaceNormalizer,
    azerbaijani_news_processor,
    default_telegram_news_processor,
)


class TestMarkdownCleaner:
    """Tests for MarkdownCleaner processor."""

    def test_remove_bold(self):
        """Test removing bold markdown."""
        cleaner = MarkdownCleaner()
        text = "**Bold text** and more **bold**"
        result = cleaner.process(text)

        assert "**" not in result
        assert "Bold text" in result
        assert "bold" in result

    def test_remove_italic(self):
        """Test removing italic markdown (both * and _)."""
        cleaner = MarkdownCleaner()
        text = "*Italic* and _also italic_"
        result = cleaner.process(text)

        assert result == "Italic and also italic"

    def test_remove_links(self):
        """Test removing markdown links."""
        cleaner = MarkdownCleaner()
        text = "Visit [our site](https://example.com) for info"
        result = cleaner.process(text)

        assert "[" not in result
        assert "]" not in result
        assert "https://example.com" not in result
        assert "our site" in result

    def test_remove_headers(self):
        """Test removing markdown headers."""
        cleaner = MarkdownCleaner()
        text = "# Header 1\n## Header 2\n### Header 3"
        result = cleaner.process(text)

        assert "#" not in result
        assert "Header 1" in result
        assert "Header 2" in result

    def test_remove_code_blocks(self):
        """Test removing code blocks."""
        cleaner = MarkdownCleaner()
        text = "Text before ```code block``` text after"
        result = cleaner.process(text)

        assert "```" not in result
        assert "code block" not in result
        assert "Text before" in result
        assert "text after" in result

    def test_remove_inline_code(self):
        """Test removing inline code."""
        cleaner = MarkdownCleaner()
        text = "Use `command` to execute"
        result = cleaner.process(text)

        assert "`" not in result
        assert "command" in result

    def test_remove_blockquotes(self):
        """Test removing blockquote markers."""
        cleaner = MarkdownCleaner()
        text = "> Important quote\n> Second line"
        result = cleaner.process(text)

        assert ">" not in result
        assert "Important quote" in result

    def test_complex_markdown(self, sample_markdown_text):
        """Test cleaning complex markdown with multiple elements."""
        cleaner = MarkdownCleaner()
        result = cleaner.process(sample_markdown_text)

        assert "**" not in result
        assert "[" not in result
        assert "`" not in result
        assert "Breaking News" in result
        assert "link" in result
        assert "code" in result

    def test_empty_string(self):
        """Test handling empty string."""
        cleaner = MarkdownCleaner()
        assert cleaner.process("") == ""

    def test_none_input(self):
        """Test handling None input."""
        cleaner = MarkdownCleaner()
        assert cleaner.process(None) == ""

    def test_whitespace_only(self):
        """Test handling whitespace-only input."""
        cleaner = MarkdownCleaner()
        assert cleaner.process("   \n\t  ") == ""


class TestWhitespaceNormalizer:
    """Tests for WhitespaceNormalizer processor."""

    def test_normalize_multiple_spaces(self):
        """Test normalizing multiple consecutive spaces."""
        normalizer = WhitespaceNormalizer()
        text = "Text    with     many   spaces"
        result = normalizer.process(text)

        assert result == "Text with many spaces"

    def test_normalize_line_breaks(self):
        """Test normalizing line breaks."""
        normalizer = WhitespaceNormalizer()
        text = "Line1\nLine2\n\nLine3\rLine4"
        result = normalizer.process(text)

        assert "\n" not in result
        assert "\r" not in result
        assert "Line1 Line2 Line3 Line4" == result

    def test_normalize_tabs(self):
        """Test normalizing tabs."""
        normalizer = WhitespaceNormalizer()
        text = "Text\twith\ttabs"
        result = normalizer.process(text)

        assert "\t" not in result
        assert result == "Text with tabs"

    def test_strip_whitespace(self):
        """Test stripping leading/trailing whitespace."""
        normalizer = WhitespaceNormalizer()
        text = "   Text with spaces   "
        result = normalizer.process(text)

        assert result == "Text with spaces"

    def test_complex_whitespace(self, sample_whitespace_text):
        """Test normalizing complex whitespace patterns."""
        normalizer = WhitespaceNormalizer()
        result = normalizer.process(sample_whitespace_text)

        assert "  " not in result
        assert "\n" not in result
        assert "\t" not in result
        assert "Text with irregular spacing and tabs" == result

    def test_empty_string(self):
        """Test handling empty string."""
        normalizer = WhitespaceNormalizer()
        assert normalizer.process("") == ""

    def test_whitespace_only(self):
        """Test handling whitespace-only string."""
        normalizer = WhitespaceNormalizer()
        assert normalizer.process("   \n\t  ") == ""


class TestEmojiRemover:
    """Tests for EmojiRemover processor."""

    def test_remove_common_emojis(self):
        """Test removing common emojis."""
        remover = EmojiRemover()
        text = "Happy 😊 Sad 😢 Fire 🔥"
        result = remover.process(text)

        assert "😊" not in result
        assert "😢" not in result
        assert "🔥" not in result
        assert "Happy" in result
        assert "Sad" in result
        assert "Fire" in result

    def test_remove_multiple_emojis(self, sample_emoji_text):
        """Test removing multiple different emojis."""
        remover = EmojiRemover()
        result = remover.process(sample_emoji_text)

        assert "🔥" not in result
        assert "🎉" not in result
        assert "😊" not in result
        assert "Amazing news" in result
        assert "Check this out" in result

    def test_remove_flag_emojis(self):
        """Test removing flag emojis."""
        remover = EmojiRemover()
        text = "Azerbaijan 🇦🇿 Turkey 🇹🇷"
        result = remover.process(text)

        assert "🇦🇿" not in result
        assert "🇹🇷" not in result
        assert "Azerbaijan" in result

    def test_preserve_punctuation(self):
        """Test that basic punctuation is preserved."""
        remover = EmojiRemover()
        text = "Hello! How are you? Great."
        result = remover.process(text)

        assert "!" in result
        assert "?" in result
        assert "." in result

    def test_remove_special_symbols(self):
        """Test removing special Unicode symbols."""
        remover = EmojiRemover()
        text = "Text © with ® symbols ™"
        result = remover.process(text)

        assert "©" not in result
        assert "®" not in result
        assert "™" not in result

    def test_empty_string(self):
        """Test handling empty string."""
        remover = EmojiRemover()
        assert remover.process("") == ""


class TestTextStandardizer:
    """Tests for TextStandardizer processor."""

    def test_lowercase_conversion(self):
        """Test converting text to lowercase."""
        standardizer = TextStandardizer()
        text = "UPPERCASE and MiXeD CaSe"
        result = standardizer.process(text)

        assert result == "uppercase and mixed case"

    def test_normalize_multiple_dots(self):
        """Test normalizing multiple dots."""
        standardizer = TextStandardizer()
        text = "Text with dots..."
        result = standardizer.process(text)

        assert "..." not in result
        assert result == "text with dots."

    def test_normalize_multiple_exclamation(self):
        """Test normalizing multiple exclamation marks."""
        standardizer = TextStandardizer()
        text = "Amazing!!!"
        result = standardizer.process(text)

        assert "!!!" not in result
        assert result == "amazing!"

    def test_normalize_multiple_question(self):
        """Test normalizing multiple question marks."""
        standardizer = TextStandardizer()
        text = "Really???"
        result = standardizer.process(text)

        assert "???" not in result
        assert result == "really?"

    def test_normalize_dashes(self):
        """Test normalizing different dash types."""
        standardizer = TextStandardizer()
        text = "Range 1–10 or 10—20"
        result = standardizer.process(text)

        assert "–" not in result
        assert "—" not in result
        assert "range 1-10 or 10-20" == result

    def test_normalize_quotes(self):
        """Test normalizing different quote types."""
        standardizer = TextStandardizer()
        text = "\u201cQuoted\u201d and \u2018single\u2019"
        result = standardizer.process(text)

        expected = "\"quoted\" and 'single'"
        assert expected == result
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result

    def test_complex_standardization(self, sample_mixed_case_text):
        """Test complex standardization with multiple elements."""
        standardizer = TextStandardizer()
        result = standardizer.process(sample_mixed_case_text)

        assert result == "breaking news! visit site-now. really?"

    def test_empty_string(self):
        """Test handling empty string."""
        standardizer = TextStandardizer()
        assert standardizer.process("") == ""


class TestAzerbaijaniDateTimeProcessor:
    """Tests for AzerbaijaniDateTimeProcessor."""

    def test_add_datetime_context(self, sample_azerbaijani_date):
        """Test adding Azerbaijani datetime context."""
        processor = AzerbaijaniDateTimeProcessor()
        text = "Breaking news"
        context = {"date": sample_azerbaijani_date}

        result = processor.process(text, context)

        assert "2024-11-27" in result
        assert "14:30" in result
        assert "çərşənbə" in result
        assert "noyabr" in result
        assert "Breaking news" in result

    def test_monday_translation(self):
        """Test Monday translation to Azerbaijani."""
        processor = AzerbaijaniDateTimeProcessor()
        text = "News"
        context = {"date": "2024-11-25T10:00:00Z"}

        result = processor.process(text, context)

        assert "bazar ertəsi" in result

    def test_january_translation(self):
        """Test January translation to Azerbaijani."""
        processor = AzerbaijaniDateTimeProcessor()
        text = "News"
        context = {"date": "2024-01-15T10:00:00Z"}

        result = processor.process(text, context)

        assert "yanvar" in result

    def test_missing_date_in_context(self):
        """Test handling missing date in context."""
        processor = AzerbaijaniDateTimeProcessor()
        text = "News without date"
        context = {}

        result = processor.process(text, context)

        assert result == "News without date"

    def test_invalid_date_format(self):
        """Test handling invalid date format."""
        processor = AzerbaijaniDateTimeProcessor()
        text = "News"
        context = {"date": "invalid-date"}

        result = processor.process(text, context)

        assert result == "News"

    def test_timezone_handling(self):
        """Test correct timezone handling."""
        processor = AzerbaijaniDateTimeProcessor()
        text = "News"
        context = {"date": "2024-11-27T10:00:00Z"}

        result = processor.process(text, context)

        assert "10:00" in result

    def test_empty_text_with_context(self):
        """Test handling empty text with valid context."""
        processor = AzerbaijaniDateTimeProcessor()
        context = {"date": "2024-11-27T10:00:00Z"}

        result = processor.process("", context)

        assert result == ""


class TestTextProcessingPipeline:
    """Tests for TextProcessingPipeline."""

    def test_sequential_processing(self):
        """Test that processors execute in order."""
        pipeline = TextProcessingPipeline(
            processors=[
                MarkdownCleaner(),
                WhitespaceNormalizer(),
                EmojiRemover(),
                TextStandardizer(),
            ]
        )

        text = "**BOLD** text  with\nemoji 🔥"
        result = pipeline.process(text)

        assert "**" not in result
        assert "🔥" not in result
        assert result == "bold text with emoji"

    def test_empty_pipeline(self):
        """Test pipeline with no processors."""
        pipeline = TextProcessingPipeline(processors=[])
        text = "Unchanged text"
        result = pipeline.process(text)

        assert result == "Unchanged text"

    def test_single_processor(self):
        """Test pipeline with single processor."""
        pipeline = TextProcessingPipeline(processors=[MarkdownCleaner()])
        text = "**Bold** text"
        result = pipeline.process(text)

        assert result == "Bold text"

    def test_default_telegram_processor(self, long_text_sample):
        """Test default Telegram processor with complex input."""
        result = default_telegram_news_processor.process(long_text_sample)

        assert "**" not in result
        assert "🔥" not in result
        assert "😊" not in result
        assert "[" not in result
        assert "`" not in result
        assert "breaking news from azerbaijan" in result


class TestContextAwareProcessingPipeline:
    """Tests for ContextAwareProcessingPipeline."""

    def test_basic_and_context_processing(self, sample_context):
        """Test pipeline with both basic and context processors."""
        pipeline = ContextAwareProcessingPipeline(
            basic_processors=[
                MarkdownCleaner(),
                WhitespaceNormalizer(),
                TextStandardizer(),
            ],
            context_processors=[AzerbaijaniDateTimeProcessor()],
        )

        text = "**BREAKING** news"
        result = pipeline.process(text, context=sample_context)

        assert "**" not in result
        assert "2024-11-27" in result
        assert "çərşənbə" in result
        assert "breaking news" in result

    def test_without_context(self):
        """Test pipeline without providing context."""
        pipeline = ContextAwareProcessingPipeline(
            basic_processors=[MarkdownCleaner(), TextStandardizer()],
            context_processors=[AzerbaijaniDateTimeProcessor()],
        )

        text = "**Bold** text"
        result = pipeline.process(text, context=None)

        assert result == "bold text"

    def test_azerbaijani_news_processor(
        self, long_text_sample, sample_azerbaijani_date
    ):
        """Test full Azerbaijani news processor."""
        context = {"date": sample_azerbaijani_date}
        result = azerbaijani_news_processor.process(
            long_text_sample, context=context
        )

        assert "2024-11-27" in result
        assert "14:30" in result
        assert "çərşənbə" in result
        assert "noyabr" in result
        assert "breaking news from azerbaijan" in result
        assert "**" not in result
        assert "🔥" not in result

    def test_empty_basic_processors(self, sample_context):
        """Test pipeline with no basic processors."""
        pipeline = ContextAwareProcessingPipeline(
            basic_processors=[],
            context_processors=[AzerbaijaniDateTimeProcessor()],
        )

        text = "News text"
        result = pipeline.process(text, context=sample_context)

        assert "2024-11-27" in result
        assert "News text" in result

    def test_empty_context_processors(self):
        """Test pipeline with no context processors."""
        pipeline = ContextAwareProcessingPipeline(
            basic_processors=[TextStandardizer()],
            context_processors=[],
        )

        text = "UPPERCASE"
        result = pipeline.process(text, context={"date": "2024-11-27"})

        assert result == "uppercase"


class TestIntegrationScenarios:
    """Integration tests with real-world scenarios."""

    def test_telegram_message_processing(self):
        """Test processing typical Telegram message."""
        fire_emoji = "\U0001f525"
        text = f"{fire_emoji} **Breaking News!** Visit [source](https://example.com) #news"

        result = default_telegram_news_processor.process(text)

        assert "**" not in result
        assert "[" not in result
        assert "#" not in result
        assert "breaking news" in result

    def test_news_article_with_date(self):
        """Test processing news article with date context."""
        text = "**IMPORTANT ANNOUNCEMENT!!!** New economic reforms unveiled"

        context = {"date": "2024-11-27T15:30:00+04:00"}
        result = azerbaijani_news_processor.process(text, context)

        assert "2024-11-27 15:30" in result
        assert "çərşənbə, noyabr" in result
        assert "important announcement!" in result

    def test_mixed_content_processing(self):
        """Test processing mixed content types."""
        emoji = "\U0001f60a"
        text = f"**Bold** *italic* `code` link: [text](url) {emoji}"
        result = default_telegram_news_processor.process(text)

        assert result == "bold italic code link: text"

    def test_azerbaijani_text_preservation(self):
        """Test that Azerbaijani text is preserved correctly."""
        text = "Azərbaycan xəbərləri"
        result = default_telegram_news_processor.process(text)

        assert "azərbaycan xəbərləri" == result

    def test_unicode_handling(self):
        """Test proper Unicode character handling."""
        text = "Привет мир 你好世界 مرحبا"
        result = default_telegram_news_processor.process(text)

        assert "привет мир" in result


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_long_text(self):
        """Test processing very long text."""
        text = "word " * 10000
        result = default_telegram_news_processor.process(text)

        assert len(result) > 0
        assert result.startswith("word")

    def test_special_characters_only(self):
        """Test text with only special characters."""
        text = "***###@@@"
        result = default_telegram_news_processor.process(text)

        assert len(result) >= 0

    def test_mixed_line_endings(self):
        """Test handling mixed line endings."""
        text = "Line1\nLine2\rLine3\r\nLine4"
        normalizer = WhitespaceNormalizer()
        result = normalizer.process(text)

        assert "\n" not in result
        assert "\r" not in result

    def test_nested_markdown(self):
        """Test nested markdown structures."""
        text = "**Bold with *italic* inside**"
        cleaner = MarkdownCleaner()
        result = cleaner.process(text)

        assert "**" not in result
        assert "*" not in result

    def test_malformed_markdown(self):
        """Test handling malformed markdown."""
        text = "**Unclosed bold and [incomplete link"
        cleaner = MarkdownCleaner()
        result = cleaner.process(text)

        assert len(result) > 0
