"""Pydantic schemas for request and response validation."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PermissionBase(BaseModel):
    """Base schema for Permission."""

    name: str = Field(..., min_length=1, max_length=100)
    codename: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""

    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class GroupBase(BaseModel):
    """Base schema for Group."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class GroupCreate(GroupBase):
    """Schema for creating a new group."""

    permission_ids: list[int] = Field(default_factory=list)


class GroupResponse(GroupBase):
    """Schema for group response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    permissions: list[PermissionResponse] = Field(default_factory=list)


class ProfileBase(BaseModel):
    """Base schema for Profile."""

    avatar_url: str | None = None
    birthday: date | None = None
    city: str | None = None
    country: str | None = None
    bio: str | None = None


class ProfileUpdate(ProfileBase):
    """Schema for updating profile."""

    pass


class ProfileResponse(ProfileBase):
    """Schema for profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class UserBase(BaseModel):
    """Base schema for User."""

    email: EmailStr
    phone: str | None = Field(None, min_length=10, max_length=20)
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserRegisterRequest(BaseModel):
    """Schema for initial registration request."""

    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str | None = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=10, max_length=20)
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    group_ids: list[int] | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None
    groups: list[GroupResponse] = Field(default_factory=list)
    profile: ProfileResponse | None = None


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: int
    type: str
    exp: datetime
    iat: datetime


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenVerifyResponse(BaseModel):
    """Schema for token verification response."""

    valid: bool
    user_id: int | None = None
    message: str | None = None


class LoginRequest(BaseModel):
    """Schema for login request."""

    login: str = Field(..., min_length=1, description="Email or phone number")
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., min_length=1)


class OTPSendRequest(BaseModel):
    """Schema for sending OTP."""

    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=10, max_length=20)


class OTPVerifyRequest(BaseModel):
    """Schema for verifying OTP."""

    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=10, max_length=20)
    code: str = Field(..., min_length=4, max_length=10)


class RegisterVerifyRequest(BaseModel):
    """Schema for registration verification."""

    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    password: str = Field(..., min_length=8, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    full_name: str | None = None


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""

    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePasswordOTPRequest(BaseModel):
    """Schema for changing password with OTP."""

    code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=8, max_length=100)


class OTPResponse(BaseModel):
    """Schema for OTP send response."""

    message: str
    expires_in_minutes: int
