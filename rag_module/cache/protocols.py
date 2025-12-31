"""Cache protocols and interfaces."""

from typing import Any, Protocol


class IQueryCache(Protocol):
    """Interface for query caching operations."""

    def generate_key(self, **kwargs: Any) -> str:
        """Generate unique cache key from parameters.

        Args:
            **kwargs: Parameters affecting the result

        Returns:
            Unique cache key
        """
        ...

    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached result by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    def set(self, key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        """Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        ...

    def delete(self, key: str) -> None:
        """Delete cached value.

        Args:
            key: Cache key
        """
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...
