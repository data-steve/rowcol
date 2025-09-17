import os
import logging
import json
from typing import List, Dict, Any
from datetime import datetime
from .base import EmailProvider, EmailMessage, EmailResult

logger = logging.getLogger(__name__)

class MockEmailProvider(EmailProvider):
    """Mock email provider for development and testing"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sent_emails = []  # Store sent emails for testing
        self.should_fail = config.get("should_fail", False)  # For testing failures
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Mock send email - logs to console and file"""
        try:
            if self.should_fail:
                return EmailResult(
                    success=False,
                    error="Mock provider configured to fail",
                    provider="Mock"
                )
            
            # Generate mock message ID
            message_id = f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.sent_emails)}"
            
            # Create email record
            email_record = {
                "message_id": message_id,
                "to_email": message.to_email,
                "from_email": message.from_email or self.get_default_from_email(),
                "from_name": message.from_name or self.get_default_from_name(),
                "subject": message.subject,
                "html_content": message.html_content,
                "text_content": message.text_content,
                "timestamp": datetime.now().isoformat(),
                "template_id": message.template_id,
                "template_data": message.template_data
            }
            
            # Store for testing
            self.sent_emails.append(email_record)
            
            # Log to console
            logger.info(
                "📧 MOCK EMAIL SENT",
                extra={
                    "message_id": message_id,
                    "to": message.to_email,
                    "subject": message.subject,
                    "provider": "Mock"
                }
            )
            
            # Save to file for inspection
            log_file = f"logs/mock_emails_{datetime.now().strftime('%Y%m%d')}.json"
            try:
                # Read existing emails
                existing_emails = []
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        existing_emails = json.load(f)
                
                # Append new email
                existing_emails.append(email_record)
                
                # Write back
                with open(log_file, 'w') as f:
                    json.dump(existing_emails, f, indent=2)
                    
                logger.info(f"Email saved to {log_file}")
                
            except Exception as e:
                logger.warning(f"Could not save email to file: {e}")
            
            return EmailResult(
                success=True,
                message_id=message_id,
                provider="Mock"
            )
            
        except Exception as e:
            error_msg = f"Mock provider error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return EmailResult(
                success=False,
                error=error_msg,
                provider="Mock"
            )
    
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails via mock provider"""
        results = []
        for message in messages:
            result = await self.send_email(message)
            results.append(result)
        return results
    
    def is_healthy(self) -> bool:
        """Mock provider is always healthy unless configured to fail"""
        return not self.should_fail
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails (for testing)"""
        return self.sent_emails.copy()
    
    def clear_sent_emails(self):
        """Clear sent emails (for testing)"""
        self.sent_emails.clear()
