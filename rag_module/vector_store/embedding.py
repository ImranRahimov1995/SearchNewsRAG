"""Embedding implementations using LangChain."""

from langchain_openai import OpenAIEmbeddings

from rag_module.config import get_logger

logger = get_logger("embedding")


class LangChainEmbedding:
    """LangChain-based embedding implementation.

    Wraps LangChain's OpenAIEmbeddings to conform to IEmbedding protocol.
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        chunk_size: int = 500,
    ):
        """Initialize LangChain embedding.

        Args:
            model: OpenAI embedding model name
            chunk_size: Batch size for embedding requests
        """
        self.model = model
        self.chunk_size = chunk_size
        self._embeddings = OpenAIEmbeddings(
            model=model,
            chunk_size=chunk_size,
        )

        logger.info(f"Initialized LangChainEmbedding: model={model}")

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for single text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        result: list[float] = self._embeddings.embed_query(text)
        return result

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        result: list[list[float]] = self._embeddings.embed_documents(texts)
        return result

    @property
    def dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Dimension of embedding vectors
        """
        if self.model == "text-embedding-3-small":
            return 1536
        elif self.model == "text-embedding-3-large":
            return 3072
        else:
            return 1536
