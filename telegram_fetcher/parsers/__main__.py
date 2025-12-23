"""CLI for news detail parsing.

Fetches article content from URLs in JSON files.
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from telegram_fetcher.parsers import get_processor
from telegram_fetcher.parsers.base import BaseContentParser, NewsItem

logger = logging.getLogger(__name__)


class NewsParsingService:
    """Service for parsing news details from JSON files."""

    def __init__(self, site_name: str, concurrent_limit: int = 50):
        self.site_name = site_name
        self.processor = get_processor(site_name)
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        self.stats = {
            "total": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }

    async def _process_with_semaphore(self, item: NewsItem) -> NewsItem:
        """Process item with semaphore to limit concurrency."""
        async with self.semaphore:
            return await self.processor.process_item(item)

    async def parse_json_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        overwrite: bool = False,
    ) -> Dict[str, int]:
        """Parse news items from JSON file."""
        if output_file is None:
            output_file = input_file

        logger.info(f"Loading data from {input_file}")

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            return self.stats
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {input_file}: {e}")
            return self.stats

        items = []
        for idx, item_data in enumerate(data):
            items.append(
                NewsItem(
                    id=item_data.get("id", idx),
                    date=item_data.get("date", ""),
                    text=item_data.get("text", ""),
                    url=item_data.get("url"),
                    detail=item_data.get("detail"),
                    image_url=item_data.get("image_url"),
                )
            )

        self.stats["total"] = len(items)

        items_to_process = []
        for item in items:
            if item.detail and not overwrite:
                if not item.detail.startswith(
                    ("Error", "Failed", "No URL", "Content not found")
                ):
                    self.stats["skipped"] += 1
                    continue

            items_to_process.append(item)

        logger.info(
            f"Found {len(items_to_process)} items to process "
            f"out of {len(items)} total"
        )

        if not items_to_process:
            logger.info("No items need processing")
            return self.stats

        processed_items = await self._process_items(items_to_process)

        processed_dict = {item.id: item for item in processed_items}
        for item in items:
            if item.id in processed_dict:
                item.url = processed_dict[item.id].url
                item.detail = processed_dict[item.id].detail
                item.image_url = processed_dict[item.id].image_url

        await self._save_results(items, output_file)

        # Close fetcher if it has a close method
        parser = self.processor.content_parser
        if isinstance(parser, BaseContentParser) and hasattr(
            parser, "fetcher"
        ):
            if hasattr(parser.fetcher, "close"):
                await parser.fetcher.close()

        return self.stats

    async def _process_items(self, items: List[NewsItem]) -> List[NewsItem]:
        """Process multiple items concurrently."""
        logger.info(
            f"Processing {len(items)} items with "
            f"{self.semaphore._value} concurrent requests"
        )

        tasks = [self._process_with_semaphore(item) for item in items]

        results = []

        for i, task in enumerate(asyncio.as_completed(tasks), 1):
            try:
                result = await task

                self.stats["processed"] += 1

                if result.detail and not result.detail.startswith(
                    ("Error", "Failed", "No URL", "Content not found")
                ):
                    self.stats["success"] += 1
                else:
                    self.stats["failed"] += 1

                results.append(result)

                if i % 100 == 0 or i == len(tasks):
                    progress = (i / len(tasks)) * 100
                    logger.info(
                        f"Progress: {i}/{len(tasks)} ({progress:.1f}%) - "
                        f"Success: {self.stats['success']}, "
                        f"Failed: {self.stats['failed']}"
                    )

            except Exception as e:
                logger.error(f"Error processing item: {e}")
                self.stats["failed"] += 1

        logger.info(
            f"Completed! Total: {self.stats['total']}, "
            f"Processed: {self.stats['processed']}, "
            f"Success: {self.stats['success']}, "
            f"Failed: {self.stats['failed']}, "
            f"Skipped: {self.stats['skipped']}"
        )

        return results

    async def _save_results(
        self, items: List[NewsItem], output_file: str
    ) -> None:
        """Save results to JSON file."""
        result_data = [
            {
                "id": item.id,
                "date": item.date,
                "text": item.text,
                "url": item.url,
                "detail": item.detail,
                "image_url": item.image_url,
            }
            for item in items
        ]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ Saved {len(items)} items to {output_file}")
        except Exception as e:
            logger.error(f"✗ Error saving to {output_file}: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Parse news article details from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            # Parse QafqazInfo news
            python -m telegram_fetcher.parsers --site qafqazinfo \\
                --input datanew/qafqazinfo.json

            # Parse and save to different file
            python -m telegram_fetcher.parsers --site qafqazinfo \\
                --input datanew/qafqazinfo.json \\
                --output datanew/qafqazinfo_parsed.json

            # Overwrite existing details
            python -m telegram_fetcher.parsers --site qafqazinfo \\
                --input datanew/qafqazinfo.json \\
                --overwrite

            # Use more concurrent requests
            python -m telegram_fetcher.parsers --site qafqazinfo \\
                --input datanew/qafqazinfo.json \\
                --concurrent 100
        """,
    )

    parser.add_argument(
        "--site",
        type=str,
        required=True,
        choices=["qafqazinfo"],
        help="News site to parse (qafqazinfo, etc.)",
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input JSON file path (e.g., datanew/qafqazinfo.json)",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path (default: same as input)",
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=50,
        help="Number of concurrent requests (default: 50)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing details (default: skip items with details)",
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        logger.error(f"Input file does not exist: {args.input}")
        return 1

    try:
        logger.info(f"Starting news detail parsing for {args.site}")
        logger.info(f"Input: {args.input}")
        logger.info(f"Output: {args.output or args.input}")
        logger.info(f"Concurrent requests: {args.concurrent}")
        logger.info(f"Overwrite existing: {args.overwrite}")
        logger.info("-" * 60)

        service = NewsParsingService(
            site_name=args.site, concurrent_limit=args.concurrent
        )

        stats = asyncio.run(
            service.parse_json_file(
                input_file=args.input,
                output_file=args.output,
                overwrite=args.overwrite,
            )
        )

        logger.info("-" * 60)
        logger.info("SUMMARY:")
        logger.info(f"  Total items: {stats['total']}")
        logger.info(f"  Processed: {stats['processed']}")
        logger.info(f"  Success: {stats['success']}")
        logger.info(f"  Failed: {stats['failed']}")
        logger.info(f"  Skipped: {stats['skipped']}")
        logger.info("-" * 60)

        return 0

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
