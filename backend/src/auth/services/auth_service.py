"""Authentication service for user registration, login, and token management."""

from typing import Any

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from users.repository import GroupRepository, ProfileRepository, UserRepository
from users.schemas import UserCreate
from users.security import JWTHandler, PasswordHasher

from .otp_service import OTPService


class AuthService:
    """Service for authentication operations."""

    def __init__(
        self,
        session: AsyncSession,
        jwt_handler: JWTHandler,
        password_hasher: PasswordHasher,
        otp_service: OTPService | None = None,
    ) -> None:
        """Initialize authentication service.

        Args:
            session: SQLAlchemy async session
            jwt_handler: JWT token handler
            password_hasher: Password hashing handler
            otp_service: Optional OTP service for registration/reset
        """
        self.session = session
        self.jwt_handler = jwt_handler
        self.password_hasher = password_hasher
        self.otp_service = otp_service
        self.user_repo = UserRepository(session)
        self.group_repo = GroupRepository(session)
        self.profile_repo = ProfileRepository(session)

    async def register_user(self, user_data: UserCreate) -> dict[str, Any]:
        """Register a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user data with tokens

        Raises:
            HTTPException: If email or username already exists
        """
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        if user_data.username:
            existing_username = await self.user_repo.get_by_username(
                user_data.username
            )
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        hashed_password = self.password_hasher.hash_password(
            user_data.password
        )

        user = await self.user_repo.create(
            email=user_data.email,
            username=user_data.username,
            phone=user_data.phone,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        user = await self.user_repo.get_by_id(user.id)

        tokens = self._generate_tokens(user.id)

        return {"user": user, **tokens}

    async def authenticate_user(
        self, login: str, password: str
    ) -> dict[str, Any]:
        """Authenticate user and generate tokens.

        Args:
            login: Email or phone number
            password: Plain text password

        Returns:
            User data with access and refresh tokens

        Raises:
            HTTPException: If credentials are invalid or user is inactive
        """
        user = await self.user_repo.get_by_login(login)

        if user is None or not self.password_hasher.verify_password(
            password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your account first",
            )

        await self.user_repo.update_last_login(user.id)

        tokens = self._generate_tokens(user.id)

        return {"user": user, **tokens}

    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        """Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access and refresh tokens

        Raises:
            HTTPException: If refresh token is invalid or user not found
        """
        try:
            payload = self.jwt_handler.verify_token(
                refresh_token,
                token_type="refresh",  # nosec B106
            )
            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )

            user = await self.user_repo.get_by_id(int(user_id))
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

            return self._generate_tokens(user.id)

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}",
            ) from e

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify access token validity.

        Args:
            token: JWT access token

        Returns:
            Token verification result
        """
        try:
            payload = self.jwt_handler.verify_token(token, token_type="access")  # nosec B106
            user_id = payload.get("sub")

            if user_id is None:
                return {
                    "valid": False,
                    "message": "Invalid token payload",
                }

            user = await self.user_repo.get_by_id(int(user_id))
            if user is None:
                return {
                    "valid": False,
                    "message": "User not found",
                }

            if not user.is_active:
                return {
                    "valid": False,
                    "message": "User account is inactive",
                }

            return {
                "valid": True,
                "user_id": user.id,
            }

        except JWTError as e:
            return {
                "valid": False,
                "message": f"Token verification failed: {str(e)}",
            }

    def _generate_tokens(self, user_id: int) -> dict[str, str]:
        """Generate access and refresh tokens.

        Args:
            user_id: User ID

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = self.jwt_handler.create_access_token(
            data={"sub": user_id}
        )
        refresh_token = self.jwt_handler.create_refresh_token(
            data={"sub": user_id}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def register_with_otp(
        self, email: str, phone: str, password: str, code: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Complete registration with OTP verification.

        Args:
            email: User email
            phone: User phone
            password: User password
            code: OTP code
            **kwargs: Additional user fields

        Returns:
            Created user with tokens

        Raises:
            HTTPException: If validation fails
        """
        if not self.otp_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OTP service not configured",
            )

        await self.otp_service.verify_otp(code, "registration", email=email)

        existing_email = await self.user_repo.get_by_email(email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        if phone:
            existing_phone = await self.user_repo.get_by_phone(phone)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone already registered",
                )

        hashed_password = self.password_hasher.hash_password(password)

        user = await self.user_repo.create(
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            **kwargs,
        )

        await self.profile_repo.create(user_id=user.id)

        if self.otp_service:
            await self.otp_service.send_welcome_email(user)

        tokens = self._generate_tokens(user.id)
        return {"user": user, **tokens}

    async def reset_password_with_otp(
        self, email: str, code: str, new_password: str
    ) -> dict[str, str]:
        """Reset password using OTP verification.

        Args:
            email: User email
            code: OTP code
            new_password: New password

        Returns:
            Success message

        Raises:
            HTTPException: If validation fails
        """
        if not self.otp_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OTP service not configured",
            )

        await self.otp_service.verify_otp(code, "password_reset", email=email)

        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        hashed_password = self.password_hasher.hash_password(new_password)
        await self.user_repo.update(user.id, hashed_password=hashed_password)

        return {"message": "Password reset successful"}

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> dict[str, str]:
        """Change password with old password verification.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Success message

        Raises:
            HTTPException: If old password is incorrect
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not self.password_hasher.verify_password(
            old_password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password",
            )

        hashed_password = self.password_hasher.hash_password(new_password)
        await self.user_repo.update(user_id, hashed_password=hashed_password)

        return {"message": "Password changed successfully"}

    async def change_password_with_otp(
        self, user_id: int, code: str, new_password: str
    ) -> dict[str, str]:
        """Change password using OTP verification.

        Args:
            user_id: User ID
            code: OTP code
            new_password: New password

        Returns:
            Success message

        Raises:
            HTTPException: If validation fails
        """
        if not self.otp_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OTP service not configured",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await self.otp_service.verify_otp(
            code, "change_password", email=user.email
        )

        hashed_password = self.password_hasher.hash_password(new_password)
        await self.user_repo.update(user_id, hashed_password=hashed_password)

        return {"message": "Password changed successfully"}
