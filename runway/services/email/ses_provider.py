import os
import logging
import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from .base import EmailProvider, EmailMessage, EmailResult

logger = logging.getLogger(__name__)

class SESProvider(EmailProvider):
    """Amazon SES email provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # AWS credentials from config or environment
        aws_access_key = config.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = config.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = config.get("aws_region", "us-east-1")
        
        # Initialize SES client
        self.client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send a single email via Amazon SES"""
        try:
            # Build SES message
            email_params = {
                'Source': f"{message.from_name or self.get_default_from_name()} <{message.from_email or self.get_default_from_email()}>",
                'Destination': {
                    'ToAddresses': [message.to_email]
                },
                'Message': {
                    'Subject': {
                        'Data': message.subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': message.html_content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            }
            
            # Add text content if provided
            if message.text_content:
                email_params['Message']['Body']['Text'] = {
                    'Data': message.text_content,
                    'Charset': 'UTF-8'
                }
            
            # Add reply-to if provided
            if message.reply_to:
                email_params['ReplyToAddresses'] = [message.reply_to]
            
            # Send email
            response = self.client.send_email(**email_params)
            
            message_id = response.get('MessageId')
            logger.info(f"Email sent successfully via SES: {message_id}")
            return EmailResult(
                success=True,
                message_id=message_id,
                provider="SES"
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = f"SES ClientError {error_code}: {e.response['Error']['Message']}"
            logger.error(error_msg)
            return EmailResult(
                success=False,
                error=error_msg,
                provider="SES"
            )
        except Exception as e:
            error_msg = f"SES send error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return EmailResult(
                success=False,
                error=error_msg,
                provider="SES"
            )
    
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails via SES"""
        results = []
        for message in messages:
            result = await self.send_email(message)
            results.append(result)
        return results
    
    def is_healthy(self) -> bool:
        """Check SES health by testing send quota"""
        try:
            response = self.client.get_send_quota()
            return 'SentLast24Hours' in response
        except Exception as e:
            logger.warning(f"SES health check failed: {e}")
            return False
