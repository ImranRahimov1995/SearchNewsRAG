"""ChromaDB vector store implementation."""

import logging
from typing import Any

from chromadb import Collection
from chromadb.api import ClientAPI

from .protocols import IEmbedding, VectorDocument, VectorSearchResult

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """ChromaDB implementation of vector store.

    Implements CRUD operations for vector documents using ChromaDB.
    Separates chunk content (vectorized) from full document text (metadata).

    Attributes:
        collection_name: Name of the ChromaDB collection
        embedding: Embedding function implementation
        persist_directory: Directory for persistent storage
    """

    def __init__(
        self,
        collection_name: str,
        embedding: IEmbedding,
        persist_directory: str = "./chroma_db",
        chroma_host: str | None = None,
        chroma_port: int | None = None,
    ):
        """Initialize ChromaDB vector store.

        Args:
            collection_name: Name of the collection
            embedding: Embedding function implementation
            persist_directory: Directory for persistent storage (embedded mode)
            chroma_host: ChromaDB server host (client mode)
            chroma_port: ChromaDB server port (client mode)
        """
        self.collection_name = collection_name
        self.embedding = embedding
        self.persist_directory = persist_directory

        self._client: ClientAPI = self._create_client(
            chroma_host, chroma_port, persist_directory
        )
        self._collection: Collection = self._client.get_or_create_collection(
            name=collection_name
        )

        logger.info(
            f"Initialized ChromaVectorStore: collection={collection_name}"
        )

    def _create_client(
        self,
        host: str | None,
        port: int | None,
        persist_directory: str,
    ) -> ClientAPI:
        """Create ChromaDB client (server or embedded mode).

        Args:
            host: ChromaDB server host (None for embedded mode)
            port: ChromaDB server port (None for embedded mode)
            persist_directory: Directory for persistent storage

        Returns:
            ChromaDB client instance
        """
        if host and port:
            import chromadb

            logger.info(f"Using ChromaDB client mode: {host}:{port}")
            return chromadb.HttpClient(host=host, port=port)

        import chromadb

        logger.info(f"Using ChromaDB embedded mode: {persist_directory}")
        return chromadb.PersistentClient(path=persist_directory)

    def add(self, document: VectorDocument) -> str:
        """Add single document to vector store.

        Args:
            document: Document to add (content will be vectorized)

        Returns:
            Document ID

        Raises:
            ValueError: If document validation fails
        """
        if not document.id:
            raise ValueError("Document ID is required")
        if not document.content:
            raise ValueError("Document content is required")

        embedding_vector = (
            document.vector
            if document.vector
            else self.embedding.embed_text(document.content)
        )

        metadata = {
            k: v for k, v in document.metadata.items() if v is not None
        }

        self._collection.add(
            ids=[document.id],
            documents=[document.content],
            embeddings=[embedding_vector],  # type: ignore[arg-type]
            metadatas=[metadata],  # type: ignore[arg-type]
        )

        logger.debug(f"Added document: {document.id}")
        return document.id

    def add_batch(self, documents: list[VectorDocument]) -> list[str]:
        """Add multiple documents in batch.

        Args:
            documents: List of documents to add

        Returns:
            List of added document IDs

        Raises:
            ValueError: If batch validation fails
        """
        if not documents:
            return []

        for doc in documents:
            if not doc.id or not doc.content:
                raise ValueError(
                    f"Invalid document: id={doc.id}, "
                    f"has_content={bool(doc.content)}"
                )

        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]

        metadatas = [
            {k: v for k, v in doc.metadata.items() if v is not None}
            for doc in documents
        ]

        embeddings = []
        for doc in documents:
            if doc.vector:
                embeddings.append(doc.vector)
            else:
                embeddings = self.embedding.embed_batch(contents)
                break

        self._collection.add(
            ids=ids,
            documents=contents,
            embeddings=embeddings,  # type: ignore[arg-type]
            metadatas=metadatas,  # type: ignore[arg-type]
        )

        logger.info(f"Added batch: {len(documents)} documents")
        return ids

    def get(self, doc_id: str) -> VectorDocument | None:
        """Retrieve document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        try:
            result = self._collection.get(
                ids=[doc_id], include=["documents", "metadatas", "embeddings"]
            )

            if not result["ids"]:
                return None

            docs = result["documents"]
            metas = result["metadatas"]
            embeds = result["embeddings"]

            return VectorDocument(
                id=result["ids"][0],
                content=docs[0] if docs else "",
                metadata=dict(metas[0]) if metas else {},
                vector=list(embeds[0]) if embeds else None,
            )

        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None

    def update(self, document: VectorDocument) -> bool:
        """Update existing document.

        Args:
            document: Document with updated data

        Returns:
            True if updated, False if not found

        Raises:
            ValueError: If document validation fails
        """
        if not document.id:
            raise ValueError("Document ID is required")

        existing = self.get(document.id)
        if not existing:
            logger.warning(f"Document not found for update: {document.id}")
            return False

        embedding_vector = (
            document.vector
            if document.vector
            else self.embedding.embed_text(document.content)
        )

        metadata = {
            k: v for k, v in document.metadata.items() if v is not None
        }

        self._collection.update(
            ids=[document.id],
            documents=[document.content],
            embeddings=[embedding_vector],  # type: ignore[arg-type]
            metadatas=[metadata],  # type: ignore[arg-type]
        )

        logger.debug(f"Updated document: {document.id}")
        return True

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            existing = self.get(doc_id)
            if not existing:
                logger.warning(f"Document not found for deletion: {doc_id}")
                return False

            self._collection.delete(ids=[doc_id])
            logger.debug(f"Deleted document: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

    def delete_batch(self, doc_ids: list[str]) -> int:
        """Delete multiple documents.

        Args:
            doc_ids: List of document identifiers

        Returns:
            Number of documents deleted
        """
        if not doc_ids:
            return 0

        try:
            self._collection.delete(ids=doc_ids)
            logger.info(f"Deleted batch: {len(doc_ids)} documents")
            return len(doc_ids)

        except Exception as e:
            logger.error(f"Error deleting batch: {e}")
            return 0

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
            filters: Optional metadata filters (ChromaDB where clause)

        Returns:
            List of search results ordered by similarity
        """
        query_embedding = self.embedding.embed_text(query)

        where_clause = filters if filters else None

        results = self._collection.query(
            query_embeddings=[query_embedding],  # type: ignore[arg-type]
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        search_results: list[VectorSearchResult] = []
        ids = results["ids"]
        docs = results["documents"]
        metas = results["metadatas"]
        distances = results.get("distances")

        if not ids or not ids[0]:
            return search_results

        for i in range(len(ids[0])):
            doc = VectorDocument(
                id=ids[0][i],
                content=docs[0][i] if docs else "",
                metadata=dict(metas[0][i]) if metas else {},
            )

            distance = distances[0][i] if distances else None
            score = 1.0 - distance if distance is not None else 1.0

            search_results.append(
                VectorSearchResult(
                    document=doc,
                    score=score,
                    distance=distance,
                )
            )

        logger.debug(f"Search query returned {len(search_results)} results")
        return search_results

    def count(self) -> int:
        """Get total number of documents.

        Returns:
            Document count
        """
        try:
            count: int = self._collection.count()
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0

    def clear(self) -> bool:
        """Remove all documents from collection.

        Returns:
            True if successful
        """
        try:
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"Cleared collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

    def get_existing_ids(self) -> set[str]:
        """Get all existing document IDs.

        Returns:
            Set of document IDs currently in store
        """
        try:
            result = self._collection.get(include=[])
            return set(result["ids"])

        except Exception as e:
            logger.error(f"Error getting existing IDs: {e}")
            return set()
