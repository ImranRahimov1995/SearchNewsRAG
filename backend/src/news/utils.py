"""Utility functions for news operations."""

from datetime import datetime, timezone


def parse_date(date_str: str | None) -> datetime | None:
    """Parse date string to datetime with timezone.

    Args:
        date_str: Date string in various formats

    Returns:
        Parsed datetime with UTC timezone or None
    """
    if not date_str:
        return None

    try:
        parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (ValueError, AttributeError):
        return None


def sort_by_date(items: list[dict], descending: bool = True) -> list[dict]:
    """Sort items by date field.

    Args:
        items: List of items with date field
        descending: Sort descending (newest first) if True

    Returns:
        Sorted items
    """

    def get_date_key(item: dict) -> datetime:
        doc_date = parse_date(item.get("date"))
        return doc_date if doc_date else datetime.min

    return sorted(items, key=get_date_key, reverse=descending)
