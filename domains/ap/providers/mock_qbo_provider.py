"""
Mock QBO Provider for AP Domain

Provides realistic mock data for QBO AP operations during development.
Follows ADR-002 Mock-First Development Strategy.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import random

from .qbo_provider import QBOAPProvider


class MockQBOAPProvider(QBOAPProvider):
    """
    Mock implementation of QBO AP provider.
    
    Generates realistic bill and vendor data for development and testing.
    Simulates API delays and occasional errors for realistic behavior.
    """
    
    def __init__(self, business_id: str):
        self.business_id = business_id
        self._bills_cache = None
        self._vendors_cache = None
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize realistic mock data for the business."""
        # Create consistent mock vendors
        self._mock_vendors = [
            {
                "Id": "1",
                "Name": "HubSpot",
                "DisplayName": "HubSpot",
                "Active": True,
                "VendorRef": {"value": "1", "name": "HubSpot"},
                "CompanyName": "HubSpot, Inc.",
                "Terms": "Net 30",
                "AcctNum": "VENDOR001"
            },
            {
                "Id": "2", 
                "Name": "Google Workspace",
                "DisplayName": "Google Workspace",
                "Active": True,
                "VendorRef": {"value": "2", "name": "Google Workspace"},
                "CompanyName": "Google LLC",
                "Terms": "Due on receipt",
                "AcctNum": "VENDOR002"
            },
            {
                "Id": "3",
                "Name": "Office Depot",
                "DisplayName": "Office Depot",
                "Active": True,
                "VendorRef": {"value": "3", "name": "Office Depot"},
                "CompanyName": "Office Depot, Inc.",
                "Terms": "Net 15",
                "AcctNum": "VENDOR003"
            },
            {
                "Id": "4",
                "Name": "Adobe Creative Cloud",
                "DisplayName": "Adobe Creative Cloud",
                "Active": True,
                "VendorRef": {"value": "4", "name": "Adobe Creative Cloud"},
                "CompanyName": "Adobe Inc.",
                "Terms": "Net 30",
                "AcctNum": "VENDOR004"
            },
            {
                "Id": "5",
                "Name": "Slack Technologies",
                "DisplayName": "Slack Technologies", 
                "Active": True,
                "VendorRef": {"value": "5", "name": "Slack Technologies"},
                "CompanyName": "Slack Technologies, Inc.",
                "Terms": "Due on receipt",
                "AcctNum": "VENDOR005"
            }
        ]
        
        # Create realistic mock bills
        self._mock_bills = self._generate_mock_bills()
    
    def _generate_mock_bills(self) -> List[Dict[str, Any]]:
        """Generate realistic mock bills with variety."""
        bills = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        # Recurring monthly bills
        recurring_bills = [
            {"vendor_id": "1", "amount": 1200.00, "description": "HubSpot Professional"},
            {"vendor_id": "2", "amount": 144.00, "description": "Google Workspace Business"},
            {"vendor_id": "4", "amount": 79.99, "description": "Adobe Creative Cloud Team"},
            {"vendor_id": "5", "amount": 96.00, "description": "Slack Pro Plan"}
        ]
        
        # Generate bills with realistic patterns
        for i, bill_template in enumerate(recurring_bills):
            vendor = next(v for v in self._mock_vendors if v["Id"] == bill_template["vendor_id"])
            
            # Create bill for this month
            bill_date = base_date + timedelta(days=i * 2)  # Spread bills across month
            due_date = bill_date + timedelta(days=30 if vendor["Terms"] == "Net 30" else 15)
            
            bill = {
                "Id": str(100 + i),
                "DocNumber": f"BILL-{2025}-{i+1:04d}",
                "TxnDate": bill_date.strftime("%Y-%m-%d"),
                "DueDate": due_date.strftime("%Y-%m-%d"),
                "TotalAmt": bill_template["amount"],
                "Balance": bill_template["amount"],  # Unpaid
                "VendorRef": {"value": bill_template["vendor_id"], "name": vendor["Name"]},
                "Memo": bill_template["description"],
                "SyncToken": "1",
                "MetaData": {
                    "CreateTime": bill_date.isoformat(),
                    "LastUpdatedTime": bill_date.isoformat()
                },
                "Line": [{
                    "Amount": bill_template["amount"],
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {"value": "6000", "name": "Software Subscriptions"}
                    }
                }]
            }
            bills.append(bill)
        
        # Add some one-time expenses
        one_time_bills = [
            {"vendor_id": "3", "amount": 234.56, "description": "Office supplies - Q1 order"},
            {"vendor_id": "3", "amount": 89.99, "description": "Printer paper and toner"}
        ]
        
        for i, bill_template in enumerate(one_time_bills):
            vendor = next(v for v in self._mock_vendors if v["Id"] == bill_template["vendor_id"])
            bill_date = base_date + timedelta(days=10 + i * 5)
            due_date = bill_date + timedelta(days=15)  # Office Depot is Net 15
            
            bill = {
                "Id": str(200 + i),
                "DocNumber": f"BILL-{2025}-{200 + i:04d}",
                "TxnDate": bill_date.strftime("%Y-%m-%d"),
                "DueDate": due_date.strftime("%Y-%m-%d"),
                "TotalAmt": bill_template["amount"],
                "Balance": bill_template["amount"],
                "VendorRef": {"value": bill_template["vendor_id"], "name": vendor["Name"]},
                "Memo": bill_template["description"],
                "SyncToken": "1",
                "MetaData": {
                    "CreateTime": bill_date.isoformat(),
                    "LastUpdatedTime": bill_date.isoformat()
                },
                "Line": [{
                    "Amount": bill_template["amount"],
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {"value": "6200", "name": "Office Supplies"}
                    }
                }]
            }
            bills.append(bill)
        
        return bills
    
    def get_bills(self, since_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Return mock bills, optionally filtered by date."""
        # Simulate API delay
        import time
        time.sleep(0.1)
        
        bills = self._mock_bills.copy()
        
        if since_date:
            # Filter bills by date
            filtered_bills = []
            for bill in bills:
                bill_date = datetime.strptime(bill["TxnDate"], "%Y-%m-%d")
                if bill_date >= since_date:
                    filtered_bills.append(bill)
            bills = filtered_bills
        
        # Simulate occasional API errors (5% chance)
        if random.random() < 0.05:
            raise Exception("Mock QBO API error: Rate limit exceeded")
        
        return bills
    
    def get_vendors(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Return mock vendors."""
        # Simulate API delay
        import time
        time.sleep(0.05)
        
        vendors = self._mock_vendors.copy()
        
        if active_only:
            vendors = [v for v in vendors if v.get("Active", True)]
        
        return vendors
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock payment creation."""
        # Simulate API delay
        import time
        time.sleep(0.2)
        
        # Simulate payment processing
        payment_id = str(uuid.uuid4())
        
        mock_payment = {
            "Id": payment_id,
            "TxnDate": datetime.utcnow().strftime("%Y-%m-%d"),
            "TotalAmt": payment_data.get("TotalAmt", 0),
            "VendorRef": payment_data.get("VendorRef"),
            "CheckPayment": {
                "BankAccountRef": {"value": "1", "name": "Checking"},
                "PrintStatus": "NotSet"
            },
            "SyncToken": "1",
            "MetaData": {
                "CreateTime": datetime.utcnow().isoformat(),
                "LastUpdatedTime": datetime.utcnow().isoformat()
            }
        }
        
        # Simulate occasional payment failures (2% chance)
        if random.random() < 0.02:
            raise Exception("Mock payment error: Insufficient funds")
        
        return mock_payment
    
    def update_bill_status(self, qbo_bill_id: str, status: str) -> Dict[str, Any]:
        """Mock bill status update."""
        # Simulate API delay
        import time
        time.sleep(0.1)
        
        # Find the bill in our mock data
        bill = next((b for b in self._mock_bills if b["Id"] == qbo_bill_id), None)
        if not bill:
            raise Exception(f"Mock QBO error: Bill {qbo_bill_id} not found")
        
        # Update bill status
        bill["Balance"] = 0.0 if status == "paid" else bill["TotalAmt"]
        bill["SyncToken"] = str(int(bill["SyncToken"]) + 1)
        bill["MetaData"]["LastUpdatedTime"] = datetime.utcnow().isoformat()
        
        return bill
    
    def test_connection(self) -> Dict[str, Any]:
        """Mock connection test."""
        # Simulate API delay
        import time
        time.sleep(0.05)
        
        return {
            "status": "connected",
            "company_info": {
                "CompanyName": f"Mock Company {self.business_id}",
                "Country": "US",
                "Id": "1",
                "QBORealmID": f"mock_realm_{self.business_id}"
            },
            "api_version": "v3",
            "last_sync": datetime.utcnow().isoformat()
        }
    
    def get_bill_by_id(self, qbo_bill_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific bill by QBO ID."""
        return next((b for b in self._mock_bills if b["Id"] == qbo_bill_id), None)
    
    def simulate_webhook_event(self, entity_type: str, entity_id: str, operation: str) -> Dict[str, Any]:
        """Simulate a QBO webhook event for testing."""
        return {
            "eventNotifications": [{
                "realmId": f"mock_realm_{self.business_id}",
                "dataChangeEvent": {
                    "entities": [{
                        "name": entity_type,
                        "id": entity_id,
                        "operation": operation,
                        "lastUpdated": datetime.utcnow().isoformat()
                    }]
                }
            }]
        }
