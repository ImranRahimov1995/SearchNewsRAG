"""Superuser creation utility."""

import logging

from config import get_settings
from database import get_db_manager
from sqlalchemy import select
from users.models import User
from users.security import PasswordHasher

logger = logging.getLogger(__name__)


async def create_superuser_if_not_exists() -> None:
    """Create superuser if it does not exist.

    Updates password if user exists.
    """
    settings = get_settings()

    if not settings.superuser_password:
        logger.warning(
            "SUPERUSER_PASSWORD not set, skipping superuser creation"
        )
        return

    db_manager = get_db_manager()

    async for session in db_manager.get_session():
        result = await session.execute(
            select(User).where(User.email == settings.superuser_email)
        )
        existing_user = result.scalar_one_or_none()

        password_hasher = PasswordHasher()

        if existing_user:
            existing_user.hashed_password = password_hasher.hash_password(
                settings.superuser_password
            )
            existing_user.is_superuser = True
            existing_user.is_active = True
            await session.commit()

            logger.info(
                f"Superuser password updated: {settings.superuser_email}"
            )
            return

        phone = getattr(settings, "superuser_phone", None) or "0000000000"
        superuser = User(
            email=settings.superuser_email,
            phone=phone,
            username="admin",
            hashed_password=password_hasher.hash_password(
                settings.superuser_password
            ),
            full_name="Administrator",
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )

        session.add(superuser)
        await session.commit()

        logger.info(
            f"Superuser created successfully: {settings.superuser_email}"
        )
