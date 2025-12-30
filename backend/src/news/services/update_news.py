import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rag_module.services.vectorization_v2 import VectorizationServiceV2
from telegram_fetcher.parsers.__main__ import NewsParsingService
from telegram_fetcher.services import NewsCollectionService

logger = logging.getLogger(__name__)


@dataclass
class NewsUpdateConfig:
    """Configuration for daily news update task."""

    sources: dict[str, str]
    data_dir: Path
    chunk_size: int
    overlap: int
    collection_name: str
    chroma_db_path: str
    database_url: str
    max_concurrent: int
    parser_concurrent: int

    @classmethod
    def from_env(cls) -> "NewsUpdateConfig":
        """Create configuration from environment variables."""
        return cls(
            sources={
                "qafqazinfo": "https://t.me/qafqazinfo",
            },
            data_dir=Path("./datanew"),
            chunk_size=800,
            overlap=150,
            collection_name=os.getenv(
                "CHROMA_COLLECTION_NAME",
                "news_analyzed_2025_800_150_large_v2",
            ),
            chroma_db_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
            database_url=os.getenv("DATABASE_URL", ""),
            max_concurrent=20,
            parser_concurrent=50,
        )


class TelegramNewsFetcher:
    """Service for fetching news from Telegram channels."""

    def __init__(self, config: NewsUpdateConfig):
        self.config = config

    async def fetch(self, stop_date: datetime) -> dict[str, int]:
        """Fetch news from Telegram channels.
        Raises:
                RuntimeError: If no messages were collected from any source.
        """
        service = NewsCollectionService(
            sources=self.config.sources,
            stop_date=stop_date,
            output_dir=str(self.config.data_dir),
        )
        logger.info(f"Fetching news from Telegram until {stop_date}")
        results = await service.collect_all()
        logger.info(f"Telegram fetch complete: {results}")
        total_messages = sum(results.values())
        if total_messages == 0:
            error_msg = (
                f"Telegram fetch failed: No messages collected from any source. "
                f"Results: {results}. Check Telegram authentication."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        return results


class ArticleContentParser:
    """Service for parsing full article content from URLs."""

    def __init__(self, config: NewsUpdateConfig):
        self.config = config

    async def parse(self, site_name: str, input_file: Path) -> dict[str, Any]:
        """Parse full article content."""
        parser_service = NewsParsingService(
            site_name=site_name,
            concurrent_limit=self.config.parser_concurrent,
        )
        logger.info(f"Parsing {site_name} articles from {input_file}")
        stats = await parser_service.parse_json_file(
            input_file=str(input_file),
            output_file=str(input_file),
            overwrite=False,
        )
        logger.info(f"Parsing complete for {site_name}: {stats}")
        return stats


class NewsVectorizer:
    """Service for vectorizing news articles."""

    def __init__(self, config: NewsUpdateConfig):
        self.config = config

    def vectorize(self, source_file: Path, source_name: str) -> dict[str, Any]:
        """Vectorize news articles."""
        logger.info(f"Vectorizing {source_name} from {source_file}")
        service = VectorizationServiceV2.create_default(
            collection_name=self.config.collection_name,
            persist_directory=self.config.chroma_db_path,
            analyzer_mode="async",
            chunk_size=self.config.chunk_size,
            overlap=self.config.overlap,
            max_concurrent=self.config.max_concurrent,
            db_url=self.config.database_url,
            persist_db=True,
        )
        result = service.vectorize(
            source=str(source_file), source_name=source_name
        )
        logger.info(
            f"Vectorization complete: {result.total_documents} docs, "
            f"{result.total_chunks} chunks, "
            f"{result.vectorized_count} vectorized"
        )
        return {
            "total_documents": result.total_documents,
            "total_chunks": result.total_chunks,
            "vectorized_count": result.vectorized_count,
            "skipped_count": result.skipped_count,
        }


class NewsUpdateOrchestrator:
    """Orchestrates daily news update pipeline."""

    def __init__(self, config: NewsUpdateConfig):
        self.config = config
        self.fetcher = TelegramNewsFetcher(config)
        self.parser = ArticleContentParser(config)
        self.vectorizer = NewsVectorizer(config)

    def execute(self, target_date: datetime) -> dict[str, Any]:
        """Execute complete news update pipeline.
        Raises:
                RuntimeError: If any step of the pipeline fails.
        """
        logger.info(f"Starting daily news update for {target_date.date()}")
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info("=== Step 1: Fetching from Telegram ===")
        try:
            fetch_results = asyncio.run(self.fetcher.fetch(target_date))
            logger.info(
                f"✓ Fetch complete: {sum(fetch_results.values())} messages"
            )
        except Exception as e:
            logger.error(f"✗ Fetch failed: {e}", exc_info=True)
            raise RuntimeError(f"Telegram fetch failed: {e}") from e
        logger.info("=== Step 2: Parsing article content ===")
        try:
            parse_results = self._parse_articles()
            total_parsed = sum(
                stats.get("parsed", 0)
                for stats in parse_results.values()
                if isinstance(stats, dict)
            )
            logger.info(f"✓ Parse complete: {total_parsed} articles parsed")
        except Exception as e:
            logger.error(f"✗ Parse failed: {e}", exc_info=True)
            raise RuntimeError(f"Article parsing failed: {e}") from e
        logger.info("=== Step 3: Vectorizing articles ===")
        try:
            vectorize_results = self._vectorize_articles(target_date)
            total_vectorized = sum(
                stats.get("vectorized_count", 0)
                for stats in vectorize_results.values()
                if isinstance(stats, dict)
            )
            logger.info(
                f"✓ Vectorization complete: {total_vectorized} articles vectorized"
            )
        except Exception as e:
            logger.error(f"✗ Vectorization failed: {e}", exc_info=True)
            raise RuntimeError(f"Vectorization failed: {e}") from e
        summary = {
            "date": target_date.isoformat(),
            "fetch_results": fetch_results,
            "parse_results": parse_results,
            "vectorize_results": vectorize_results,
            "status": "success",
        }
        logger.info(f"✓ Daily news update completed successfully: {summary}")
        return summary

    def _parse_articles(self) -> dict[str, Any]:
        """Parse all articles from fetched data."""
        logger.info("=== Step 2: Parsing article content ===")
        results = {}
        for site_name in self.config.sources.keys():
            input_file = self.config.data_dir / f"{site_name}.json"
            if not input_file.exists():
                logger.warning(f"Skipping {site_name}: file not found")
                continue
            stats = asyncio.run(self.parser.parse(site_name, input_file))
            results[site_name] = stats
        return results

    def _vectorize_articles(self, target_date: datetime) -> dict[str, Any]:
        """Vectorize all parsed articles."""
        logger.info("=== Step 3: Vectorizing news ===")
        results = {}
        for site_name in self.config.sources.keys():
            input_file = self.config.data_dir / f"{site_name}.json"
            if not input_file.exists():
                logger.warning(f"Skipping {site_name}: file not found")
                continue
            source_name = f"{site_name}_daily_{target_date.strftime('%Y%m%d')}"
            result = self.vectorizer.vectorize(input_file, source_name)
            results[site_name] = result
        return results
