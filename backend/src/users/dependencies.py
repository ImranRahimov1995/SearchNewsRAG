"""Dependencies for authentication and authorization."""

from typing import Annotated

from auth.services import AuthService
from config import get_settings
from database import get_db_session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services.email_service import SMTPEmailSender
from auth.services.otp_service import OTPService
from users.models import User
from users.repository import UserRepository
from users.security import JWTHandler, PasswordHasher

settings = get_settings()

security = HTTPBearer()


def get_jwt_handler() -> JWTHandler:
    """Get JWT handler instance.

    Returns:
        Configured JWT handler

    Raises:
        RuntimeError: If JWT_SECRET_KEY is not configured
    """
    if not settings.jwt_secret_key:
        raise RuntimeError("JWT_SECRET_KEY not configured")

    return JWTHandler(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
    )


def get_password_hasher() -> PasswordHasher:
    """Get password hasher instance.

    Returns:
        Password hasher instance
    """
    return PasswordHasher()


def get_email_sender() -> SMTPEmailSender:
    """Get email sender instance.

    Returns:
        Configured email sender
    """
    return SMTPEmailSender(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
        from_email=settings.smtp_from_email,
        from_name=settings.smtp_from_name,
    )


async def get_otp_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    email_sender: Annotated[SMTPEmailSender, Depends(get_email_sender)],
) -> OTPService:
    """Get OTP service instance.

    Args:
        session: Database session
        email_sender: Email sender

    Returns:
        OTP service instance
    """
    return OTPService(
        session=session,
        email_sender=email_sender,
        otp_length=settings.otp_length,
        otp_expire_minutes=settings.otp_expire_minutes,
        max_attempts=settings.otp_max_attempts,
    )


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> AuthService:
    """Get authentication service instance.

    Args:
        session: Database session
        jwt_handler: JWT token handler
        password_hasher: Password hasher
        otp_service: OTP service

    Returns:
        Authentication service instance
    """
    return AuthService(session, jwt_handler, password_hasher, otp_service)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials
        session: Database session
        jwt_handler: JWT token handler

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        payload = jwt_handler.verify_token(token, token_type="access")
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Current active user
    """
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current superuser.

    Args:
        current_user: Current user from token

    Returns:
        Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have sufficient privileges",
        )
    return current_user


class PermissionChecker:
    """Dependency class for checking user permissions."""

    def __init__(self, required_permissions: list[str]) -> None:
        """Initialize permission checker.

        Args:
            required_permissions: List of required permission codenames
        """
        self.required_permissions = required_permissions

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> User:
        """Check if user has required permissions.

        Args:
            current_user: Current authenticated user
            session: Database session

        Returns:
            Current user if authorized

        Raises:
            HTTPException: If user lacks required permissions
        """
        if current_user.is_superuser:
            return current_user

        user_repo = UserRepository(session)
        user_permissions = await user_repo.get_user_permissions(
            current_user.id
        )

        for required_permission in self.required_permissions:
            if required_permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {required_permission} required",
                )

        return current_user


def require_permissions(permissions: list[str]) -> PermissionChecker:
    """Create a permission checker dependency.

    Args:
        permissions: List of required permission codenames

    Returns:
        Permission checker dependency
    """
    return PermissionChecker(permissions)
