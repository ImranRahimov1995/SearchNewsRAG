"""Tests for telegram_fetcher/services.py"""

import os
from unittest.mock import patch

import pytest

from telegram_fetcher.services import NewsCollectionService


class TestNewsCollectionService:
    """Tests for NewsCollectionService."""

    def test_init_with_collector(
        self, sources, stop_date, mock_collector, tmp_path
    ):
        """Test initialization with provided collector."""
        service = NewsCollectionService(
            sources=sources,
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        assert service.sources == sources
        assert service.stop_date == stop_date
        assert service.collector == mock_collector
        assert service.output_dir == str(tmp_path)
        assert os.path.exists(tmp_path)

    def test_init_without_collector_raises_error(
        self, sources, stop_date, tmp_path
    ):
        """Test initialization without collector and no API credentials."""
        with patch.dict(
            os.environ, {"API_ID": "", "API_HASH": ""}, clear=True
        ):
            with pytest.raises(
                ValueError, match="API_ID environment variable"
            ):
                NewsCollectionService(
                    sources=sources,
                    stop_date=stop_date,
                    output_dir=str(tmp_path),
                )

    def test_init_creates_output_directory(
        self, sources, stop_date, mock_collector, tmp_path
    ):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "new_dir"
        assert not output_dir.exists()

        service = NewsCollectionService(
            sources=sources,
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(output_dir),
        )

        assert output_dir.exists()
        assert service.output_dir == str(output_dir)

    @pytest.mark.asyncio
    async def test_collect_all_success(
        self, sources, stop_date, mock_collector, tmp_path
    ):
        """Test collecting from all sources successfully."""
        service = NewsCollectionService(
            sources=sources,
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        mock_collector.collect.return_value = 15

        results = await service.collect_all()

        assert results == {"operativ": 15, "qafqazinfo": 15}
        assert mock_collector.collect.call_count == 2

        calls = mock_collector.collect.call_args_list
        assert calls[0][0][0] == "https://t.me/operativ_news"
        assert calls[0][0][1] == stop_date
        assert calls[1][0][0] == "https://t.me/qafqazinfo"
        assert calls[1][0][1] == stop_date

    @pytest.mark.asyncio
    async def test_collect_all_with_failure(
        self, sources, stop_date, mock_collector, tmp_path
    ):
        """Test collecting when one source fails."""
        service = NewsCollectionService(
            sources=sources,
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        mock_collector.collect.side_effect = [20, Exception("Network error")]

        results = await service.collect_all()

        assert results == {"operativ": 20, "qafqazinfo": 0}
        assert mock_collector.collect.call_count == 2

    @pytest.mark.asyncio
    async def test_collect_all_creates_output_files(
        self, sources, stop_date, mock_collector, tmp_path
    ):
        """Test that output files are passed correctly."""
        service = NewsCollectionService(
            sources=sources,
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        await service.collect_all()

        calls = mock_collector.collect.call_args_list
        assert calls[0][0][2] == str(tmp_path / "operativ.json")
        assert calls[1][0][2] == str(tmp_path / "qafqazinfo.json")

    @pytest.mark.asyncio
    async def test_collect_single_success(
        self, stop_date, mock_collector, tmp_path
    ):
        """Test collecting from a single source."""
        service = NewsCollectionService(
            sources={},
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        mock_collector.collect.return_value = 25

        count = await service.collect_single(
            "test_source", "https://t.me/test_channel"
        )

        assert count == 25
        mock_collector.collect.assert_called_once()

        call_args = mock_collector.collect.call_args[0]
        assert call_args[0] == "https://t.me/test_channel"
        assert call_args[1] == stop_date
        assert call_args[2] == str(tmp_path / "test_source.json")

    @pytest.mark.asyncio
    async def test_collect_single_with_custom_output(
        self, stop_date, mock_collector, tmp_path
    ):
        """Test collecting with custom output file."""
        service = NewsCollectionService(
            sources={},
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        mock_collector.collect.return_value = 30
        custom_output = str(tmp_path / "custom_output.json")

        count = await service.collect_single(
            "test_source",
            "https://t.me/test_channel",
            output_file=custom_output,
        )

        assert count == 30
        call_args = mock_collector.collect.call_args[0]
        assert call_args[2] == custom_output

    @pytest.mark.asyncio
    async def test_collect_single_failure(
        self, stop_date, mock_collector, tmp_path
    ):
        """Test handling failure in single collection."""
        service = NewsCollectionService(
            sources={},
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        mock_collector.collect.side_effect = Exception("Connection timeout")

        count = await service.collect_single(
            "test_source", "https://t.me/test_channel"
        )

        assert count == 0
        mock_collector.collect.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_all_returns_zero_on_exception(
        self, sources, stop_date, mock_collector, tmp_path
    ):
        """Test that collect_all handles exceptions gracefully."""
        service = NewsCollectionService(
            sources=sources,
            stop_date=stop_date,
            collector=mock_collector,
            output_dir=str(tmp_path),
        )

        mock_collector.collect.side_effect = Exception("Test error")

        results = await service.collect_all()

        assert results == {"operativ": 0, "qafqazinfo": 0}
        assert mock_collector.collect.call_count == 2
