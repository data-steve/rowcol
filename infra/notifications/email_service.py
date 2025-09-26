"""
Email Service Infrastructure

Provides email delivery services for notifications, digests, and alerts.
Supports multiple email providers with fallback and retry logic.

Key Features:
- Multi-provider email delivery (SendGrid, AWS SES, SMTP)
- Template-based email generation
- Retry logic with exponential backoff
- Delivery tracking and analytics
- Business isolation for multi-tenant usage
"""

import logging
import smtplib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from infra.utils.error_handling import retry_with_backoff, handle_integration_errors, ErrorContext
from common.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)


class EmailProvider(Enum):
    """Supported email providers."""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"


@dataclass
class EmailResult:
    """Result of email delivery attempt."""
    success: bool
    message_id: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class EmailTemplate:
    """Email template configuration."""
    subject: str
    html_body: str
    text_body: str
    sender_name: str = "Oodaloo"
    sender_email: str = "noreply@oodaloo.com"


class EmailService:
    """
    Email delivery service with multi-provider support.
    
    Provides reliable email delivery with fallback providers,
    retry logic, and template-based email generation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email service with configuration.
        
        Args:
            config: Email service configuration
        """
        self.config = config
        self.providers = self._initialize_providers()
        self.templates = self._load_templates()
        
        logger.info(f"EmailService initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self) -> Dict[EmailProvider, Dict[str, Any]]:
        """Initialize available email providers."""
        providers = {}
        
        # SMTP provider
        if self.config.get("smtp", {}).get("enabled", False):
            providers[EmailProvider.SMTP] = self.config["smtp"]
        
        # SendGrid provider
        if self.config.get("sendgrid", {}).get("enabled", False):
            providers[EmailProvider.SENDGRID] = self.config["sendgrid"]
        
        # AWS SES provider
        if self.config.get("aws_ses", {}).get("enabled", False):
            providers[EmailProvider.AWS_SES] = self.config["aws_ses"]
        
        return providers
    
    def _load_templates(self) -> Dict[str, EmailTemplate]:
        """Load email templates."""
        return {
            "digest": EmailTemplate(
                subject="Your Cash Runway Digest - {business_name}",
                html_body=self._get_digest_html_template(),
                text_body=self._get_digest_text_template(),
                sender_name="Oodaloo Runway"
            ),
            "alert": EmailTemplate(
                subject="Alert: {alert_type} - {business_name}",
                html_body=self._get_alert_html_template(),
                text_body=self._get_alert_text_template(),
                sender_name="Oodaloo Alerts"
            ),
            "welcome": EmailTemplate(
                subject="Welcome to Oodaloo - {business_name}",
                html_body=self._get_welcome_html_template(),
                text_body=self._get_welcome_text_template(),
                sender_name="Oodaloo Team"
            )
        }
    
    @retry_with_backoff(max_attempts=3, base_delay=1.0, exponential_base=2.0)
    @handle_integration_errors(context=ErrorContext.EXTERNAL_SERVICE)
    async def send_email(
        self,
        to_email: str,
        template_name: str,
        template_vars: Dict[str, Any],
        provider: Optional[EmailProvider] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> EmailResult:
        """
        Send email using specified template and provider.
        
        Args:
            to_email: Recipient email address
            template_name: Name of email template
            template_vars: Variables for template substitution
            provider: Specific provider to use (default: auto-select)
            attachments: Optional file attachments
            
        Returns:
            EmailResult with delivery status
        """
        try:
            # Get template
            template = self.templates.get(template_name)
            if not template:
                raise EmailDeliveryError(f"Template '{template_name}' not found")
            
            # Substitute template variables
            subject = template.subject.format(**template_vars)
            html_body = template.html_body.format(**template_vars)
            text_body = template.text_body.format(**template_vars)
            
            # Select provider
            if provider and provider in self.providers:
                selected_provider = provider
            else:
                selected_provider = self._select_best_provider()
            
            # Send email
            if selected_provider == EmailProvider.SMTP:
                return await self._send_via_smtp(
                    to_email, subject, html_body, text_body, 
                    template.sender_name, template.sender_email, attachments
                )
            elif selected_provider == EmailProvider.SENDGRID:
                return await self._send_via_sendgrid(
                    to_email, subject, html_body, text_body, 
                    template.sender_name, template.sender_email, attachments
                )
            elif selected_provider == EmailProvider.AWS_SES:
                return await self._send_via_aws_ses(
                    to_email, subject, html_body, text_body, 
                    template.sender_name, template.sender_email, attachments
                )
            else:
                raise EmailDeliveryError("No email providers available")
                
        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            return EmailResult(success=False, error=str(e))
    
    async def send_digest_email(
        self,
        to_email: str,
        business_name: str,
        digest_data: Dict[str, Any]
    ) -> EmailResult:
        """
        Send runway digest email.
        
        Args:
            to_email: Recipient email address
            business_name: Business name for personalization
            digest_data: Runway calculation data
            
        Returns:
            EmailResult with delivery status
        """
        template_vars = {
            "business_name": business_name,
            "runway_days": digest_data.get("runway_days", 0),
            "cash_position": digest_data.get("cash", 0),
            "ar_overdue": digest_data.get("ar_overdue", 0),
            "ap_due_soon": digest_data.get("ap_due_soon", 0),
            "burn_rate": digest_data.get("burn_rate", 0),
            "net_position": digest_data.get("net_position", 0),
            "date": datetime.now().strftime("%B %d, %Y")
        }
        
        return await self.send_email(
            to_email=to_email,
            template_name="digest",
            template_vars=template_vars
        )
    
    async def send_alert_email(
        self,
        to_email: str,
        business_name: str,
        alert_type: str,
        alert_message: str,
        severity: str = "medium"
    ) -> EmailResult:
        """
        Send alert email.
        
        Args:
            to_email: Recipient email address
            business_name: Business name for personalization
            alert_type: Type of alert
            alert_message: Alert message content
            severity: Alert severity level
            
        Returns:
            EmailResult with delivery status
        """
        template_vars = {
            "business_name": business_name,
            "alert_type": alert_type,
            "alert_message": alert_message,
            "severity": severity,
            "date": datetime.now().strftime("%B %d, %Y at %I:%M %p")
        }
        
        return await self.send_email(
            to_email=to_email,
            template_name="alert",
            template_vars=template_vars
        )
    
    def _select_best_provider(self) -> EmailProvider:
        """Select the best available email provider."""
        # Priority order: SendGrid > AWS SES > SMTP
        if EmailProvider.SENDGRID in self.providers:
            return EmailProvider.SENDGRID
        elif EmailProvider.AWS_SES in self.providers:
            return EmailProvider.AWS_SES
        elif EmailProvider.SMTP in self.providers:
            return EmailProvider.SMTP
        else:
            raise EmailDeliveryError("No email providers configured")
    
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        sender_name: str,
        sender_email: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> EmailResult:
        """Send email via SMTP."""
        smtp_config = self.providers[EmailProvider.SMTP]
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add text and HTML parts
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Add attachments if any
        if attachments:
            for attachment in attachments:
                self._add_attachment(msg, attachment)
        
        # Send email
        try:
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()
                if smtp_config.get('username'):
                    server.login(smtp_config['username'], smtp_config['password'])
                
                server.send_message(msg)
                
            return EmailResult(
                success=True,
                message_id=f"smtp_{datetime.now().timestamp()}",
                provider="smtp"
            )
        except Exception as e:
            raise EmailDeliveryError(f"SMTP delivery failed: {e}")
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        sender_name: str,
        sender_email: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> EmailResult:
        """Send email via SendGrid API."""
        # TODO: Implement SendGrid API integration
        # This would use the SendGrid Python SDK
        raise EmailDeliveryError("SendGrid integration not yet implemented")
    
    async def _send_via_aws_ses(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        sender_name: str,
        sender_email: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> EmailResult:
        """Send email via AWS SES API."""
        # TODO: Implement AWS SES API integration
        # This would use boto3 for SES
        raise EmailDeliveryError("AWS SES integration not yet implemented")
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message."""
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment['content'])
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {attachment["filename"]}'
        )
        msg.attach(part)
    
    def _get_digest_html_template(self) -> str:
        """Get HTML template for digest emails."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Cash Runway Digest</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .metric { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Cash Runway Digest</h1>
                    <p>{business_name} - {date}</p>
                </div>
                <div class="content">
                    <div class="metric">
                        <h3>Current Runway</h3>
                        <div class="metric-value">{runway_days} days</div>
                    </div>
                    <div class="metric">
                        <h3>Cash Position</h3>
                        <div class="metric-value">${cash_position:,.2f}</div>
                    </div>
                    <div class="metric">
                        <h3>AR Overdue</h3>
                        <div class="metric-value">${ar_overdue:,.2f}</div>
                    </div>
                    <div class="metric">
                        <h3>AP Due Soon</h3>
                        <div class="metric-value">${ap_due_soon:,.2f}</div>
                    </div>
                    <div class="metric">
                        <h3>Monthly Burn Rate</h3>
                        <div class="metric-value">${burn_rate:,.2f}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated message from Oodaloo. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_digest_text_template(self) -> str:
        """Get text template for digest emails."""
        return """
        Cash Runway Digest - {business_name}
        {date}
        
        Current Runway: {runway_days} days
        Cash Position: ${cash_position:,.2f}
        AR Overdue: ${ar_overdue:,.2f}
        AP Due Soon: ${ap_due_soon:,.2f}
        Monthly Burn Rate: ${burn_rate:,.2f}
        
        This is an automated message from Oodaloo.
        """
    
    def _get_alert_html_template(self) -> str:
        """Get HTML template for alert emails."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Alert: {alert_type}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #e74c3c; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .alert { background: white; padding: 20px; border-radius: 5px; border-left: 4px solid #e74c3c; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Alert: {alert_type}</h1>
                    <p>{business_name} - {date}</p>
                </div>
                <div class="content">
                    <div class="alert">
                        <h3>Alert Details</h3>
                        <p><strong>Severity:</strong> {severity}</p>
                        <p><strong>Message:</strong> {alert_message}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated alert from Oodaloo. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_alert_text_template(self) -> str:
        """Get text template for alert emails."""
        return """
        Alert: {alert_type} - {business_name}
        {date}
        
        Severity: {severity}
        Message: {alert_message}
        
        This is an automated alert from Oodaloo.
        """
    
    def _get_welcome_html_template(self) -> str:
        """Get HTML template for welcome emails."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Oodaloo</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Oodaloo!</h1>
                    <p>{business_name}</p>
                </div>
                <div class="content">
                    <p>Thank you for joining Oodaloo! We're excited to help you manage your cash runway and financial health.</p>
                    <p>You can now access your dashboard and start tracking your business metrics.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from Oodaloo.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_text_template(self) -> str:
        """Get text template for welcome emails."""
        return """
        Welcome to Oodaloo!
        
        {business_name}
        
        Thank you for joining Oodaloo! We're excited to help you manage your cash runway and financial health.
        
        You can now access your dashboard and start tracking your business metrics.
        
        This is an automated message from Oodaloo.
        """



