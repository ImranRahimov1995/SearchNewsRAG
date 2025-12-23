"""Batch processing utilities for vector operations."""

import logging
from typing import Any, Callable

from .protocols import VectorDocument

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process documents in batches for scalable operations.

    Handles batching logic for embedding generation and vector storage
    to avoid memory issues and API rate limits.
    """

    def __init__(
        self,
        batch_size: int = 100,
        max_embedding_batch: int = 2048,
        max_chroma_batch: int = 5000,
    ):
        """Initialize batch processor.

        Args:
            batch_size: Default batch size for processing
            max_embedding_batch: Maximum batch size for embedding API
            max_chroma_batch: Maximum batch size for ChromaDB operations
        """
        self.batch_size = batch_size
        self.max_embedding_batch = max_embedding_batch
        self.max_chroma_batch = max_chroma_batch

        logger.info(
            f"BatchProcessor initialized: batch_size={batch_size}, "
            f"max_embedding={max_embedding_batch}, "
            f"max_chroma={max_chroma_batch}"
        )

    def create_batches(
        self, items: list[Any], batch_size: int | None = None
    ) -> list[list[Any]]:
        """Split items into batches.

        Args:
            items: List of items to batch
            batch_size: Override default batch size

        Returns:
            List of batches
        """
        if not items:
            return []

        size = batch_size or self.batch_size
        batches = []

        for i in range(0, len(items), size):
            batches.append(items[i : i + size])

        logger.debug(
            f"Created {len(batches)} batches from {len(items)} items "
            f"(batch_size={size})"
        )
        return batches

    def process_in_batches(
        self,
        items: list[Any],
        processor: Callable[[list[Any]], Any],
        batch_size: int | None = None,
        on_batch_complete: Callable[[int, int], None] | None = None,
    ) -> list[Any]:
        """Process items in batches with progress callback.

        Args:
            items: Items to process
            processor: Function to process each batch
            batch_size: Override default batch size
            on_batch_complete: Callback(batch_num, total_batches)

        Returns:
            List of processing results
        """
        batches = self.create_batches(items, batch_size)
        results = []

        for batch_num, batch in enumerate(batches, 1):
            try:
                batch_result = processor(batch)
                results.append(batch_result)

                if on_batch_complete:
                    on_batch_complete(batch_num, len(batches))

                logger.debug(
                    f"Processed batch {batch_num}/{len(batches)}: "
                    f"{len(batch)} items"
                )

            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                raise

        return results

    def filter_existing(
        self,
        documents: list[VectorDocument],
        existing_ids: set[str],
    ) -> tuple[list[VectorDocument], list[VectorDocument]]:
        """Filter documents into new and existing.

        Args:
            documents: Documents to filter
            existing_ids: Set of existing document IDs

        Returns:
            Tuple of (new_documents, existing_documents)
        """
        new_docs = []
        existing_docs = []

        for doc in documents:
            if doc.id in existing_ids:
                existing_docs.append(doc)
            else:
                new_docs.append(doc)

        logger.info(
            f"Filtered documents: {len(new_docs)} new, "
            f"{len(existing_docs)} existing"
        )

        return new_docs, existing_docs

    def validate_batch(self, documents: list[VectorDocument]) -> bool:
        """Validate batch of documents.

        Args:
            documents: Documents to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        if not documents:
            raise ValueError("Empty document batch")

        for i, doc in enumerate(documents):
            if not doc.id:
                raise ValueError(f"Document {i} missing ID")
            if not doc.content:
                raise ValueError(f"Document {i} ({doc.id}) missing content")

        logger.debug(f"Validated batch of {len(documents)} documents")
        return True

    def estimate_batches(
        self, total_items: int, batch_size: int | None = None
    ) -> dict[str, int]:
        """Estimate batch processing metrics.

        Args:
            total_items: Total number of items
            batch_size: Override default batch size

        Returns:
            Dictionary with estimation metrics
        """
        size = batch_size or self.batch_size
        num_batches = (total_items + size - 1) // size

        return {
            "total_items": total_items,
            "batch_size": size,
            "num_batches": num_batches,
            "last_batch_size": total_items % size or size,
        }
