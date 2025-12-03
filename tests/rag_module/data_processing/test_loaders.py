"""Tests for data loaders."""

import json

import pytest

from rag_module.data_processing.loaders import (
    JSONFileLoader,
    TelegramJSONLoader,
)


class TestJSONFileLoader:
    """Test JSONFileLoader functionality."""

    def test_load_list_from_file(self, tmp_path):
        """Test loading JSON list from file."""
        test_data = [
            {"id": 1, "text": "First item"},
            {"id": 2, "text": "Second item"},
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = JSONFileLoader()
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["text"] == "Second item"

    def test_load_single_object_from_file(self, tmp_path):
        """Test loading single JSON object converts to list."""
        test_data = {"id": 1, "text": "Single item"}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = JSONFileLoader()
        result = loader.load(str(file_path))

        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["text"] == "Single item"

    def test_load_file_not_found(self):
        """Test loading non-existent file raises error."""
        loader = JSONFileLoader()

        with pytest.raises(FileNotFoundError, match="File not found"):
            loader.load("nonexistent.json")

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises error."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json", encoding="utf-8")

        loader = JSONFileLoader()

        with pytest.raises(json.JSONDecodeError):
            loader.load(str(file_path))

    def test_load_empty_list(self, tmp_path):
        """Test loading empty JSON list."""
        file_path = tmp_path / "empty.json"
        file_path.write_text("[]", encoding="utf-8")

        loader = JSONFileLoader()
        result = loader.load(str(file_path))

        assert result == []


class TestTelegramJSONLoader:
    """Test TelegramJSONLoader functionality."""

    def test_load_valid_telegram_data_with_text(self, tmp_path):
        """Test loading valid Telegram data with text field."""
        test_data = [
            {"id": 1, "text": "Message with text", "date": "2025-11-28"},
            {"id": 2, "text": "Another message", "date": "2025-11-27"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["text"] == "Message with text"

    def test_load_valid_telegram_data_with_detail(self, tmp_path):
        """Test loading valid Telegram data with detail field."""
        test_data = [
            {"id": 1, "detail": "Detailed content", "date": "2025-11-28"},
            {"id": 2, "detail": "More details", "date": "2025-11-27"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["detail"] == "Detailed content"

    def test_load_data_with_both_text_and_detail(self, tmp_path):
        """Test loading data with both text and detail fields."""
        test_data = [
            {
                "id": 1,
                "text": "Short text",
                "detail": "Full detail",
                "date": "2025-11-28",
            }
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 1
        assert result[0]["text"] == "Short text"
        assert result[0]["detail"] == "Full detail"

    def test_skip_items_without_text_or_detail(self, tmp_path):
        """Test skipping items missing both text and detail fields."""
        test_data = [
            {"id": 1, "text": "Valid message"},
            {"id": 2, "date": "2025-11-28"},
            {"id": 3, "detail": "Another valid"},
            {"id": 4},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3

    def test_load_all_items_invalid(self, tmp_path):
        """Test loading when all items are invalid."""
        test_data = [
            {"id": 1, "date": "2025-11-28"},
            {"id": 2, "url": "http://example.com"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 0

    def test_load_empty_text_field(self, tmp_path):
        """Test handling empty text field."""
        test_data = [
            {"id": 1, "text": "", "detail": "Has detail"},
            {"id": 2, "text": "   ", "detail": "Also has detail"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 2

    def test_slicing_with_start_index(self, tmp_path):
        """Test data slicing with start index."""
        test_data = [
            {"id": 1, "text": "First"},
            {"id": 2, "text": "Second"},
            {"id": 3, "text": "Third"},
            {"id": 4, "text": "Fourth"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader(start_index=2)
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["id"] == 3
        assert result[1]["id"] == 4

    def test_slicing_with_end_index(self, tmp_path):
        """Test data slicing with end index."""
        test_data = [
            {"id": 1, "text": "First"},
            {"id": 2, "text": "Second"},
            {"id": 3, "text": "Third"},
            {"id": 4, "text": "Fourth"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader(end_index=2)
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_slicing_with_start_and_end_index(self, tmp_path):
        """Test data slicing with both start and end indices."""
        test_data = [
            {"id": 1, "text": "First"},
            {"id": 2, "text": "Second"},
            {"id": 3, "text": "Third"},
            {"id": 4, "text": "Fourth"},
            {"id": 5, "text": "Fifth"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader(start_index=1, end_index=4)
        result = loader.load(str(file_path))

        assert len(result) == 3
        assert result[0]["id"] == 2
        assert result[1]["id"] == 3
        assert result[2]["id"] == 4

    def test_slicing_without_indices(self, tmp_path):
        """Test loading without slicing returns all valid items."""
        test_data = [
            {"id": 1, "text": "First"},
            {"id": 2, "text": "Second"},
            {"id": 3, "text": "Third"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader()
        result = loader.load(str(file_path))

        assert len(result) == 3
        assert result[0]["id"] == 1
        assert result[2]["id"] == 3

    def test_slicing_with_invalid_items(self, tmp_path):
        """Test slicing filters invalid items after slice."""
        test_data = [
            {"id": 1, "text": "First"},
            {"id": 2},  # Invalid - will be skipped
            {"id": 3, "text": "Third"},
            {"id": 4, "detail": "Fourth"},
            {"id": 5},  # Invalid - will be skipped
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader(start_index=1, end_index=5)
        result = loader.load(str(file_path))

        assert len(result) == 2
        assert result[0]["id"] == 3
        assert result[1]["id"] == 4

    def test_slicing_out_of_bounds(self, tmp_path):
        """Test slicing with out of bounds indices."""
        test_data = [
            {"id": 1, "text": "First"},
            {"id": 2, "text": "Second"},
        ]
        file_path = tmp_path / "telegram.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        loader = TelegramJSONLoader(start_index=5, end_index=10)
        result = loader.load(str(file_path))

        assert len(result) == 0
