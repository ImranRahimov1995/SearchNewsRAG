"""Email notification service with SOLID principles."""

import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class IEmailSender(ABC):
    """Interface for email sending implementations."""

    @abstractmethod
    async def send_email(
        self, to_email: str, subject: str, body: str, html: bool = True
    ) -> bool:
        """Send email to recipient."""
        pass


class SMTPEmailSender(IEmailSender):
    """SMTP email sender implementation."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "SearchNewsRAG",
    ) -> None:
        """Initialize SMTP email sender.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            from_name: Sender display name
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name

    async def send_email(
        self, to_email: str, subject: str, body: str, html: bool = True
    ) -> bool:
        """Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether body is HTML format

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception:
            return False


class EmailTemplateService:
    """Service for generating email templates."""

    @staticmethod
    def get_otp_template(
        code: str, purpose: str, expires_minutes: int = 10
    ) -> str:
        """Generate OTP email template.

        Args:
            code: OTP code
            purpose: Purpose of OTP (registration, password reset, etc.)
            expires_minutes: OTP expiration time in minutes

        Returns:
            HTML email template
        """
        purpose_text = {
            "registration": "verify your account",
            "password_reset": "reset your password",
            "change_password": "change your password",
        }.get(purpose, "verify your action")

        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #333; margin: 0; }}
        .otp-code {{ background: #f0f0f0; border: 2px solid #4CAF50; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; }}
        .otp-code h2 {{ color: #4CAF50; font-size: 36px; margin: 0; letter-spacing: 8px; }}
        .message {{ color: #666; line-height: 1.6; text-align: center; }}
        .warning {{ color: #ff6b6b; font-size: 14px; margin-top: 20px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SearchNewsRAG</h1>
        </div>

        <div class="message">
            <p>You requested to {purpose_text}. Use the verification code below:</p>
        </div>

        <div class="otp-code">
            <h2>{code}</h2>
        </div>

        <div class="message">
            <p>This code will expire in <strong>{expires_minutes} minutes</strong>.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </div>

        <div class="warning">
            ⚠️ Never share this code with anyone!
        </div>

        <div class="footer">
            <p>© 2025 SearchNewsRAG. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

    @staticmethod
    def get_welcome_template(username: str) -> str:
        """Generate welcome email template.

        Args:
            username: User's name

        Returns:
            HTML email template
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #4CAF50; margin: 0; }}
        .message {{ color: #666; line-height: 1.6; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to SearchNewsRAG!</h1>
        </div>

        <div class="message">
            <p>Hello {username},</p>
            <p>Thank you for verifying your account! You're now ready to explore the latest Azerbaijani news with our powerful RAG-powered search.</p>
            <p>Get started by exploring trending news, searching for specific topics, or setting up your preferences.</p>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Happy searching!</p>
        </div>

        <div class="footer">
            <p>© 2025 SearchNewsRAG. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
