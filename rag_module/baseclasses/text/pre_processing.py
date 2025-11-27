"""Text Processing Module for RAG Vectorization.

This module provides a comprehensive text processing pipeline specifically
designed for preparing Azerbaijani news content for vector embeddings and
RAG (Retrieval-Augmented Generation) systems.

Key Components:
    - BaseTextProcessor: Abstract base for simple text transformations
    - BaseContextProcessor: Abstract base for context-aware transformations
    - TextProcessingPipeline: Sequential processing for basic transformations
    - ContextAwareProcessingPipeline: Advanced pipeline with metadata support
    - Ready-to-use instances: default_telegram_news_processor, etc.

"""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Protocol

from settings import get_logger

logger = get_logger("text_processors")


class ITextProcessor(Protocol):
    """Protocol for basic text processors.

    Defines the interface for processors that transform text without
    requiring additional context or metadata. All basic processors must
    implement the process() method with this exact signature.

    This protocol enables compile-time type checking and ensures
    consistency across all text processors in the pipeline.
    """

    def process(self, text: str) -> str:
        """Transform input text according to processor's rules.

        Args:
            text: Raw input text to be processed

        Returns:
            Transformed text after applying processor's logic
        """
        ...


class IContextProcessor(Protocol):
    """Protocol for context-aware text processors.

    Defines the interface for processors that require additional metadata
    or context (such as dates, sources, or custom parameters) to perform
    their transformations. Context is passed as a dictionary to allow
    flexible, extensible metadata handling.

    This separation from ITextProcessor follows the Interface Segregation
    Principle, ensuring clients only depend on methods they actually use.
    """

    def process(self, text: str, context: dict) -> str:
        """Transform text using provided contextual information.

        Args:
            text: Raw input text to be processed
            context: Dictionary containing metadata (e.g., 'date', 'source')

        Returns:
            Transformed text incorporating context information
        """
        ...


class BaseTextProcessor(ABC):
    """Abstract base class for simple text processors."""

    def __init__(self):
        """Initialize processor with logger instance."""
        self.logger = logger

    def validate_input(self, text: str) -> bool:
        """Validate input text before processing.

        Ensures text is not None, is a string, and contains non-whitespace
        content. This prevents processing errors and provides consistent
        validation across all processors.

        Args:
            text: Input text to validate

        Returns:
            True if text is valid, False otherwise
        """
        return (
            text is not None and isinstance(text, str) and bool(text.strip())
        )

    @abstractmethod
    def process(self, text: str) -> str:
        """Process text according to specific transformation rules.

        Must be implemented by all subclasses. Should include input
        validation using validate_input() method.

        Args:
            text: Input text to transform

        Returns:
            Transformed text
        """
        pass


class BaseContextProcessor(ABC):
    """Abstract base class for context-aware text processors.

    Extends the base processor concept to handle transformations that
    require additional metadata or context information. Follows the same
    template method pattern as BaseTextProcessor but with context support.

    Context is passed as a dictionary to allow flexible metadata handling:
        - {'date': '2024-11-27T10:00:00Z'}
        - {'source': 'qafqazinfo', 'category': 'politics'}
        - {'metadata': {...}, 'tags': [...]}
    """

    def __init__(self):
        """Initialize context processor with logger instance."""
        self.logger = logger

    def validate_input(self, text: str) -> bool:
        """Validate input text before processing.

        Ensures text is not None, is a string, and contains non-whitespace
        content. Identical to BaseTextProcessor validation for consistency.

        Args:
            text: Input text to validate

        Returns:
            True if text is valid, False otherwise
        """
        return (
            text is not None and isinstance(text, str) and bool(text.strip())
        )

    @abstractmethod
    def process(self, text: str, context: dict) -> str:
        """Process text with additional contextual information.

        Must be implemented by all subclasses. Should validate both text
        input and context data before processing.

        Args:
            text: Input text to transform
            context: Dictionary with metadata (e.g., date, source, tags)

        Returns:
            Transformed text incorporating context information
        """
        pass


