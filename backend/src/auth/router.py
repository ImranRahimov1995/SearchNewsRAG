"""Authentication routes for login, registration, and password management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from users.dependencies import (
    get_auth_service,
    get_current_active_user,
    get_otp_service,
)
from users.models import User
from backend.src.auth.services.otp_service import OTPService
from users.schemas import UserResponse
from auth.services import AuthService

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

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register/send-otp", response_model=OTPResponse)
async def send_registration_otp(
    email_data: OTPSendRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> OTPResponse:
    """Send OTP for registration.

    Args:
        email_data: Email for OTP
        otp_service: OTP service

    Returns:
        OTP sent confirmation

    Raises:
        HTTPException: If email already exists
    """
    if not email_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required for registration",
        )

    await otp_service.send_otp_email(
        email=email_data.email, purpose="registration"
    )

    return OTPResponse(
        message="Verification code sent to your email",
        expires_in_minutes=10,
    )


@router.post("/register/resend-otp", response_model=OTPResponse)
async def resend_registration_otp(
    email_data: OTPSendRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> OTPResponse:
    """Resend OTP for registration.

    Args:
        email_data: Email for OTP
        otp_service: OTP service

    Returns:
        OTP sent confirmation
    """
    if not email_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required",
        )

    await otp_service.send_otp_email(
        email=email_data.email, purpose="registration"
    )

    return OTPResponse(
        message="Verification code resent to your email",
        expires_in_minutes=10,
    )


@router.post(
    "/register/verify",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def verify_registration(
    verify_data: RegisterVerifyRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Complete registration with OTP verification.

    Args:
        verify_data: Registration verification data
        auth_service: Authentication service

    Returns:
        Created user data

    Raises:
        HTTPException: If verification fails
    """
    result = await auth_service.register_with_otp(
        email=verify_data.email,
        phone=verify_data.phone,
        password=verify_data.password,
        code=verify_data.code,
        full_name=verify_data.full_name,
    )

    return UserResponse.model_validate(result["user"])


@router.post("/token", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Authenticate user and return access/refresh tokens.

    Args:
        login_data: Login credentials (email/phone and password)
        auth_service: Authentication service

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    result = await auth_service.authenticate_user(
        login_data.login, login_data.password
    )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Generate new access token from refresh token.

    Args:
        refresh_data: Refresh token
        auth_service: Authentication service

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    result = await auth_service.refresh_access_token(
        refresh_data.refresh_token
    )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    token: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenVerifyResponse:
    """Verify token validity.

    Args:
        token: JWT access token to verify
        auth_service: Authentication service

    Returns:
        Token verification result
    """
    result = await auth_service.verify_token(token)
    return TokenVerifyResponse(**result)


@router.post("/reset-password/send-otp", response_model=OTPResponse)
async def send_password_reset_otp(
    email_data: OTPSendRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> OTPResponse:
    """Send OTP for password reset.

    Args:
        email_data: Email for password reset
        otp_service: OTP service

    Returns:
        OTP sent confirmation
    """
    if not email_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required",
        )

    await otp_service.send_otp_email(
        email=email_data.email, purpose="password_reset"
    )

    return OTPResponse(
        message="Password reset code sent to your email",
        expires_in_minutes=10,
    )


@router.post("/reset-password/resend-otp", response_model=OTPResponse)
async def resend_password_reset_otp(
    email_data: OTPSendRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> OTPResponse:
    """Resend OTP for password reset.

    Args:
        email_data: Email for password reset
        otp_service: OTP service

    Returns:
        OTP sent confirmation
    """
    if not email_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required",
        )

    await otp_service.send_otp_email(
        email=email_data.email, purpose="password_reset"
    )

    return OTPResponse(
        message="Password reset code resent to your email",
        expires_in_minutes=10,
    )


@router.post("/reset-password/verify")
async def verify_password_reset(
    reset_data: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Reset password with OTP verification.

    Args:
        reset_data: Password reset data
        auth_service: Authentication service

    Returns:
        Success message
    """
    return await auth_service.reset_password_with_otp(
        reset_data.email, reset_data.code, reset_data.new_password
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Change password with old password verification.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    return await auth_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password,
    )


@router.post("/change-password/send-otp", response_model=OTPResponse)
async def send_change_password_otp(
    current_user: Annotated[User, Depends(get_current_active_user)],
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> OTPResponse:
    """Send OTP for password change.

    Args:
        current_user: Current authenticated user
        otp_service: OTP service

    Returns:
        OTP sent confirmation
    """
    await otp_service.send_otp_email(
        email=current_user.email,
        purpose="change_password",
        user_id=current_user.id,
    )

    return OTPResponse(
        message="Verification code sent to your email",
        expires_in_minutes=10,
    )


@router.post("/change-password/verify-otp")
async def verify_change_password_otp(
    otp_data: ChangePasswordOTPRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Change password with OTP verification.

    Args:
        otp_data: OTP verification data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message
    """
    return await auth_service.change_password_with_otp(
        current_user.id, otp_data.code, otp_data.new_password
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return UserResponse.model_validate(current_user)
