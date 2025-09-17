import os
import logging
from typing import List, Optional, Dict, Any
from .base import EmailProvider, EmailMessage, EmailResult
from .sendgrid_provider import SendGridProvider
from .ses_provider import SESProvider
from .mock_provider import MockEmailProvider

logger = logging.getLogger(__name__)

class EmailService:
    """
    Email service with provider abstraction and fallback support.
    Primary: SendGrid, Fallback: Amazon SES
    """
    
    def __init__(self):
        self.providers: List[EmailProvider] = []
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup email providers based on configuration"""
        
        # Check if we're in development/testing mode
        environment = os.getenv("ENVIRONMENT", "development")
        use_mock_email = os.getenv("USE_MOCK_EMAIL", "true").lower() == "true"
        
        if environment == "development" or use_mock_email:
            # Use mock provider for development
            mock_config = {
                "default_from_email": os.getenv("DEFAULT_FROM_EMAIL", "digest@oodaloo.com"),
                "default_from_name": os.getenv("DEFAULT_FROM_NAME", "Oodaloo Runway"),
                "should_fail": False
            }
            
            try:
                mock_provider = MockEmailProvider(mock_config)
                self.providers.append(mock_provider)
                logger.info("Mock email provider initialized for development")
            except Exception as e:
                logger.error(f"Failed to initialize Mock provider: {e}")
        
        else:
            # Production providers: SendGrid + SES fallback
            
            # Primary provider: SendGrid
            sendgrid_config = {
                "api_key": os.getenv("SENDGRID_API_KEY"),
                "default_from_email": os.getenv("DEFAULT_FROM_EMAIL", "digest@oodaloo.com"),
                "default_from_name": os.getenv("DEFAULT_FROM_NAME", "Oodaloo Runway")
            }
            
            if sendgrid_config["api_key"]:
                try:
                    sendgrid_provider = SendGridProvider(sendgrid_config)
                    self.providers.append(sendgrid_provider)
                    logger.info("SendGrid provider initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize SendGrid provider: {e}")
            
            # Fallback provider: SES
            ses_config = {
                "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
                "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "aws_region": os.getenv("AWS_REGION", "us-east-1"),
                "default_from_email": os.getenv("DEFAULT_FROM_EMAIL", "digest@oodaloo.com"),
                "default_from_name": os.getenv("DEFAULT_FROM_NAME", "Oodaloo Runway")
            }
            
            if ses_config["aws_access_key_id"] and ses_config["aws_secret_access_key"]:
                try:
                    ses_provider = SESProvider(ses_config)
                    self.providers.append(ses_provider)
                    logger.info("SES provider initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize SES provider: {e}")
        
        if not self.providers:
            logger.warning("No email providers configured! Email sending will fail.")
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send email with automatic fallback"""
        if not self.providers:
            return EmailResult(
                success=False,
                error="No email providers available",
                provider="None"
            )
        
        last_error = None
        
        for provider in self.providers:
            if not provider.is_healthy():
                logger.warning(f"Provider {provider.name} is unhealthy, skipping")
                continue
            
            try:
                result = await provider.send_email(message)
                if result.success:
                    return result
                else:
                    last_error = result.error
                    logger.warning(f"Provider {provider.name} failed: {result.error}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Provider {provider.name} error: {e}", exc_info=True)
        
        return EmailResult(
            success=False,
            error=f"All providers failed. Last error: {last_error}",
            provider="All"
        )
    
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails with fallback"""
        results = []
        for message in messages:
            result = await self.send_email(message)
            results.append(result)
        return results
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get health status of all providers"""
        return {
            provider.name: provider.is_healthy() 
            for provider in self.providers
        }
    
    async def send_digest_email(
        self, 
        to_email: str, 
        business_name: str,
        digest_data: Dict[str, Any]
    ) -> EmailResult:
        """Send weekly digest email with template"""
        
        # Generate digest HTML content
        html_content = self._generate_digest_html(business_name, digest_data)
        text_content = self._generate_digest_text(business_name, digest_data)
        
        message = EmailMessage(
            to_email=to_email,
            subject=f"Weekly Runway Digest - {business_name}",
            html_content=html_content,
            text_content=text_content
        )
        
        return await self.send_email(message)
    
    def _generate_digest_html(self, business_name: str, data: Dict[str, Any]) -> str:
        """Generate HTML content for digest email"""
        runway_days = data.get('runway_days', 0)
        cash = data.get('cash', 0)
        ar_overdue = data.get('ar_overdue', 0)
        ap_due_soon = data.get('ap_due_soon', 0)
        
        # Determine runway status color
        if runway_days >= 60:
            status_color = "#10B981"  # Green
            status_text = "Healthy"
        elif runway_days >= 30:
            status_color = "#F59E0B"  # Yellow
            status_text = "Caution"
        else:
            status_color = "#EF4444"  # Red
            status_text = "Critical"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Weekly Runway Digest</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: #1f2937; color: white; padding: 24px; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 24px; }}
                .metric {{ display: flex; justify-content: space-between; align-items: center; padding: 16px; margin: 8px 0; background: #f9fafb; border-radius: 6px; }}
                .metric-label {{ font-weight: 600; color: #374151; }}
                .metric-value {{ font-size: 18px; font-weight: 700; }}
                .status {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; color: white; }}
                .footer {{ background: #f9fafb; padding: 16px 24px; border-radius: 0 0 8px 8px; font-size: 14px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 24px;">Weekly Runway Digest</h1>
                    <p style="margin: 8px 0 0 0; opacity: 0.9;">{business_name}</p>
                </div>
                
                <div class="content">
                    <div class="metric">
                        <span class="metric-label">Cash Runway</span>
                        <div>
                            <span class="metric-value" style="color: {status_color};">{runway_days:.0f} days</span>
                            <span class="status" style="background-color: {status_color};">{status_text}</span>
                        </div>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Available Cash</span>
                        <span class="metric-value" style="color: #10B981;">${cash:,.2f}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">AR Overdue (30+ days)</span>
                        <span class="metric-value" style="color: #F59E0B;">${ar_overdue:,.2f}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">AP Due Soon (14 days)</span>
                        <span class="metric-value" style="color: #EF4444;">${ap_due_soon:,.2f}</span>
                    </div>
                    
                    <div style="margin-top: 24px; padding: 16px; background: #eff6ff; border-radius: 6px; border-left: 4px solid #3b82f6;">
                        <p style="margin: 0; font-weight: 600; color: #1e40af;">Next Steps:</p>
                        <ul style="margin: 8px 0 0 0; color: #1e40af;">
                            {"<li>Review overdue AR and send reminders</li>" if ar_overdue > 0 else ""}
                            {"<li>Schedule upcoming bill payments</li>" if ap_due_soon > 0 else ""}
                            {"<li>Consider cash flow optimization</li>" if runway_days < 60 else ""}
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 0;">This digest was generated by Oodaloo Runway. <a href="#" style="color: #3b82f6;">View in app</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_digest_text(self, business_name: str, data: Dict[str, Any]) -> str:
        """Generate text content for digest email"""
        runway_days = data.get('runway_days', 0)
        cash = data.get('cash', 0)
        ar_overdue = data.get('ar_overdue', 0)
        ap_due_soon = data.get('ap_due_soon', 0)
        
        return f"""
Weekly Runway Digest - {business_name}

Cash Runway: {runway_days:.0f} days
Available Cash: ${cash:,.2f}
AR Overdue (30+ days): ${ar_overdue:,.2f}
AP Due Soon (14 days): ${ap_due_soon:,.2f}

Next Steps:
{"- Review overdue AR and send reminders" if ar_overdue > 0 else ""}
{"- Schedule upcoming bill payments" if ap_due_soon > 0 else ""}
{"- Consider cash flow optimization" if runway_days < 60 else ""}

Generated by Oodaloo Runway
        """
