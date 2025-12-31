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

    openai_api_key: str = Field(
        default="", description="OpenAI API key (from OPENAI_API_KEY env var)"
    )

    async_database_url: str | None = Field(
        default=None, description="PostgreSQL async connection URL"
    )

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

    redis_url: str | None = Field(
        default=None, description="Redis connection URL"
    )
    cache_ttl: int = Field(
        default=3600*24*3, description="Cache time to live in seconds"
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

    jwt_secret_key: str = Field(
        default="", description="Secret key for JWT token encoding/decoding"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    smtp_host: str = Field(
        default="smtp.gmail.com",
        description="SMTP host",
        validation_alias="EMAIL_HOST",
    )
    smtp_port: int = Field(
        default=587, description="SMTP port", validation_alias="EMAIL_PORT"
    )
    smtp_user: str = Field(
        default="",
        description="SMTP username",
        validation_alias="EMAIL_HOST_USER",
    )
    smtp_password: str = Field(
        default="",
        description="SMTP password",
        validation_alias="EMAIL_HOST_PASSWORD",
    )
    smtp_from_email: str = Field(
        default="",
        description="From email address",
        validation_alias="DEFAULT_FROM_EMAIL",
    )
    smtp_from_name: str = Field(
        default="SearchNewsRAG", description="From name"
    )

    otp_length: int = Field(default=6, description="OTP code length")
    otp_expire_minutes: int = Field(
        default=10, description="OTP expiration in minutes"
    )
    otp_max_attempts: int = Field(
        default=3, description="Maximum OTP verification attempts"
    )

    superuser_email: str = Field(
        default="admin@searchnewsrag.com",
        description="Default superuser email",
    )
    superuser_password: str = Field(
        default="", description="Default superuser password"
    )


def get_settings() -> BackendSettings:
    """Get backend settings singleton."""
    return BackendSettings()
