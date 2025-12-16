"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """Password hashing and verification handler."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)


class JWTHandler:
    """JWT token creation and validation handler."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        """Initialize JWT handler.

        Args:
            secret_key: Secret key for encoding/decoding tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token lifetime in minutes
            refresh_token_expire_days: Refresh token lifetime in days
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT access token.

        Args:
            data: Payload data to encode in token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update(
            {
                "exp": expire,
                "type": "access",
                "iat": datetime.now(timezone.utc),
            }
        )
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT refresh token.

        Args:
            data: Payload data to encode in token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self.refresh_token_expire_days
            )

        to_encode.update(
            {
                "exp": expire,
                "type": "refresh",
                "iat": datetime.now(timezone.utc),
            }
        )
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> dict[str, Any]:
        """Verify and decode JWT token.

        Args:
            token: JWT token string to verify
            token_type: Expected token type (access or refresh)

        Returns:
            Decoded token payload

        Raises:
            JWTError: If token is invalid or expired
            ValueError: If token type doesn't match expected type
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            if payload.get("type") != token_type:
                raise ValueError(f"Invalid token type: expected {token_type}")
            return payload
        except JWTError as e:
            raise JWTError(f"Token verification failed: {str(e)}") from e
