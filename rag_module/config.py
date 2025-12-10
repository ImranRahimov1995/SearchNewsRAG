"""RAG module configuration."""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
_DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"
_DEFAULT_COLLECTION = "news_analyzed_0_5k_800_200_large"


@dataclass
class RAGConfig:
    """RAG module configuration.

    Attributes:
        openai_api_key: OpenAI API key
        openai_model: OpenAI chat model name
        openai_embedding_model: OpenAI embedding model name
        openai_temperature: Temperature for chat completions
        openai_max_tokens: Maximum tokens for responses
        chroma_db_path: Path to ChromaDB storage
        chroma_collection_name: ChromaDB collection name
        chroma_host: ChromaDB server host (optional)
        chroma_port: ChromaDB server port (optional)
        default_top_k: Default number of results to retrieve
        min_similarity_score: Minimum similarity threshold
        log_level: Logging level
    """

    openai_api_key: str
    openai_model: str = _DEFAULT_OPENAI_MODEL
    openai_embedding_model: str = _DEFAULT_EMBEDDING_MODEL
    openai_temperature: float = 0.1
    openai_max_tokens: int = 2000

    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = _DEFAULT_COLLECTION
    chroma_host: str | None = None
    chroma_port: int | None = None

    default_top_k: int = 5
    min_similarity_score: float = 0.3

    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create config from environment variables.

        Returns:
            RAGConfig instance

        Raises:
            ValueError: If OPENAI_API_KEY is missing
        """
        api_key = cls._get_required_api_key()

        return cls(
            openai_api_key=api_key,
            openai_model=os.getenv("OPENAI_MODEL", _DEFAULT_OPENAI_MODEL),
            openai_embedding_model=os.getenv(
                "OPENAI_EMBEDDING_MODEL", _DEFAULT_EMBEDDING_MODEL
            ),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            chroma_db_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
            chroma_collection_name=os.getenv(
                "CHROMA_COLLECTION_NAME", _DEFAULT_COLLECTION
            ),
            chroma_host=os.getenv("CHROMA_HOST"),
            chroma_port=(
                int(port) if (port := os.getenv("CHROMA_PORT")) else None
            ),
            default_top_k=int(os.getenv("RAG_TOP_K", "5")),
            min_similarity_score=float(os.getenv("RAG_MIN_SCORE", "0.5")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @staticmethod
    def _get_required_api_key() -> str:
        """Get OpenAI API key from environment.

        Returns:
            API key string

        Raises:
            ValueError: If OPENAI_API_KEY is missing
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please create a .env file or set OPENAI_API_KEY in your environment."
            )
        return api_key


def get_logger(name: str) -> logging.Logger:
    """Get logger for RAG module.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level))

    return logger
