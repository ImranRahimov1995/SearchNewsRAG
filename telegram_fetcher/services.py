import os
from datetime import datetime
from typing import Dict, Optional

from telegram_fetcher.base import (
    BaseCollectionService,
    IMessageCollector,
    TelegramCollector,
    logger,
)
from telegram_fetcher.config import TelegramFetcherConfig


class NewsCollectionService(BaseCollectionService):
    """Service to collect news from multiple sources."""

    def __init__(
        self,
        sources: Dict[str, str],
        stop_date: datetime,
        collector: Optional[IMessageCollector] = None,
        output_dir: str = ".",
    ):
        if collector is None:
            config = TelegramFetcherConfig.from_env()
            collector = TelegramCollector(str(config.api_id), config.api_hash)

        super().__init__(collector)
        self.sources = sources
        self.stop_date = stop_date
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    async def collect_all(self) -> Dict[str, int]:
        """Collect from all sources."""
        results = {}

        for name, url in self.sources.items():
            logger.info(f"Processing: {name}")
            output_file = os.path.join(self.output_dir, f"{name}.json")

            try:
                count = await self.collector.collect(
                    url, self.stop_date, output_file
                )
                results[name] = count
                self._log_result(name, count)

            except Exception as e:
                logger.error(f"✗ {name} failed: {e}")
                results[name] = 0

            logger.info("-" * 50)

        return results

    async def collect_single(
        self, name: str, url: str, output_file: Optional[str] = None
    ) -> int:
        """Collect from single source."""
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"{name}.json")

        logger.info(f"Processing: {name}")

        try:
            count = await self.collector.collect(
                url, self.stop_date, output_file
            )
            self._log_result(name, count)
            return count

        except Exception as e:
            logger.error(f"✗ {name} failed: {e}")
            return 0
