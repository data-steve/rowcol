"""Data providers for DataIngestionService."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import os
from datetime import datetime

class DataProvider(ABC):
    """Abstract base class for data providers."""
    
    @abstractmethod
    def fetch_transactions(self, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch transaction data from the platform."""
        pass
    
    @abstractmethod
    def test_connection(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Test connection to the platform."""
        pass

class MockDataProvider(DataProvider):
    """Mock data provider for development."""
    
    def fetch_transactions(self, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate mock transaction data for development."""
        # Generate realistic mock data with variety
        mock_transactions = []
        
        # Create different types of transactions
        transaction_types = [
            {"type": "deposit", "base_amount": 2500, "description": "Client payment"},
            {"type": "expense", "base_amount": -500, "description": "Office supplies"},
            {"type": "expense", "base_amount": -1200, "description": "Software subscription"},
            {"type": "deposit", "base_amount": 5000, "description": "Project milestone"},
            {"type": "expense", "base_amount": -800, "description": "Marketing expense"},
        ]
        
        for i in range(20):  # Reasonable number for development
            tx_type = transaction_types[i % len(transaction_types)]
            mock_transactions.append({
                "txn_id": f"MOCK_TXN_{i:04d}",
                "amount": tx_type["base_amount"] + (i * 10),  # Add variation
                "date": f"2025-01-{(i % 28) + 1:02d}",  # Spread across January
                "type": tx_type["type"],
                "description": f"{tx_type['description']} #{i+1}",
                "vendor": f"Vendor_{i % 5 + 1}",  # 5 different vendors
                "category": "Business Expense" if tx_type["type"] == "expense" else "Income"
            })
        
        return mock_transactions
    
    def test_connection(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Mock connection test - always succeeds."""
        return {
            "status": "success",
            "message": "Mock connection successful",
            "mock": True,
            "timestamp": datetime.now().isoformat()
        }

class QBODataProvider(DataProvider):
    """Production QBO data provider."""
    
    def __init__(self):
        self.base_url = "https://sandbox-quickbooks.api.intuit.com/v3/company"
        self.timeout = 30
    
    def fetch_transactions(self, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch real transactions from QBO API."""
        # TODO: Implement real QBO API calls
        # This would make actual HTTP requests to QBO
        raise NotImplementedError("Production QBO data fetching not yet implemented")
    
    def test_connection(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Test real QBO connection."""
        # TODO: Implement real QBO connection test
        raise NotImplementedError("Production QBO connection test not yet implemented")

def get_data_provider() -> DataProvider:
    """Factory function to get the appropriate data provider."""
    use_mock = os.getenv("USE_MOCK_DATA_INGESTION", "true").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development" or use_mock:
        return MockDataProvider()
    else:
        return QBODataProvider()
