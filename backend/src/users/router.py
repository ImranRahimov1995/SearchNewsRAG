"""User management routes for CRUD operations and profiles."""

from typing import Annotated

from database import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from users.dependencies import (
    get_auth_service,
    get_current_active_user,
    get_current_superuser,
)
from users.models import User
from users.repository import ProfileRepository, UserRepository
from users.schemas import (
    ProfileResponse,
    ProfileUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from auth.services import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    """Get user by ID (superuser only).

    Args:
        user_id: User ID
        current_user: Current superuser
        session: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(get_current_superuser)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Create a new user (superuser only).

    Args:
        user_data: User creation data
        current_user: Current superuser
        auth_service: Authentication service

    Returns:
        Created user data
    """
    result = await auth_service.register_user(user_data)
    return UserResponse.model_validate(result["user"])


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    """Update user (superuser only).

    Args:
        user_id: User ID
        user_data: User update data
        current_user: Current superuser
        session: Database session

    Returns:
        Updated user data

    Raises:
        HTTPException: If user not found
    """
    repo = UserRepository(session)

    update_dict = user_data.model_dump(exclude_unset=True)
    group_ids = update_dict.pop("group_ids", None)

    user = await repo.update(user_id, **update_dict)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if group_ids is not None:
        for group_id in group_ids:
            await repo.add_to_group(user_id, group_id)

    user = await repo.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    """Soft delete user by setting is_active=False (superuser only).

    Args:
        user_id: User ID
        current_user: Current superuser
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found
    """
    repo = UserRepository(session)
    user = await repo.update(user_id, is_active=False)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "User deactivated successfully"}


@router.get("/profile/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileResponse:
    """Get current user's profile.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        User profile data
    """
    repo = ProfileRepository(session)
    profile = await repo.get_by_user_id(current_user.id)

    if not profile:
        profile = await repo.create(user_id=current_user.id)

    return ProfileResponse.model_validate(profile)


@router.patch("/profile/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileResponse:
    """Update current user's profile.

    Args:
        profile_data: Profile update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated profile data
    """
    repo = ProfileRepository(session)
    update_dict = profile_data.model_dump(exclude_unset=True)
    profile = await repo.update(current_user.id, **update_dict)

    return ProfileResponse.model_validate(profile)


@router.get("/admin/test")
async def admin_test(
    current_user: Annotated[User, Depends(get_current_superuser)],
) -> dict[str, str]:
    """Test endpoint for superuser access.

    Args:
        current_user: Current superuser

    Returns:
        Success message
    """
    return {
        "message": f"Welcome superuser {current_user.username or current_user.email}",
        "user_id": str(current_user.id),
    }
