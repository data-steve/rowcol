"""Mock data provider for TrayService development and testing."""

from typing import Dict, Any, List
from abc import ABC, abstractmethod
import os

class TrayDataProvider(ABC):
    """Abstract base class for tray data providers."""
    
    @abstractmethod
    def get_runway_impact(self, item_type: str) -> Dict[str, Any]:
        """Get runway impact data for a tray item type."""
        pass
    
    @abstractmethod
    def get_action_result(self, action: str, item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get result data for a tray action."""
        pass
    
    @abstractmethod
    def get_priority_weights(self) -> Dict[str, int]:
        """Get priority weights for different tray item types."""
        pass

class MockTrayDataProvider(TrayDataProvider):
    """Mock data provider for development."""
    
    def get_runway_impact(self, item_type: str) -> Dict[str, Any]:
        """Get mock runway impact data."""
        impact_map = {
            "overdue_bill": {"cash_impact": -1500, "days_impact": -2, "urgency": "high"},
            "overdue_invoice": {"cash_impact": 2500, "days_impact": 3, "urgency": "medium"},
            "upcoming_payroll": {"cash_impact": -15000, "days_impact": -7, "urgency": "critical"},
            "bank_reconciliation": {"cash_impact": 0, "days_impact": 0, "urgency": "low"},
            "vendor_duplicate": {"cash_impact": 0, "days_impact": 0, "urgency": "low"}
        }
        
        return impact_map.get(item_type, {"cash_impact": 0, "days_impact": 0, "urgency": "low"})
    
    def get_action_result(self, action: str, item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mock action result data."""
        from datetime import datetime
        
        action_results = {
            "approve_payment": {
                "payment_scheduled": True,
                "amount": data.get("amount", 1500),
                "payment_date": data.get("payment_date", datetime.now().isoformat()),
                "qbo_payment_id": f"mock_payment_{item_id}"
            },
            "schedule_payment": {
                "scheduled": True,
                "scheduled_date": data.get("scheduled_date"),
                "qbo_scheduled_id": f"mock_scheduled_{item_id}"
            },
            "send_reminder": {
                "reminder_sent": True,
                "recipient": data.get("email", "client@example.com"),
                "template": "overdue_invoice_reminder",
                "qbo_activity_id": f"mock_activity_{item_id}"
            },
            "auto_match": {
                "transactions_matched": data.get("transaction_count", 5),
                "match_confidence": 0.95,
                "qbo_reconciliation_id": f"mock_recon_{item_id}"
            },
            "merge_vendors": {
                "vendors_merged": True,
                "primary_vendor_id": data.get("primary_vendor_id"),
                "secondary_vendor_id": data.get("secondary_vendor_id"),
                "qbo_merge_id": f"mock_merge_{item_id}"
            }
        }
        
        return action_results.get(action, {"processed": True, "mock_result": True})
    
    def get_priority_weights(self) -> Dict[str, int]:
        """Get mock priority weights."""
        return {
            "overdue_bill": 35,
            "upcoming_payroll": 40,
            "overdue_invoice": 30,
            "bank_reconciliation": 25,
            "vendor_duplicate": 15,
            "missing_receipt": 10
        }

class ProductionTrayDataProvider(TrayDataProvider):
    """Production data provider that integrates with real QBO."""
    
    def __init__(self, qbo_service=None):
        self.qbo_service = qbo_service
    
    def get_runway_impact(self, item_type: str) -> Dict[str, Any]:
        """Calculate real runway impact based on QBO data."""
        # TODO: Implement real runway impact calculation
        # This would analyze actual account balances, pending payments, etc.
        raise NotImplementedError("Production runway impact calculation not yet implemented")
    
    def get_action_result(self, action: str, item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real actions against QBO."""
        # TODO: Implement real QBO actions
        # This would make actual API calls to QBO
        raise NotImplementedError("Production QBO actions not yet implemented")
    
    def get_priority_weights(self) -> Dict[str, int]:
        """Get priority weights based on business rules."""
        # TODO: Could be configurable per business
        return {
            "overdue_bill": 35,
            "upcoming_payroll": 40,
            "overdue_invoice": 30,
            "bank_reconciliation": 25,
            "vendor_duplicate": 15,
            "missing_receipt": 10
        }

def get_tray_data_provider() -> TrayDataProvider:
    """Factory function to get the appropriate data provider based on environment."""
    use_mock = os.getenv("USE_MOCK_TRAY_DATA", "true").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development" or use_mock:
        return MockTrayDataProvider()
    else:
        # TODO: Initialize with real QBO service
        return ProductionTrayDataProvider()
