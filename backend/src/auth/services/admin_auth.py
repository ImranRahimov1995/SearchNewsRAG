"""SQLAdmin authentication backend for superuser-only access."""

from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from src.database import get_db_manager
from users.models import User
from users.security import JWTHandler


class AdminAuthBackend(AuthenticationBackend):
    """Authentication backend for SQLAdmin with superuser verification."""

    def __init__(self, secret_key: str) -> None:
        """Initialize admin authentication backend.

        Args:
            secret_key: JWT secret key for token verification
        """
        super().__init__(secret_key)
        self.jwt_handler = JWTHandler(secret_key=secret_key)

    async def login(self, request: Request) -> bool:
        """Handle admin login.

        Args:
            request: HTTP request with form data (username, password)

        Returns:
            True if login successful, False otherwise
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        async with get_db_manager().get_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()

            if not user or not user.is_superuser or not user.is_active:
                return False

            from users.security import PasswordHasher

            password_hasher = PasswordHasher()
            if not password_hasher.verify_password(
                password, user.hashed_password
            ):
                return False

            token = self.jwt_handler.create_access_token(
                data={"sub": user.id, "is_superuser": True}
            )
            request.session.update({"token": token})
            return True

    async def logout(self, request: Request) -> bool:
        """Handle admin logout.

        Args:
            request: HTTP request

        Returns:
            True
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Verify user has valid superuser token.

        Args:
            request: HTTP request with session token

        Returns:
            True if user is authenticated superuser, False otherwise
        """
        token = request.session.get("token")

        if not token:
            return False

        try:
            payload = self.jwt_handler.verify_token(token, token_type="access")
            user_id = payload.get("sub")
            is_superuser = payload.get("is_superuser", False)

            if not user_id or not is_superuser:
                return False

            async with get_db_manager.get_session() as session:
                result = await session.execute(
                    select(User).where(User.id == int(user_id))
                )
                user = result.scalar_one_or_none()

                if not user or not user.is_superuser or not user.is_active:
                    return False

                return True

        except Exception:
            return False
