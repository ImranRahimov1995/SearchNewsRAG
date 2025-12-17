"""OTP (One-Time Password) service for verification."""

import secrets
import string
from datetime import datetime, timedelta, timezone

from auth.services.email_service import EmailTemplateService, IEmailSender
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from users.models import OTP, User


class OTPService:
    """Service for managing OTP operations."""

    def __init__(
        self,
        session: AsyncSession,
        email_sender: IEmailSender,
        otp_length: int = 6,
        otp_expire_minutes: int = 10,
        max_attempts: int = 3,
    ) -> None:
        """Initialize OTP service.

        Args:
            session: SQLAlchemy async session
            email_sender: Email sender implementation
            otp_length: Length of generated OTP code
            otp_expire_minutes: OTP expiration time in minutes
            max_attempts: Maximum verification attempts allowed
        """
        self.session = session
        self.email_sender = email_sender
        self.otp_length = otp_length
        self.otp_expire_minutes = otp_expire_minutes
        self.max_attempts = max_attempts
        self.template_service = EmailTemplateService()

    def _generate_code(self) -> str:
        """Generate random OTP code.

        Returns:
            Random numeric OTP code
        """
        return "".join(
            secrets.choice(string.digits) for _ in range(self.otp_length)
        )

    async def create_otp(
        self,
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
        user_id: int | None = None,
    ) -> OTP:
        """Create a new OTP record.

        Args:
            purpose: Purpose of OTP (registration, password_reset, etc.)
            email: Email address for OTP
            phone: Phone number for OTP
            user_id: Associated user ID

        Returns:
            Created OTP instance

        Raises:
            ValueError: If neither email nor phone provided
        """
        if not email and not phone:
            raise ValueError("Either email or phone must be provided")

        await self._invalidate_previous_otps(purpose, email, phone, user_id)

        code = self._generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.otp_expire_minutes
        )

        otp = OTP(
            user_id=user_id,
            email=email,
            phone=phone,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
        )

        self.session.add(otp)
        await self.session.commit()
        await self.session.refresh(otp)

        return otp

    async def send_otp_email(
        self, email: str, purpose: str, user_id: int | None = None
    ) -> bool:
        """Generate and send OTP via email.

        Args:
            email: Recipient email address
            purpose: Purpose of OTP
            user_id: Associated user ID

        Returns:
            True if sent successfully

        Raises:
            HTTPException: If email sending fails
        """
        otp = await self.create_otp(
            purpose=purpose, email=email, user_id=user_id
        )

        subject = {
            "registration": "Verify Your Account",
            "password_reset": "Reset Your Password",
            "change_password": "Verify Password Change",
        }.get(purpose, "Verification Code")

        html_body = self.template_service.get_otp_template(
            code=otp.code,
            purpose=purpose,
            expires_minutes=self.otp_expire_minutes,
        )

        success = await self.email_sender.send_email(
            to_email=email, subject=subject, body=html_body, html=True
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email",
            )

        return True

    async def verify_otp(
        self,
        code: str,
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> OTP:
        """Verify OTP code.

        Args:
            code: OTP code to verify
            purpose: Expected purpose
            email: Email associated with OTP
            phone: Phone associated with OTP

        Returns:
            Verified OTP instance

        Raises:
            HTTPException: If OTP is invalid, expired, or max attempts exceeded
        """
        filters = [
            OTP.code == code,
            OTP.purpose == purpose,
            OTP.is_used == False,  # noqa: E712
        ]

        if email:
            filters.append(OTP.email == email)
        if phone:
            filters.append(OTP.phone == phone)

        result = await self.session.execute(select(OTP).where(and_(*filters)))
        otp = result.scalar_one_or_none()

        if otp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        otp.attempts += 1

        if otp.attempts > self.max_attempts:
            otp.is_used = True
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded",
            )

        if datetime.now(timezone.utc) > otp.expires_at:
            otp.is_used = True
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired",
            )

        otp.is_used = True
        await self.session.commit()

        return otp

    async def _invalidate_previous_otps(
        self,
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
        user_id: int | None = None,
    ) -> None:
        """Invalidate all previous unused OTPs for the same purpose.

        Args:
            purpose: OTP purpose
            email: Email address
            phone: Phone number
            user_id: User ID
        """
        filters = [OTP.purpose == purpose, OTP.is_used == False]  # noqa: E712

        if user_id:
            filters.append(OTP.user_id == user_id)
        if email:
            filters.append(OTP.email == email)
        if phone:
            filters.append(OTP.phone == phone)

        result = await self.session.execute(select(OTP).where(and_(*filters)))
        old_otps = result.scalars().all()

        for old_otp in old_otps:
            old_otp.is_used = True

        await self.session.commit()

    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email after successful registration.

        Args:
            user: User instance

        Returns:
            True if email sent successfully, False otherwise
        """
        html_body = self.template_service.get_welcome_template(
            username=user.username or user.email.split("@")[0]
        )

        success = await self.email_sender.send_email(
            to_email=user.email,
            subject="Welcome to SearchNewsRAG!",
            body=html_body,
            html=True,
        )

        return success
