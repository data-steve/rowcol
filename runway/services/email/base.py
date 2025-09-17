from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EmailMessage:
    """Email message data structure"""
    to_email: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None

@dataclass
class EmailResult:
    """Email send result"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    provider: Optional[str] = None

class EmailProvider(ABC):
    """Abstract base class for email providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send a single email"""
        pass
    
    @abstractmethod
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails"""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if provider is healthy and can send emails"""
        pass
    
    def get_default_from_email(self) -> str:
        """Get default from email address"""
        return self.config.get("default_from_email", "noreply@oodaloo.com")
    
    def get_default_from_name(self) -> str:
        """Get default from name"""
        return self.config.get("default_from_name", "Oodaloo")
