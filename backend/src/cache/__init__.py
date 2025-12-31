"""Cache package for backend."""

from .decorator import cached
from .dependencies import get_redis_cache

__all__ = ["cached", "get_redis_cache"]
