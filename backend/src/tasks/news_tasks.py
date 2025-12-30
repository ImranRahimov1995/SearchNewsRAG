"""Daily news update task for automatic data collection and vectorization."""

import logging
from datetime import datetime, timedelta
from typing import Any

import pytz
from src.news.services import NewsUpdateConfig, NewsUpdateOrchestrator
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.news_tasks.daily_news_update",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def daily_news_update(self: Any) -> dict[str, Any]:
    """Daily task to fetch, parse, and vectorize news from Telegram channels.

    Runs at 00:01 Baku time daily.
    Fetches news from yesterday, parses full content, and vectorizes.
    """
    try:
        baku_tz = pytz.timezone("Asia/Baku")
        now_baku = datetime.now(baku_tz)
        yesterday = now_baku.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=1)

        config = NewsUpdateConfig.from_env()
        orchestrator = NewsUpdateOrchestrator(config)
        summary = orchestrator.execute(yesterday)

        logger.info(f"Daily news update completed successfully: {summary}")
        return summary

    except Exception as exc:
        logger.error(f"Daily news update failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)
