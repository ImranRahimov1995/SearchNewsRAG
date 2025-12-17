"""Repository layer for database operations."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from users.models import Group, Permission, Profile, User


class UserRepository:
    """Repository for User CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize user repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self, email: str, username: str, hashed_password: str, **kwargs: Any
    ) -> User:
        """Create a new user.

        Args:
            email: User email address
            username: Unique username
            hashed_password: Hashed password
            **kwargs: Additional user fields

        Returns:
            Created user instance
        """
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            **kwargs,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.groups).selectinload(Group.permissions))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: User email address

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.groups).selectinload(Group.permissions))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.groups).selectinload(Group.permissions))
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Get user by phone number.

        Args:
            phone: Phone number

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(
            select(User)
            .where(User.phone == phone)
            .options(selectinload(User.groups).selectinload(Group.permissions))
        )
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> User | None:
        """Get user by email or phone.

        Args:
            login: Email or phone number

        Returns:
            User instance or None if not found
        """
        user = await self.get_by_email(login)
        if user:
            return user
        return await self.get_by_phone(login)

    async def update(self, user_id: int, **kwargs: Any) -> User | None:
        """Update user fields.

        Args:
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated user instance or None if not found
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp.

        Args:
            user_id: User ID
        """
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            await self.session.commit()

    async def delete(self, user_id: int) -> bool:
        """Delete user.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True

    async def add_to_group(self, user_id: int, group_id: int) -> User | None:
        """Add user to a group.

        Args:
            user_id: User ID
            group_id: Group ID

        Returns:
            Updated user instance or None if not found
        """
        user = await self.get_by_id(user_id)
        group = await self._get_group_by_id(group_id)

        if user is None or group is None:
            return None

        if group not in user.groups:
            user.groups.append(group)
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def remove_from_group(
        self, user_id: int, group_id: int
    ) -> User | None:
        """Remove user from a group.

        Args:
            user_id: User ID
            group_id: Group ID

        Returns:
            Updated user instance or None if not found
        """
        user = await self.get_by_id(user_id)
        group = await self._get_group_by_id(group_id)

        if user is None or group is None:
            return None

        if group in user.groups:
            user.groups.remove(group)
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def get_user_permissions(self, user_id: int) -> set[str]:
        """Get all permission codenames for a user.

        Args:
            user_id: User ID

        Returns:
            Set of permission codenames
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return set()

        permissions = set()
        for group in user.groups:
            for permission in group.permissions:
                permissions.add(permission.codename)

        return permissions

    async def _get_group_by_id(self, group_id: int) -> Group | None:
        """Get group by ID.

        Args:
            group_id: Group ID

        Returns:
            Group instance or None if not found
        """
        result = await self.session.execute(
            select(Group).where(Group.id == group_id)
        )
        return result.scalar_one_or_none()


class PermissionRepository:
    """Repository for Permission CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize permission repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self, name: str, codename: str, description: str | None = None
    ) -> Permission:
        """Create a new permission.

        Args:
            name: Permission name
            codename: Unique permission codename
            description: Optional description

        Returns:
            Created permission instance
        """
        permission = Permission(
            name=name, codename=codename, description=description
        )
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission

    async def get_by_id(self, permission_id: int) -> Permission | None:
        """Get permission by ID.

        Args:
            permission_id: Permission ID

        Returns:
            Permission instance or None if not found
        """
        result = await self.session.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_codename(self, codename: str) -> Permission | None:
        """Get permission by codename.

        Args:
            codename: Permission codename

        Returns:
            Permission instance or None if not found
        """
        result = await self.session.execute(
            select(Permission).where(Permission.codename == codename)
        )
        return result.scalar_one_or_none()


class GroupRepository:
    """Repository for Group CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize group repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, name: str, description: str | None = None) -> Group:
        """Create a new group.

        Args:
            name: Group name
            description: Optional description

        Returns:
            Created group instance
        """
        group = Group(name=name, description=description)
        self.session.add(group)
        await self.session.commit()
        await self.session.refresh(group)
        return group

    async def get_by_id(self, group_id: int) -> Group | None:
        """Get group by ID.

        Args:
            group_id: Group ID

        Returns:
            Group instance or None if not found
        """
        result = await self.session.execute(
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.permissions))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Group | None:
        """Get group by name.

        Args:
            name: Group name

        Returns:
            Group instance or None if not found
        """
        result = await self.session.execute(
            select(Group)
            .where(Group.name == name)
            .options(selectinload(Group.permissions))
        )
        return result.scalar_one_or_none()

    async def add_permission(
        self, group_id: int, permission_id: int
    ) -> Group | None:
        """Add permission to a group.

        Args:
            group_id: Group ID
            permission_id: Permission ID

        Returns:
            Updated group instance or None if not found
        """
        group = await self.get_by_id(group_id)
        permission = await self._get_permission_by_id(permission_id)

        if group is None or permission is None:
            return None

        if permission not in group.permissions:
            group.permissions.append(permission)
            await self.session.commit()
            await self.session.refresh(group)

        return group

    async def _get_permission_by_id(
        self, permission_id: int
    ) -> Permission | None:
        """Get permission by ID.

        Args:
            permission_id: Permission ID

        Returns:
            Permission instance or None if not found
        """
        result = await self.session.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()


class ProfileRepository:
    """Repository for Profile CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize profile repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, user_id: int, **kwargs: Any) -> Profile:
        """Create a new profile.

        Args:
            user_id: User ID
            **kwargs: Profile fields

        Returns:
            Created profile instance
        """
        profile = Profile(user_id=user_id, **kwargs)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_by_user_id(self, user_id: int) -> Profile | None:
        """Get profile by user ID.

        Args:
            user_id: User ID

        Returns:
            Profile instance or None if not found
        """
        result = await self.session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user_id: int, **kwargs: Any) -> Profile | None:
        """Update profile fields.

        Args:
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated profile instance or None if not found
        """
        profile = await self.get_by_user_id(user_id)
        if profile is None:
            profile = await self.create(user_id, **kwargs)
            return profile

        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        await self.session.commit()
        await self.session.refresh(profile)
        return profile
