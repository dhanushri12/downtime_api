"""
═══════════════════════════════════════════════════════════════════════
EMAIL SERVICE MODULE
═══════════════════════════════════════════════════════════════════════
Handles email sending functionality including OTP and notifications.
Uses Gmail SMTP with secure configuration.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config import settings
from constants import EMAIL_SUBJECT_OTP, EMAIL_SUBJECT_WELCOME

# ═══════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# EMAIL SERVICE CLASS
# ═══════════════════════════════════════════════


class EmailService:
    """
    Email service for sending notifications and OTPs.
    Uses Gmail SMTP protocol.
    """

    def __init__(
        self,
        sender_email: str = settings.EMAIL_ADDRESS,
        app_password: str = settings.EMAIL_PASSWORD,
        smtp_host: str = settings.EMAIL_HOST,
        smtp_port: int = settings.EMAIL_PORT
    ):
        """
        Initialize email service.
        
        Args:
            sender_email: Gmail address.
            app_password: Gmail app password (not regular password).
            smtp_host: SMTP server host.
            smtp_port: SMTP server port.
        """
        self.sender_email = sender_email
        self.app_password = app_password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_otp_email(self, recipient_email: str, otp: str) -> bool:
        """
        Send OTP to recipient email.
        
        Args:
            recipient_email: Email address to send OTP to.
            otp: One-time password to send.
            
        Returns:
            True if email sent successfully, False otherwise.
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = EMAIL_SUBJECT_OTP
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # Plain text version
            text = f"""Your OTP for Password Reset: {otp}

Valid for {settings.OTP_EXPIRY_MINUTES} minutes.

If you didn't request this, please ignore this email."""

            # HTML version
            html = f"""\
            <html>
              <body>
                <h2>Password Reset OTP</h2>
                <p>Your OTP is: <strong>{otp}</strong></p>
                <p>Valid for {settings.OTP_EXPIRY_MINUTES} minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <hr>
                <small>Wind Turbine SCADA System</small>
              </body>
            </html>
            """

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())

            logger.info(f"OTP email sent successfully to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            return False

    def send_welcome_email(self, recipient_email: str, user_name: str) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            recipient_email: Email address of new user.
            user_name: Name of the user.
            
        Returns:
            True if email sent successfully, False otherwise.
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = EMAIL_SUBJECT_WELCOME
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # Plain text version
            text = f"""Welcome to {settings.APP_NAME}!

Hello {user_name},

Your account has been created successfully. 
You can now access the Wind Turbine SCADA Dashboard.

Best regards,
Wind Turbine Support Team"""

            # HTML version
            html = f"""\
            <html>
              <body>
                <h2>Welcome to {settings.APP_NAME}!</h2>
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>Your account has been created successfully.</p>
                <p>You can now access the Wind Turbine SCADA Dashboard.</p>
                <br>
                <p>Best regards,<br>Wind Turbine Support Team</p>
                <hr>
                <small>{settings.APP_NAME}</small>
              </body>
            </html>
            """

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())

            logger.info(f"Welcome email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False

    def send_generic_email(
        self,
        recipient_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send generic email with custom content.
        
        Args:
            recipient_email: Recipient email address.
            subject: Email subject.
            body_text: Plain text body.
            body_html: Optional HTML body.
            
        Returns:
            True if email sent successfully, False otherwise.
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email

            part1 = MIMEText(body_text, "plain")
            message.attach(part1)

            if body_html:
                part2 = MIMEText(body_html, "html")
                message.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())

            logger.info(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False


# ═══════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════
email_service = EmailService()
