"""Authentication-specific schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    model_config = ConfigDict(from_attributes=True)

    login: str = Field(..., description="Email or phone number")
    password: str = Field(..., min_length=8, description="User password")


class TokenResponse(BaseModel):
    """Token response schema."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    model_config = ConfigDict(from_attributes=True)

    refresh_token: str


class TokenVerifyResponse(BaseModel):
    """Token verification response."""

    model_config = ConfigDict(from_attributes=True)

    valid: bool
    user_id: int | None = None
    email: str | None = None


class OTPSendRequest(BaseModel):
    """OTP send request schema."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr = Field(..., description="Email for OTP delivery")


class OTPResponse(BaseModel):
    """OTP response schema."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    expires_in_minutes: int = 10


class RegisterVerifyRequest(BaseModel):
    """Registration verification request."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    code: str = Field(..., min_length=6, max_length=6)
    full_name: str | None = Field(None, max_length=255)


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Password change request with old password."""

    model_config = ConfigDict(from_attributes=True)

    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class ChangePasswordOTPRequest(BaseModel):
    """Password change request with OTP."""

    model_config = ConfigDict(from_attributes=True)

    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)
