"""Abstract query cache implementation."""

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any


class QueryCache(ABC):
    """Abstract base class for query caching.

    Provides common functionality for generating cache keys
    and enforcing cache interface.
    """

    def __init__(self, prefix: str = "qa"):
        """Initialize query cache.

        Args:
            prefix: Cache key prefix for namespacing
        """
        self.prefix = prefix

    def generate_key(self, query: str, **kwargs: Any) -> str:
        """Generate unique cache key from query and parameters.

        Args:
            query: User query text
            **kwargs: Additional parameters affecting the result

        Returns:
            Unique cache key
        """
        data = {"query": query.lower().strip(), **kwargs}
        serialized = json.dumps(data, sort_keys=True)
        hash_value = hashlib.sha256(serialized.encode()).hexdigest()[:16]
        return f"{self.prefix}:{hash_value}"

    @abstractmethod
    def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached result by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    @abstractmethod
    def set(self, key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        """Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete cached value.

        Args:
            key: Cache key
        """
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        ...
