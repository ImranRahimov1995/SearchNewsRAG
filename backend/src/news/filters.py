"""Date filtering utilities for news."""

from datetime import datetime, timedelta, timezone

from .schemas import DateFilter


def calculate_date_threshold(date_filter: DateFilter) -> datetime | None:
    """Calculate date threshold based on filter.

    Args:
        date_filter: Date filter option

    Returns:
        Datetime threshold or None for ALL filter
    """
    if date_filter == DateFilter.ALL:
        return None

    now = datetime.now(timezone.utc)
    thresholds = {
        DateFilter.TODAY: now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ),
        DateFilter.WEEK: now - timedelta(days=7),
        DateFilter.MONTH: now - timedelta(days=30),
    }
    return thresholds.get(date_filter)


def build_chroma_date_filter(date_filter: DateFilter) -> dict | None:
    """Build ChromaDB where filter for date range.

    Args:
        date_filter: Date filter option

    Returns:
        ChromaDB filter dict or None for ALL
    """
    threshold = calculate_date_threshold(date_filter)
    if threshold is None:
        return None

    timestamp = int(threshold.timestamp())
    return {"date": {"$gte": timestamp}}
