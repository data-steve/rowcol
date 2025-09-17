"""
QBO Provider Abstraction for AP Domain

Defines the interface for QBO integration specific to AP operations.
Follows ADR-002 Mock-First Development Strategy.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class QBOAPProvider(ABC):
    """
    Abstract base class for QBO AP operations.
    
    This provider handles QBO operations specific to Accounts Payable:
    - Bill synchronization
    - Vendor management
    - Payment execution
    """
    
    @abstractmethod
    def get_bills(self, since_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Retrieve bills from QBO.
        
        Args:
            since_date: Only fetch bills modified since this date
            
        Returns:
            List of QBO bill data dictionaries
        """
        pass
    
    @abstractmethod
    def get_vendors(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve vendors from QBO.
        
        Args:
            active_only: Only fetch active vendors
            
        Returns:
            List of QBO vendor data dictionaries
        """
        pass
    
    @abstractmethod
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment in QBO.
        
        Args:
            payment_data: Payment details
            
        Returns:
            Created payment data from QBO
        """
        pass
    
    @abstractmethod
    def update_bill_status(self, qbo_bill_id: str, status: str) -> Dict[str, Any]:
        """
        Update bill status in QBO.
        
        Args:
            qbo_bill_id: QBO bill identifier
            status: New status
            
        Returns:
            Updated bill data from QBO
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test QBO API connectivity.
        
        Returns:
            Connection status and company info
        """
        pass
