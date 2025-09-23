"""
QBO API Provider - Production QBO API Integration

This is the PRODUCTION QBO integration that makes real API calls.
Mock behavior is handled externally via dependency injection (ADR-002).

Key Responsibilities:
- Make authenticated QBO API calls
- Handle QBO-specific data transformations
- Manage QBO API rate limits and errors
- Return standardized data structures

NOT responsible for:
- Database operations (use domain services)
- Business logic (use domain services)  
- Mock data (handled by test providers)
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session

from domains.integrations.qbo.qbo_auth import qbo_auth
from common.exceptions import IntegrationError

logger = logging.getLogger(__name__)


class QBOAPIProvider:
    """
    Production QBO API provider that makes real API calls.
    
    This class handles ONLY QBO API communication. All business logic
    and database operations are handled by domain services.
    """
    
    def __init__(self, business_id: str, realm_id: str, db: Session):
        self.business_id = business_id
        self.realm_id = realm_id
        self.db = db
        self.base_url = self._get_base_url()
        
    def _get_base_url(self) -> str:
        """Get QBO API base URL based on environment."""
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            return "https://quickbooks.api.intuit.com/v3/company"
        else:
            return "https://sandbox-quickbooks.api.intuit.com/v3/company"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _make_api_call(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated QBO API call with retry logic."""
        # Get valid access token
        access_token = qbo_auth.get_valid_token(self.business_id, self.db)
        if not access_token:
            raise IntegrationError(f"No valid QBO access token for business {self.business_id}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}/{self.realm_id}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params or {})
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"QBO API call failed: {e.response.status_code} - {e.response.text}")
            raise IntegrationError(f"QBO API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"QBO API call failed: {e}")
            raise IntegrationError(f"QBO API call failed: {str(e)}")
    
    async def get_bills(self, due_days: int = 30) -> List[Dict[str, Any]]:
        """Get bills from QBO API."""
        # Calculate date filter
        due_date = (datetime.now() + timedelta(days=due_days)).strftime('%Y-%m-%d')
        
        params = {
            "query": f"SELECT * FROM Bill WHERE DueDate <= '{due_date}' AND Balance > '0'",
            "minorversion": "65"
        }
        
        response = await self._make_api_call("query", params=params)
        
        # Transform QBO response to standardized format
        bills_data = response.get("QueryResponse", {}).get("Bill", [])
        
        return [
            {
                "qbo_id": bill["Id"],
                "vendor_ref": bill.get("VendorRef", {}),
                "amount": float(bill.get("TotalAmt", 0)),
                "due_date": bill.get("DueDate"),
                "txn_date": bill.get("TxnDate"),
                "balance": float(bill.get("Balance", 0)),
                "doc_number": bill.get("DocNumber"),
                "memo": bill.get("Memo"),
                "sync_token": bill.get("SyncToken")
            }
            for bill in bills_data
        ]
    
    async def get_invoices(self, aging_days: int = 30) -> List[Dict[str, Any]]:
        """Get invoices from QBO API."""
        # Calculate date filter for aging
        aging_date = (datetime.now() - timedelta(days=aging_days)).strftime('%Y-%m-%d')
        
        params = {
            "query": f"SELECT * FROM Invoice WHERE DueDate <= '{aging_date}' AND Balance > '0'",
            "minorversion": "65"
        }
        
        response = await self._make_api_call("query", params=params)
        
        # Transform QBO response to standardized format
        invoices_data = response.get("QueryResponse", {}).get("Invoice", [])
        
        return [
            {
                "qbo_id": invoice["Id"],
                "customer_ref": invoice.get("CustomerRef", {}),
                "amount": float(invoice.get("TotalAmt", 0)),
                "due_date": invoice.get("DueDate"),
                "txn_date": invoice.get("TxnDate"),
                "balance": float(invoice.get("Balance", 0)),
                "doc_number": invoice.get("DocNumber"),
                "sync_token": invoice.get("SyncToken")
            }
            for invoice in invoices_data
        ]
    
    async def get_vendors(self) -> List[Dict[str, Any]]:
        """Get vendors from QBO API."""
        params = {
            "query": "SELECT * FROM Vendor WHERE Active = true",
            "minorversion": "65"
        }
        
        response = await self._make_api_call("query", params=params)
        
        # Transform QBO response to standardized format
        vendors_data = response.get("QueryResponse", {}).get("Vendor", [])
        
        return [
            {
                "qbo_id": vendor["Id"],
                "name": vendor.get("Name"),
                "display_name": vendor.get("DisplayName"),
                "active": vendor.get("Active", True),
                "balance": float(vendor.get("Balance", 0)),
                "sync_token": vendor.get("SyncToken")
            }
            for vendor in vendors_data
        ]
    
    async def get_customers(self) -> List[Dict[str, Any]]:
        """Get customers from QBO API."""
        params = {
            "query": "SELECT * FROM Customer WHERE Active = true",
            "minorversion": "65"
        }
        
        response = await self._make_api_call("query", params=params)
        
        # Transform QBO response to standardized format
        customers_data = response.get("QueryResponse", {}).get("Customer", [])
        
        return [
            {
                "qbo_id": customer["Id"],
                "name": customer.get("Name"),
                "display_name": customer.get("DisplayName"),
                "active": customer.get("Active", True),
                "balance": float(customer.get("Balance", 0)),
                "sync_token": customer.get("SyncToken")
            }
            for customer in customers_data
        ]
    
    async def get_accounts(self) -> List[Dict[str, Any]]:
        """Get chart of accounts from QBO API."""
        params = {
            "query": "SELECT * FROM Account WHERE AccountType IN ('Bank', 'Other Current Asset')",
            "minorversion": "65"
        }
        
        response = await self._make_api_call("query", params=params)
        
        # Transform QBO response to standardized format
        accounts_data = response.get("QueryResponse", {}).get("Account", [])
        
        return [
            {
                "qbo_id": account["Id"],
                "name": account.get("Name"),
                "account_type": account.get("AccountType"),
                "account_sub_type": account.get("AccountSubType"),
                "current_balance": float(account.get("CurrentBalance", 0)),
                "active": account.get("Active", True),
                "sync_token": account.get("SyncToken")
            }
            for account in accounts_data
        ]
    
    async def get_company_info(self) -> Dict[str, Any]:
        """Get company information from QBO API."""
        response = await self._make_api_call("companyinfo/1")
        
        company_data = response.get("QueryResponse", {}).get("CompanyInfo", [{}])[0]
        
        return {
            "qbo_id": company_data.get("Id"),
            "company_name": company_data.get("CompanyName"),
            "legal_name": company_data.get("LegalName"),
            "country": company_data.get("Country"),
            "fiscal_year_start": company_data.get("FiscalYearStartMonth"),
            "sync_token": company_data.get("SyncToken")
        }




def get_qbo_provider(business_id: str, db: Session, realm_id: str = None) -> QBOAPIProvider:
    """
    Factory function to get QBO provider for real API calls.
    
    Args:
        business_id: Business identifier
        db: Database session
        realm_id: QBO realm/company ID (if None, will be looked up from database)
    
    Returns:
        QBOAPIProvider instance for real QBO API calls
    """
    # If realm_id not provided, look it up (for convenience)
    if realm_id is None:
        realm_id = _get_realm_id_for_business(business_id, db)
    
    # Always use real QBO API provider - no more mocks
    return QBOAPIProvider(business_id, realm_id, db)


def _get_realm_id_for_business(business_id: str, db: Session) -> str:
    """
    Helper function to get realm_id for a business from the database.
    
    This is a convenience function for the factory, but services should
    ideally pass the realm_id explicitly for better performance.
    """
    try:
        from domains.core.models.integration import Integration
        
        integration = db.query(Integration).filter(
            Integration.business_id == business_id,
            Integration.platform == "qbo"
        ).first()
        
        if not integration or not integration.realm_id:
            logger.warning(f"No QBO integration or realm_id found for business {business_id}")
            return "mock_realm"  # Fallback for development
        
        return integration.realm_id
            
    except Exception as e:
        logger.error(f"Failed to lookup realm_id for business {business_id}: {e}")
        return "mock_realm"  # Fallback for development


# Test data for QBO integration testing
QBO_TEST_DATA = {
    "bills": [
        {
            "qbo_id": "1",
            "vendor_ref": {"value": "1", "name": "Office Supplies Co"},
            "amount": 250.00,
            "due_date": "2025-10-01",
            "txn_date": "2025-09-15",
            "balance": 250.00,
            "doc_number": "BILL-001",
            "memo": "Office supplies",
            "sync_token": "0"
        },
        {
            "qbo_id": "2", 
            "vendor_ref": {"value": "2", "name": "Software Solutions Inc"},
            "amount": 1500.00,
            "due_date": "2025-10-15",
            "txn_date": "2025-09-20",
            "balance": 1500.00,
            "doc_number": "BILL-002",
            "memo": "Monthly software license",
            "sync_token": "0"
        }
    ],
    "invoices": [
        {
            "qbo_id": "1",
            "customer_ref": {"value": "1", "name": "Acme Corp"},
            "amount": 5000.00,
            "due_date": "2025-09-01",
            "txn_date": "2025-08-15",
            "balance": 5000.00,
            "doc_number": "INV-001",
            "sync_token": "0"
        },
        {
            "qbo_id": "2",
            "customer_ref": {"value": "2", "name": "Tech Startup LLC"},
            "amount": 2500.00,
            "due_date": "2025-09-15",
            "txn_date": "2025-08-30",
            "balance": 2500.00,
            "doc_number": "INV-002",
            "sync_token": "0"
        }
    ],
    "vendors": [
        {
            "qbo_id": "1",
            "name": "Office Supplies Co",
            "display_name": "Office Supplies Co",
            "active": True,
            "balance": 250.00,
            "sync_token": "0"
        },
        {
            "qbo_id": "2",
            "name": "Software Solutions Inc", 
            "display_name": "Software Solutions Inc",
            "active": True,
            "balance": 1500.00,
            "sync_token": "0"
        }
    ],
    "customers": [
        {
            "qbo_id": "1",
            "name": "Acme Corp",
            "display_name": "Acme Corp",
            "active": True,
            "balance": 5000.00,
            "sync_token": "0"
        },
        {
            "qbo_id": "2",
            "name": "Tech Startup LLC",
            "display_name": "Tech Startup LLC", 
            "active": True,
            "balance": 2500.00,
            "sync_token": "0"
        }
    ],
    "accounts": [
        {
            "qbo_id": "1",
            "name": "Checking Account",
            "account_type": "Bank",
            "account_sub_type": "Checking",
            "current_balance": 15000.00,
            "active": True,
            "sync_token": "0"
        },
        {
            "qbo_id": "2",
            "name": "Savings Account",
            "account_type": "Bank", 
            "account_sub_type": "Savings",
            "current_balance": 5000.00,
            "active": True,
            "sync_token": "0"
        }
    ],
    "company_info": {
        "qbo_id": "1",
        "company_name": "Test Company Inc",
        "legal_name": "Test Company Inc",
        "country": "US",
        "fiscal_year_start": "January",
        "sync_token": "0"
    }
}
