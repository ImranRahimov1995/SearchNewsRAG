"""Telegram news collector CLI.

Collects messages from Telegram channels and saves to JSON.
"""

import argparse
import asyncio
from datetime import datetime, timezone
from typing import Optional

from settings import SOURCES
from telegram_fetcher.base import logger
from telegram_fetcher.services import NewsCollectionService


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect news from Telegram channels"
    )

    parser.add_argument(
        "--stop-date",
        type=str,
        default="2020-01-01",
        help="Stop collecting at this date (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Collect from specific source only",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory for JSON files",
    )

    return parser.parse_args()


def parse_stop_date(date_string: str) -> datetime:
    """Parse stop date from string format YYYY-MM-DD."""
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError as e:
        logger.error(f"Invalid date format: {date_string}")
        logger.error("Expected format: YYYY-MM-DD (e.g., 2020-01-01)")
        raise SystemExit(1) from e


def get_sources(source_name: Optional[str] = None) -> dict:
    """Get sources to collect from."""
    if source_name:
        if source_name not in SOURCES:
            logger.error(
                f"Unknown source: {source_name}. "
                f"Available: {list(SOURCES.keys())}"
            )
            raise SystemExit(1)
        return {source_name: SOURCES[source_name]}
    return SOURCES


async def main():
    """Main execution function."""
    args = parse_arguments()

    # Parse stop date
    stop_date = parse_stop_date(args.stop_date)
    logger.info(f"Stop date set to: {stop_date.date()}")

    # Get sources
    sources = get_sources(args.source)
    logger.info(f"Collecting from: {list(sources.keys())}")

    # Create service
    service = NewsCollectionService(
        sources=sources, stop_date=stop_date, output_dir=args.output_dir
    )

    # Collect messages
    logger.info("Starting collection...")
    results = await service.collect_all()

    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 50)

    total = 0
    for name, count in results.items():
        status = "✓" if count > 0 else "✗"
        logger.info(f"{status} {name}: {count} messages")
        total += count

    logger.info("=" * 50)
    logger.info(f"Total collected: {total} messages")
    logger.info("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nCollection interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise SystemExit(1)
