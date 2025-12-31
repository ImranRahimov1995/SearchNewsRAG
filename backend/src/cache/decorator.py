"""Cache decorator for endpoint caching."""

import functools
import logging
from typing import Any, Callable

from rag_module.cache import IQueryCache

logger = logging.getLogger(__name__)


def cached(
    cache: IQueryCache,
    ttl: int = 3600,
    key_prefix: str = "",
) -> Callable:
    """Decorator for caching function results.

    Args:
        cache: Cache implementation
        ttl: Time to live in seconds
        key_prefix: Additional prefix for cache keys

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            query = kwargs.get("query") or (args[0] if args else "")
            if not query:
                logger.warning("No query found for caching, skipping cache")
                return func(*args, **kwargs)

            cache_key_params = {
                "query": str(query),
                "top_k": kwargs.get("top_k", 5),
            }

            cache_key = (
                f"{key_prefix}:{cache.generate_key(**cache_key_params)}"
                if key_prefix
                else cache.generate_key(**cache_key_params)
            )

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for query: {str(query)[:50]}...")
                return cached_result

            logger.info(f"Cache miss for query: {str(query)[:50]}...")
            result = func(*args, **kwargs)

            if result:
                cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator
