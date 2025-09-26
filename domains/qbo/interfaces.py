"""
QBO Infrastructure Interfaces - Dependency Inversion

These interfaces define contracts between infrastructure and domain layers,
breaking circular dependencies through dependency inversion principle.

Key Principle: Infrastructure defines interfaces, domain implements them.

NOTE: Currently commented out because QBO is in domains/ and doesn't need
these interfaces. Save for future if we move QBO back to infra/.
"""

# from abc import ABC, abstractmethod
# from typing import Optional, Dict, Any
# from datetime import datetime


# class QBOIntegrationRepository(ABC):
#     """Interface for QBO integration data operations."""
#     
#     @abstractmethod
#     def get_integration(self, business_id: str) -> Optional[Dict[str, Any]]:
#         """Get QBO integration for a business."""
#         pass
#     
#     @abstractmethod
#     def save_integration(self, business_id: str, integration_data: Dict[str, Any]) -> None:
#         """Save QBO integration data."""
#         pass
#     
#     @abstractmethod
#     def update_integration(self, business_id: str, updates: Dict[str, Any]) -> None:
#         """Update QBO integration data."""
#         pass
#     
#     @abstractmethod
#     def delete_integration(self, business_id: str) -> None:
#         """Delete QBO integration."""
#         pass


# class QBOAuthServiceInterface(ABC):
#     """Interface for QBO authentication operations."""
#     
#     @abstractmethod
#     def get_auth_url(self, business_id: str, state: str) -> str:
#         """Get QBO OAuth authorization URL."""
#         pass
#     
#     @abstractmethod
#     def exchange_code_for_tokens(self, authorization_code: str, realm_id: str) -> Dict[str, Any]:
#         """Exchange authorization code for access/refresh tokens."""
#         pass
#     
#     @abstractmethod
#     def refresh_access_token(self, business_id: str) -> Optional[str]:
#         """Refresh expired access token."""
#         pass
#     
#     @abstractmethod
#     def is_connected(self, business_id: str) -> bool:
#         """Check if QBO is connected for a business."""
#         pass
#     
#     @abstractmethod
#     def disconnect(self, business_id: str) -> None:
#         """Disconnect QBO integration."""
#         pass
