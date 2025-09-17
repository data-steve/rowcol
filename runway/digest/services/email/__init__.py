"""
Email service providers with abstraction layer for SendGrid and SES fallback.
"""

from .base import EmailProvider
from .sendgrid_provider import SendGridProvider
from .ses_provider import SESProvider
from .mock_provider import MockEmailProvider
from .email_service import EmailService

__all__ = [
    "EmailProvider",
    "SendGridProvider", 
    "SESProvider",
    "MockEmailProvider",
    "EmailService"
]