class MarkdownCleaner(BaseTextProcessor):
    """Remove Markdown formatting from text.

    Converts Markdown-formatted text to plain text by removing all markup
    elements while preserving the actual content. Essential for processing
    Telegram messages and web content that use Markdown formatting.

    Removed elements:
        - Bold: **text** → text
        - Italic: *text*, _text_ → text
        - Links: [label](url) → label
        - Headers: # Header → Header
        - Code blocks: ```code``` → (removed)
        - Inline code: `code` → code
        - Blockquotes: > quote → quote

    This ensures clean text for vector embeddings without formatting noise.
    """

    def process(self, text: str) -> str:
        """Remove all Markdown formatting from text.

        Applies multiple regex patterns to strip various Markdown elements
        while preserving the actual text content. Patterns are applied in
        specific order to handle nested formatting correctly.

        Args:
            text: Markdown-formatted text

        Returns:
            Plain text without Markdown formatting, empty string if invalid
        """
        if not self.validate_input(text):
            return ""

        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

        self.logger.debug(f"Markdown cleaned: '{text[:50]}...'")

        return text


class WhitespaceNormalizer(BaseTextProcessor):
    r"""Normalize and standardize whitespace in text.

    Cleans up irregular spacing, line breaks, and other whitespace
    irregularities to create consistent, single-space separated text.
    Critical for vector embeddings where whitespace variations would
    create unnecessary noise.

    Transformations:
        - Multiple spaces → single space
        - Line breaks (\n, \r) → space
        - Leading/trailing whitespace → removed
        - Tabs and special whitespace → single space

    This ensures consistent token boundaries for embedding models.
    """

    def process(self, text: str) -> str:
        """Normalize all whitespace to single spaces.

        Collapses multiple consecutive whitespace characters into single
        spaces, removes line breaks, and trims leading/trailing whitespace.

        Args:
            text: Text with irregular whitespace

        Returns:
            Text with normalized spacing, empty string if invalid
        """
        if not self.validate_input(text):
            return ""

        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ").replace("\r", " ")
        text = text.strip()

        self.logger.debug(f"Whitespace normalized: '{text[:50]}...'")

        return text


class EmojiRemover(BaseTextProcessor):
    """Remove emojis and special Unicode symbols from text.

    Strips all emoji characters and special symbols from text to create
    clean, text-only content suitable for embedding. While emojis can
    carry meaning, they often create noise in vector representations and
    may not be well-handled by embedding models.

    Removed characters:
        - Emoticons (😀-🙏)
        - Symbols & Pictographs (🌀-🗿)
        - Transport symbols (🚀-🛿)
        - Flag emojis (🇦-🇿)
        - Supplemental symbols (🤀-🧿)
        - Other special Unicode characters

    Preserves standard punctuation and alphanumeric characters.

    """

    def process(self, text: str) -> str:
        """Remove all emojis and special Unicode symbols.

        Uses comprehensive Unicode range patterns to detect and remove
        emoji characters. Also removes other special symbols while
        preserving basic punctuation and alphanumeric characters.

        Args:
            text: Text containing emojis and special symbols

        Returns:
            Clean text without emojis, empty string if invalid
        """
        if not self.validate_input(text):
            return ""

        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"
            "\U0001f300-\U0001f5ff"
            "\U0001f680-\U0001f6ff"
            "\U0001f1e0-\U0001f1ff"
            "\U0001f900-\U0001f9ff"
            "\U00002600-\U000027bf"
            "\U000024c2-\U0001f251"
            "\U0001f170-\U0001f251"
            "]+",
            flags=re.UNICODE,
        )

        text = emoji_pattern.sub(r"", text)

        text = re.sub(r"[^\w\s.,!?;:()\-\"\']+", "", text, flags=re.UNICODE)

        text = re.sub(r"\s+", " ", text).strip()

        self.logger.debug(f"Emojis removed: '{text[:50]}...'")

        return text


