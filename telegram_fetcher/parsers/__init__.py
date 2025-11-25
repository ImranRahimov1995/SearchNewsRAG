from typing import Callable, Dict

from telegram_fetcher.parsers.base import SiteProcessor
from telegram_fetcher.parsers.qafqazinfo import create_qafqazinfo_processor

# Registry mapping site names to factory functions
SITE_PROCESSORS: Dict[str, Callable[[], SiteProcessor]] = {
    "qafqazinfo": create_qafqazinfo_processor,
}


def get_processor(site_name: str) -> SiteProcessor:
    """Get processor for specific site."""
    factory = SITE_PROCESSORS.get(site_name)
    if not factory:
        raise ValueError(
            f"No processor registered for '{site_name}'. "
            f"Available: {list(SITE_PROCESSORS.keys())}"
        )
    return factory()


def list_available_sites() -> list:
    """List all available site processors."""
    return list(SITE_PROCESSORS.keys())
