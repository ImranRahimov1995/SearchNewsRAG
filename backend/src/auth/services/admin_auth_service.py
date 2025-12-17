"""SQLAdmin authentication backend for superuser-only access."""

from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from src.database import get_db_manager
from users.models import User


class AdminAuthBackend(AuthenticationBackend):
    """Authentication backend for SQLAdmin with superuser verification."""

    def __init__(self, secret_key: str) -> None:
        """Initialize admin authentication backend.

        Args:
            secret_key: Secret key for session management
        """
        super().__init__(secret_key)

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

        async for session in get_db_manager().get_session():
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

            request.session["user_id"] = user.id
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
        """Verify user has valid superuser session.

        Args:
            request: HTTP request with session

        Returns:
            True if user is authenticated superuser, False otherwise
        """
        user_id = request.session.get("user_id")
        if not user_id:
            return False

        try:
            async for session in get_db_manager().get_session():
                result = await session.execute(
                    select(User).where(User.id == int(user_id))
                )
                user = result.scalar_one_or_none()

                if not user or not user.is_superuser or not user.is_active:
                    return False

                return True

        except Exception:
            return False
