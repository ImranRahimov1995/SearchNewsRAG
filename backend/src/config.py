"""Backend service configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendSettings(BaseSettings):
    """Backend service settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", description="Server host")  # nosec B104
    port: int = Field(default=8000, description="Server port")
    environment: str = Field(
        default="local", description="Environment: local/prod"
    )
    debug: bool = Field(default=False, description="Debug mode")

    openai_api_key: str = Field(..., description="OpenAI API key")

    chroma_db_path: str = Field(
        default="./chroma_db", description="ChromaDB storage path"
    )
    chroma_collection_name: str = Field(
        default="news_analyzed_0_5k_800_200_large",
        description="ChromaDB collection name",
    )
    chroma_host: str | None = Field(
        default=None, description="ChromaDB server host (for client mode)"
    )
    chroma_port: int | None = Field(
        default=None, description="ChromaDB server port (for client mode)"
    )

    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="json", description="Log format: json or text"
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )
    rag_top_k: int = Field(
        default=5, description="Default top_k for retrieval"
    )
    rag_max_tokens: int = Field(
        default=2000, description="Max tokens for LLM response"
    )


def get_settings() -> BackendSettings:
    """Get backend settings singleton."""
    return BackendSettings()
