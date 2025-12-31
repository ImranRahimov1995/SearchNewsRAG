"""Redis-based query cache implementation."""

import json
import logging
from typing import Any

import redis  # type: ignore[import-untyped]

from .query_cache import QueryCache

logger = logging.getLogger(__name__)


class RedisCache(QueryCache):
    """Redis implementation of query cache."""

    def __init__(
        self,
        redis_url: str | None = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        prefix: str = "qa",
        decode_responses: bool = True,
    ):
        """Initialize Redis cache.

        Args:
            redis_url: Redis connection URL (preferred over host/port)
            host: Redis server host (used if redis_url not provided)
            port: Redis server port
            db: Redis database number
            password: Redis password
            prefix: Cache key prefix
            decode_responses: Decode byte responses to strings
        """
        super().__init__(prefix=prefix)
        if redis_url:
            self.client = redis.from_url(
                redis_url, decode_responses=decode_responses
            )
        else:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
            )
        self._check_connection()

    def _check_connection(self) -> None:
        """Verify Redis connection on initialization."""
        try:
            self.client.ping()
            logger.info(f"Redis cache connected: {self.client}")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached result from Redis.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                if isinstance(value, str):
                    parsed: dict[str, Any] = json.loads(value)
                    return parsed
                return None
            logger.debug(f"Cache miss: {key}")
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        """Store value in Redis cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        except (redis.RedisError, TypeError) as e:
            logger.error(f"Cache set error for key {key}: {e}")

    def delete(self, key: str) -> None:
        """Delete cached value from Redis.

        Args:
            key: Cache key
        """
        try:
            self.client.delete(key)
            logger.debug(f"Cache deleted: {key}")
        except redis.RedisError as e:
            logger.error(f"Cache delete error for key {key}: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Cache exists check error for key {key}: {e}")
            return False

    def clear(self) -> None:
        """Clear all cached values with prefix."""
        try:
            pattern = f"{self.prefix}:*"
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.info(f"Cache cleared: {len(keys)} keys deleted")
        except redis.RedisError as e:
            logger.error(f"Cache clear error: {e}")

    def close(self) -> None:
        """Close Redis connection."""
        try:
            self.client.close()
            logger.info("Redis cache connection closed")
        except redis.RedisError as e:
            logger.error(f"Error closing Redis connection: {e}")
