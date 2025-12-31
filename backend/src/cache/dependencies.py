"""Cache dependencies for FastAPI."""

from functools import lru_cache

from config import get_settings

from rag_module.cache import RedisCache


@lru_cache
def get_redis_cache() -> RedisCache:
    """Get Redis cache instance.

    Returns:
        RedisCache instance configured from settings
    """
    settings = get_settings()
    if settings.redis_url:
        return RedisCache(redis_url=settings.redis_url, prefix="qa")
