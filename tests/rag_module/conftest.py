"""Pytest fixtures for rag_module tests."""

import pytest


@pytest.fixture
def sample_markdown_text():
    """Sample text with markdown formatting."""
    return "**Breaking News**: Visit [link](https://example.com) for `code`"


@pytest.fixture
def sample_emoji_text():
    """Sample text with emojis."""
    return "Amazing news! 🔥 Check this out 🎉 Great stuff 😊"


@pytest.fixture
def sample_whitespace_text():
    """Sample text with irregular whitespace."""
    return "Text   with\n\nirregular    spacing\tand\ttabs"


@pytest.fixture
def sample_mixed_case_text():
    """Sample text with mixed case and punctuation."""
    return "BREAKING NEWS!!! Visit site—now... Really???"


@pytest.fixture
def sample_azerbaijani_date():
    """Sample ISO datetime for testing."""
    return "2024-11-27T14:30:00+04:00"


@pytest.fixture
def sample_context(sample_azerbaijani_date):
    """Sample context dictionary."""
    return {
        "date": sample_azerbaijani_date,
        "source": "qafqazinfo",
        "metadata": {"category": "politics"},
    }


@pytest.fixture
def long_text_sample():
    """Long text sample for pipeline testing."""
    return """
    **Breaking News from Azerbaijan**

    Visit our [website](https://example.com) for more details.

    This is an important announcement! 🔥 Please read carefully.

    Contact us at:
    - Email: `info@example.com`
    - Phone: +994 12 345 67 89

    > Important quote here

    Thank you for your attention!!! 😊
    """
