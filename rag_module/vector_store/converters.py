"""Converters for transforming data processing documents to vector documents."""

from rag_module.data_processing.protocols import Document
from settings import get_logger

from .protocols import VectorDocument

logger = get_logger("converters")


class DocumentConverter:
    """Convert data processing documents to vector documents.

    Transforms chunked documents from data processing pipeline
    into VectorDocuments suitable for vector storage.

    Strategy: Each chunk becomes a separate vector document with
    full document content and metadata preserved in metadata field.
    """

    def __init__(self, include_full_content: bool = True):
        """Initialize converter.

        Args:
            include_full_content: Include full document content in metadata
        """
        self.include_full_content = include_full_content

    def convert_document(
        self, document: Document, chunk_index: int = 0
    ) -> VectorDocument:
        """Convert single chunk to vector document.

        Args:
            document: Processed document with chunks
            chunk_index: Index of chunk to convert

        Returns:
            Vector document ready for storage

        Raises:
            ValueError: If chunk index is invalid
        """
        if not document.chunks:
            raise ValueError("Document has no chunks")

        if chunk_index >= len(document.chunks):
            raise ValueError(
                f"Chunk index {chunk_index} out of range "
                f"(document has {len(document.chunks)} chunks)"
            )

        chunk_content = document.chunks[chunk_index]

        base_id = document.metadata.get("message_id", "unknown")
        vector_id = f"{base_id}_{chunk_index}"

        metadata = {**document.metadata}

        if self.include_full_content:
            metadata["full_content"] = document.content

        metadata["chunk_index"] = chunk_index
        metadata["total_chunks"] = len(document.chunks)

        return VectorDocument(
            id=vector_id, content=chunk_content, metadata=metadata
        )

    def convert_document_chunks(
        self, document: Document
    ) -> list[VectorDocument]:
        """Convert all chunks of document to vector documents.

        Args:
            document: Processed document with chunks

        Returns:
            List of vector documents (one per chunk)
        """
        if not document.chunks:
            logger.warning("Document has no chunks, skipping conversion")
            return []

        vector_docs = []

        for i in range(len(document.chunks)):
            try:
                vector_doc = self.convert_document(document, i)
                vector_docs.append(vector_doc)
            except Exception as e:
                logger.error(
                    f"Error converting chunk {i} of document "
                    f"{document.metadata.get('message_id')}: {e}"
                )
                continue

        logger.debug(
            f"Converted document to {len(vector_docs)} vector documents"
        )
        return vector_docs

    def convert_batch(self, documents: list[Document]) -> list[VectorDocument]:
        """Convert batch of documents to vector documents.

        Args:
            documents: List of processed documents

        Returns:
            Flattened list of vector documents from all chunks
        """
        all_vector_docs = []

        for doc in documents:
            vector_docs = self.convert_document_chunks(doc)
            all_vector_docs.extend(vector_docs)

        logger.info(
            f"Converted {len(documents)} documents to "
            f"{len(all_vector_docs)} vector documents"
        )

        return all_vector_docs
