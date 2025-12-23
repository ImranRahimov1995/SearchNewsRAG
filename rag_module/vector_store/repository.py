"""High-level repository for vector store operations."""

import logging
from typing import Any

from .batch_processor import BatchProcessor
from .chroma_store import ChromaVectorStore
from .protocols import IEmbedding, VectorDocument, VectorSearchResult

logger = logging.getLogger(__name__)


class VectorStoreRepository:
    """High-level repository for vector document operations.

    Provides scalable CRUD operations with batching, deduplication,
    and progress tracking. Coordinates ChromaVectorStore and BatchProcessor.
    """

    def __init__(
        self,
        collection_name: str,
        embedding: IEmbedding,
        persist_directory: str = "chroma_db",
        batch_size: int = 100,
    ):
        """Initialize repository.

        Args:
            collection_name: Name of the vector collection
            embedding: Embedding function implementation
            persist_directory: Directory for persistent storage
            batch_size: Default batch size for operations
        """
        self.store = ChromaVectorStore(
            collection_name=collection_name,
            embedding=embedding,
            persist_directory=persist_directory,
        )
        self.batch_processor = BatchProcessor(batch_size=batch_size)

        logger.info(f"VectorStoreRepository initialized: {collection_name}")

    def add_document(self, document: VectorDocument) -> str:
        """Add single document.

        Args:
            document: Document to add

        Returns:
            Document ID

        Raises:
            ValueError: If document validation fails
        """
        logger.info(f"Adding document: {document.id}")
        return self.store.add(document)

    def add_documents(
        self,
        documents: list[VectorDocument],
        skip_existing: bool = True,
        batch_size: int | None = None,
    ) -> dict[str, Any]:
        """Add multiple documents with deduplication.

        Args:
            documents: Documents to add
            skip_existing: Skip documents that already exist
            batch_size: Override default batch size

        Returns:
            Dictionary with operation statistics

        Raises:
            ValueError: If validation fails
        """
        if not documents:
            return {"added": 0, "skipped": 0, "total": 0}

        logger.info(f"Adding {len(documents)} documents")

        if skip_existing:
            existing_ids = self.store.get_existing_ids()
            new_docs, existing_docs = self.batch_processor.filter_existing(
                documents, existing_ids
            )

            logger.info(
                f"Filtered: {len(new_docs)} new, "
                f"{len(existing_docs)} existing"
            )

            if not new_docs:
                return {
                    "added": 0,
                    "skipped": len(existing_docs),
                    "total": len(documents),
                }

            documents_to_add = new_docs
            skipped_count = len(existing_docs)
        else:
            documents_to_add = documents
            skipped_count = 0

        batches = self.batch_processor.create_batches(
            documents_to_add, batch_size
        )

        added_count = 0
        for batch_num, batch in enumerate(batches, 1):
            try:
                self.batch_processor.validate_batch(batch)
                self.store.add_batch(batch)
                added_count += len(batch)

                logger.info(
                    f"Batch {batch_num}/{len(batches)}: "
                    f"added {len(batch)} documents"
                )

            except Exception as e:
                logger.error(f"Error in batch {batch_num}: {e}")
                raise

        return {
            "added": added_count,
            "skipped": skipped_count,
            "total": len(documents),
            "batches": len(batches),
        }

    def get_document(self, doc_id: str) -> VectorDocument | None:
        """Retrieve document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        return self.store.get(doc_id)

    def update_document(self, document: VectorDocument) -> bool:
        """Update existing document.

        Args:
            document: Document with updated data

        Returns:
            True if updated, False if not found

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Updating document: {document.id}")
        return self.store.update(document)

    def update_documents(
        self, documents: list[VectorDocument], batch_size: int | None = None
    ) -> dict[str, int]:
        """Update multiple documents.

        Args:
            documents: Documents to update
            batch_size: Override default batch size

        Returns:
            Dictionary with operation statistics
        """
        if not documents:
            return {"updated": 0, "not_found": 0, "total": 0}

        logger.info(f"Updating {len(documents)} documents")

        updated_count = 0
        not_found_count = 0

        batches = self.batch_processor.create_batches(documents, batch_size)

        for batch_num, batch in enumerate(batches, 1):
            for doc in batch:
                if self.store.update(doc):
                    updated_count += 1
                else:
                    not_found_count += 1

            logger.info(
                f"Batch {batch_num}/{len(batches)}: "
                f"{updated_count} updated, {not_found_count} not found"
            )

        return {
            "updated": updated_count,
            "not_found": not_found_count,
            "total": len(documents),
        }

    def delete_document(self, doc_id: str) -> bool:
        """Delete document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting document: {doc_id}")
        return self.store.delete(doc_id)

    def delete_documents(self, doc_ids: list[str]) -> int:
        """Delete multiple documents.

        Args:
            doc_ids: List of document identifiers

        Returns:
            Number of documents deleted
        """
        if not doc_ids:
            return 0

        logger.info(f"Deleting {len(doc_ids)} documents")
        return self.store.delete_batch(doc_ids)

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar documents.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of search results ordered by similarity
        """
        logger.debug(f"Searching: query='{query[:50]}...', top_k={top_k}")
        return self.store.search(query, top_k, filters)

    def count(self) -> int:
        """Get total number of documents.

        Returns:
            Document count
        """
        return self.store.count()

    def clear(self) -> bool:
        """Remove all documents.

        Returns:
            True if successful
        """
        logger.warning("Clearing all documents from store")
        return self.store.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get repository statistics.

        Returns:
            Dictionary with statistics
        """
        total_docs = self.count()

        return {
            "collection_name": self.store.collection_name,
            "total_documents": total_docs,
            "persist_directory": self.store.persist_directory,
            "batch_size": self.batch_processor.batch_size,
        }