class TextStandardizer(BaseTextProcessor):
    """Standardize text formatting, casing, and punctuation.

    Normalizes text to a consistent format suitable for vector embeddings
    by converting to lowercase and standardizing punctuation. This reduces
    vocabulary size and ensures semantically similar texts have similar
    representations regardless of formatting variations.

    Transformations:
        - Case: ALL CAPS, Title Case → lowercase
        - Punctuation: Multiple ... → single .
        - Dashes: – — → standard -
        - Quotes: " " ' ' → " '
        - Repeated marks: !!! ??? → ! ?

    This creates consistent input for embedding models, improving semantic
    matching and reducing token diversity.

    """

    def process(self, text: str) -> str:
        """Standardize text format and punctuation.

        Converts to lowercase, normalizes punctuation marks, and
        standardizes special characters like quotes and dashes.

        Args:
            text: Text with varied formatting

        Returns:
            Standardized lowercase text, empty string if invalid
        """
        if not self.validate_input(text):
            return ""

        text = text.lower()

        text = re.sub(r"[.]{2,}", ".", text)
        text = re.sub(r"[!]{2,}", "!", text)
        text = re.sub(r"[?]{2,}", "?", text)

        text = text.replace("–", "-").replace("—", "-")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2018", "'").replace("\u2019", "'")

        text = re.sub(r"\s+", " ", text).strip()

        self.logger.debug(f"Text standardized: '{text[:50]}...'")

        return text


class AzerbaijaniDateTimeProcessor(BaseContextProcessor):
    """Add Azerbaijani date and time context to text.

    Enhances text with temporal context in Azerbaijani language, providing
    both machine-readable timestamps and human-readable date information.
    This improves semantic understanding by giving the embedding model
    explicit temporal grounding.

    Context requirements:
        - context['date']: ISO format datetime string
          (e.g., '2024-11-27T10:30:00+00:00')

    Output format:
        "YYYY-MM-DD HH:MM, day_name_az, month_name_az. [original text]"

    Example:
        "2024-11-27 10:30, çərşənbə, noyabr. Breaking news text"

    """

    AZERBAIJANI_DAYS = {
        "Monday": "Bazar ertəsi",
        "Tuesday": "Çərşənbə axşamı",
        "Wednesday": "Çərşənbə",
        "Thursday": "Cümə axşamı",
        "Friday": "Cümə",
        "Saturday": "Şənbə",
        "Sunday": "Bazar",
    }

    AZERBAIJANI_MONTHS = {
        "January": "Yanvar",
        "February": "Fevral",
        "March": "Mart",
        "April": "Aprel",
        "May": "May",
        "June": "İyun",
        "July": "İyul",
        "August": "Avqust",
        "September": "Sentyabr",
        "October": "Oktyabr",
        "November": "Noyabr",
        "December": "Dekabr",
    }

    def process(self, text: str, context: dict) -> str:
        """Add Azerbaijani datetime context to text.

        Parses ISO datetime from context, converts to Azerbaijani day and
        month names, and prepends formatted timestamp to text. Handles
        timezone conversion and provides graceful fallback on errors.

        Args:
            text: Original text content
            context: Dictionary with 'date' key (ISO format string)

        Returns:
            Text with Azerbaijani datetime prefix, original text on error
        """
        if not self.validate_input(text):
            return ""

        date_str = context.get("date", "")
        if not date_str:
            self.logger.warning("No date in context")
            return text

        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            date_formatted = dt.strftime("%Y-%m-%d")
            time_formatted = dt.strftime("%H:%M")

            day_name_az = self.AZERBAIJANI_DAYS.get(
                dt.strftime("%A"), dt.strftime("%A")
            )
            month_name_az = self.AZERBAIJANI_MONTHS.get(
                dt.strftime("%B"), dt.strftime("%B")
            )

            datetime_context = (
                f"{date_formatted} {time_formatted}, "
                f"{day_name_az.lower()}, {month_name_az.lower()}. "
            )

            enhanced_text = datetime_context + text

            self.logger.debug(f"Added datetime context: '{datetime_context}'")

            return enhanced_text

        except (ValueError, AttributeError) as e:
            self.logger.error(f"Error parsing date '{date_str}': {e}")
            return text


