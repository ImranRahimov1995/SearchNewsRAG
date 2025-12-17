"""Database models for users, permissions, and groups."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    pass


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
)

group_permissions = Table(
    "group_permissions",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
    ),
)


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=user_groups,
        back_populates="users",
        lazy="selectin",
    )
    profile: Mapped["Profile | None"] = relationship(
        "Profile", back_populates="user", uselist=False, lazy="selectin"
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, phone={self.phone})>"


class Permission(Base):
    """Permission model for fine-grained access control."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    codename: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=group_permissions,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of Permission."""
        return f"<Permission(id={self.id}, codename={self.codename})>"


class Group(Base):
    """Group model for role-based access control."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_groups,
        back_populates="groups",
        lazy="selectin",
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=group_permissions,
        back_populates="groups",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of Group."""
        return f"<Group(id={self.id}, name={self.name})>"


class Profile(Base):
    """User profile model for additional user information."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    birthday: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        """String representation of Profile."""
        return f"<Profile(id={self.id}, user_id={self.user_id})>"


class OTP(Base):
    """OTP (One-Time Password) model for verification."""

    __tablename__ = "otps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    purpose: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of OTP."""
        return (
            f"<OTP(id={self.id}, purpose={self.purpose}, used={self.is_used})>"
        )
