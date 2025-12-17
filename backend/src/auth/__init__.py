"""Authentication module for JWT tokens and OTP verification."""

from auth.schemas import (
    ChangePasswordOTPRequest,
    ChangePasswordRequest,
    LoginRequest,
    OTPResponse,
    OTPSendRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterVerifyRequest,
    TokenResponse,
    TokenVerifyResponse,
)

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "TokenVerifyResponse",
    "RefreshTokenRequest",
    "OTPSendRequest",
    "OTPResponse",
    "RegisterVerifyRequest",
    "PasswordResetRequest",
    "ChangePasswordRequest",
    "ChangePasswordOTPRequest",
]