class TextProcessingPipeline:
    """Sequential processing pipeline for basic text transformations.

    Orchestrates multiple text processors in a defined sequence, passing
    the output of each processor as input to the next. Implements the
    Chain of Responsibility pattern for modular, extensible text processing.

    Pipeline Architecture:
        Input Text → Processor 1 → Processor 2 → ... → Processor N → Output

    Features:
        - Sequential execution order guaranteed
        - Early termination if any processor returns empty string
        - Comprehensive logging at each step
        - Type-safe through ITextProcessor protocol
        - Easily extendable with new processors

    Use cases:
        - Cleaning Telegram messages
        - Preprocessing web-scraped content
        - Standardizing user-generated content
        - Preparing text for embedding models

    """

    def __init__(self, processors: List[ITextProcessor]):
        """Initialize pipeline with ordered list of processors.

        Args:
            processors: List of text processors to apply in sequence.
                       Each must implement ITextProcessor protocol.
        """
        self.processors = processors
        self.logger = logger

    def process(self, text: str) -> str:
        """Process text through all processors sequentially.

        Executes each processor in order, passing the output of one as
        input to the next. If any processor returns an empty string,
        that result is propagated through remaining processors.

        Args:
            text: Raw input text to process

        Returns:
            Fully processed text after all transformations

        """
        for processor in self.processors:
            text = processor.process(text)

        self.logger.debug(f"Pipeline processed text: '{text[:50]}...'")

        return text


class ContextAwareProcessingPipeline:
    """Advanced pipeline supporting both basic and context-aware processors.

    Extends the basic pipeline concept to handle processors that require
    additional metadata or context. Executes in two phases:

    Phase 1 - Basic Processing:
        Applies all basic transformations (cleaning, normalization) that
        don't require context. These run first to clean the raw input.

    Phase 2 - Context Processing:
        Applies context-aware transformations (date stamping, source
        tagging) that enrich the cleaned text with metadata.

    This two-phase approach ensures clean text before adding context,
    preventing context information from being corrupted by cleaning steps.

    Pipeline Architecture:
        Input Text
          ↓
        Basic Processor 1 → 2 → ... → N (cleaning)
          ↓
        Context Processor 1 → 2 → ... → M (enrichment)
          ↓
        Output Text

    Features:
        - Separation of concerns (cleaning vs. enrichment)
        - Optional context - basic processing always runs

    Use cases:
        - Processing timestamped news articles
        - Adding source attribution to scraped content

    """

    def __init__(
        self,
        basic_processors: List[ITextProcessor],
        context_processors: List[IContextProcessor],
    ):
        """Initialize two-phase processing pipeline.

        Args:
            basic_processors: List of basic text processors (no context)
            context_processors: List of context-aware processors
        """
        self.basic_processors = basic_processors
        self.context_processors = context_processors
        self.logger = logger

    def process(self, text: str, context: dict | None = None) -> str:
        """Process text through basic and context-aware processors.

        Executes basic processors first to clean text, then applies
        context processors if context is provided. This ensures clean
        text before enrichment with metadata.

        Args:
            text: Raw input text to process
            context: Optional dictionary with metadata for context
                    processors (e.g., {'date': '...', 'source': '...'})

        Returns:
            Fully processed and enriched text

        """
        for processor in self.basic_processors:
            text = processor.process(text)

        if context:
            for ctx_processor in self.context_processors:
                text = ctx_processor.process(text, context)

        self.logger.debug(f"Context pipeline processed: '{text[:50]}...'")

        return text


default_telegram_news_processor = TextProcessingPipeline(
    processors=[
        MarkdownCleaner(),
        WhitespaceNormalizer(),
        EmojiRemover(),
        TextStandardizer(),
    ],
)

azerbaijani_news_processor = ContextAwareProcessingPipeline(
    basic_processors=[
        MarkdownCleaner(),
        WhitespaceNormalizer(),
        EmojiRemover(),
        TextStandardizer(),
    ],
    context_processors=[
        AzerbaijaniDateTimeProcessor(),
    ],
)
