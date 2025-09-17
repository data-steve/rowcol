import os
import logging
from typing import List, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent
from .base import EmailProvider, EmailMessage, EmailResult

logger = logging.getLogger(__name__)

class SendGridProvider(EmailProvider):
    """SendGrid email provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            raise ValueError("SendGrid API key is required")
        
        self.client = SendGridAPIClient(api_key=self.api_key)
        
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send a single email via SendGrid"""
        try:
            # Build SendGrid message
            mail = Mail(
                from_email=From(
                    message.from_email or self.get_default_from_email(),
                    message.from_name or self.get_default_from_name()
                ),
                to_emails=To(message.to_email),
                subject=Subject(message.subject),
                html_content=HtmlContent(message.html_content)
            )
            
            if message.text_content:
                mail.plain_text_content = PlainTextContent(message.text_content)
            
            if message.reply_to:
                mail.reply_to = message.reply_to
            
            # Add template data if using dynamic templates
            if message.template_id:
                mail.template_id = message.template_id
                if message.template_data:
                    mail.dynamic_template_data = message.template_data
            
            # Send email
            response = self.client.send(mail)
            
            # Parse response
            if response.status_code in [200, 201, 202]:
                message_id = response.headers.get('X-Message-Id')
                logger.info(f"Email sent successfully via SendGrid: {message_id}")
                return EmailResult(
                    success=True,
                    message_id=message_id,
                    provider="SendGrid"
                )
            else:
                error_msg = f"SendGrid API error: {response.status_code} - {response.body}"
                logger.error(error_msg)
                return EmailResult(
                    success=False,
                    error=error_msg,
                    provider="SendGrid"
                )
                
        except Exception as e:
            error_msg = f"SendGrid send error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return EmailResult(
                success=False,
                error=error_msg,
                provider="SendGrid"
            )
    
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails via SendGrid"""
        results = []
        for message in messages:
            result = await self.send_email(message)
            results.append(result)
        return results
    
    def is_healthy(self) -> bool:
        """Check SendGrid health by testing API key"""
        try:
            # Test with a simple API call
            response = self.client.user.get()
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"SendGrid health check failed: {e}")
            return False
