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

from domains.integrations.qbo.auth import QBOAuthService
from common.exceptions import IntegrationError
from .config import qbo_config
from domains.integrations.qbo.auth import QBOEnvironment

def get_production_qbo_business():
    """
    Get real QBO business from production database.
    
    This centralizes the logic for accessing production QBO data
    instead of duplicating database connection code across tests and services.
    
    Returns:
        tuple: (business, realm_id) from production database
        
    Raises:
        IntegrationError: If no QBO integration found
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from domains.core.models.integration import Integration
    from domains.core.models.business import Business
    
    database_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///oodaloo.db')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    
    with Session() as prod_session:
        # Get real QBO integration from production database
        integration = prod_session.query(Integration).filter(
            Integration.platform == 'qbo'
        ).first()
        
        if not integration:
            raise IntegrationError("No QBO integration found in production database")
        
        # Get the business associated with this integration
        business = prod_session.query(Business).filter(
            Business.business_id == integration.business_id
        ).first()
        
        if not business:
            raise IntegrationError(f"Business {integration.business_id} not found for QBO integration")
        
        # Get realm_id from environment
        realm_id = os.getenv('QBO_REALM_ID')
        if not realm_id:
            raise IntegrationError("QBO_REALM_ID environment variable not set")
        
        return business, realm_id

logger = logging.getLogger(__name__)

# Error message for token refresh manual intervention
QBO_TOKEN_REFRESH_ERROR_MESSAGE = """
🚨 QBO TOKEN REFRESH REQUIRED - MANUAL INTERVENTION NEEDED

The QBO access token has expired and automatic refresh failed. Follow these exact steps:

1. RUN THE TOKEN REFRESH SCRIPT:
   poetry run python domains/integrations/qbo/get_qbo_tokens.py

2. WHEN PROMPTED FOR AUTHORIZATION CODE:
   - Go to the QBO OAuth URL that appears
   - Sign in to QuickBooks Online
   - Copy the authorization code from the redirect URL
   - Paste it here (DO NOT click "GET TOKEN" button - that uses up the code)

3. THE SCRIPT WILL AUTOMATICALLY:
   - Use QBO_REALM_ID from your .env file
   - Save tokens to both database and dev_tokens.json
   - Complete the refresh process

4. VERIFY THE FIX:
   poetry run pytest tests/integration/test_qbo_api_direct.py -m qbo_real_api

The system will self-heal from dev_tokens.json on future runs, so this should be a one-time fix.

If you continue to see this error, check:
- QBO_REALM_ID is correct in .env
- QBO_CLIENT_ID and QBO_CLIENT_SECRET are valid
- You have internet connectivity to QBO API
"""


class QBOAPIClient:
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
        
        # Rate limiting and caching
        self.retry_cache = {}  # Cache for deduplication
        self.rate_limits = {
            "qbo": {
                "min_interval": 0.1,  # Minimum 6 seconds between calls
                "max_calls_per_hour": 100,  # QBO rate limit
                "backoff_multiplier": 1.5,  # Gentler exponential backoff
                "max_retries": 2  # Reduced from 3 to 2
            }
        }
        
    def _get_base_url(self) -> str:
        """Get QBO API base URL based on environment."""
        return qbo_config.api_base_url
    
    def _should_allow_call(self, platform: str) -> bool:
        """Check if API call should be allowed based on rate limiting."""
        if platform not in self.rate_limits:
            return True
        
        # Check minimum interval
        last_call = self.rate_limits[platform].get("last_call")
        if last_call:
            min_interval = self.rate_limits[platform]["min_interval"]
            time_since_last = (datetime.now() - last_call).total_seconds() / 60
            if time_since_last < min_interval:
                return False
        
        # Check hourly rate limit
        hourly_calls = self.rate_limits[platform].get("hourly_calls", [])
        now = datetime.now()
        hourly_calls = [call_time for call_time in hourly_calls if (now - call_time).total_seconds() < 3600]
        
        max_calls = self.rate_limits[platform]["max_calls_per_hour"]
        if len(hourly_calls) >= max_calls:
            return False
        
        # Update rate limiting tracking
        self.rate_limits[platform]["last_call"] = now
        self.rate_limits[platform]["hourly_calls"] = hourly_calls + [now]
        
        return True
    
    def _get_retry_after(self, platform: str) -> int:
        """Get seconds to wait before retrying."""
        if platform not in self.rate_limits:
            return 60
        
        last_call = self.rate_limits[platform].get("last_call")
        if not last_call:
            return 0
        
        min_interval = self.rate_limits[platform]["min_interval"]
        time_since_last = (datetime.now() - last_call).total_seconds() / 60
        if time_since_last < min_interval:
            return int((min_interval - time_since_last) * 60)
        
        return 0
    
    def _generate_call_key(self, operation: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique key for caching API calls."""
        import hashlib
        key_data = f"{operation}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _determine_business_size(self) -> str:
        """Determine business size based on business_id or other context."""
        # For now, use a simple hash of business_id to determine size
        # In production, this could query the database for actual business metrics
        if not self.business_id:
            return "small"
        
        # Use hash to consistently assign business size
        hash_val = hash(self.business_id) % 100
        if hash_val < 60:
            return "small"      # 60% small businesses
        elif hash_val < 85:
            return "medium"     # 25% medium businesses  
        else:
            return "large"      # 15% large businesses
    
    def _get_realistic_mock_data(self, business_size: str) -> Dict[str, Any]:
        """Generate realistic mock data based on business size."""
        if business_size == "small":
            return self._get_small_business_data()
        elif business_size == "medium":
            return self._get_medium_business_data()
        else:
            return self._get_large_business_data()
    
    def _get_small_business_data(self) -> Dict[str, Any]:
        """Mock data for small business (1-10 employees, <$1M revenue)."""
        return {
            "bills": [
                {
                    "Id": "bill_001",
                    "VendorRef": {"name": "Office Depot", "value": "vendor_001"},
                    "TotalAmt": 150.00,
                    "Balance": 150.00,
                    "DueDate": "2025-10-15",
                    "TxnDate": "2025-09-15",
                    "DocNumber": "BILL-001",
                    "Line": [{"Id": "1", "Amount": 150.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_002", 
                    "VendorRef": {"name": "Internet Provider", "value": "vendor_002"},
                    "TotalAmt": 89.99,
                    "Balance": 89.99,
                    "DueDate": "2025-10-01",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "BILL-002",
                    "Line": [{"Id": "2", "Amount": 89.99, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_003",
                    "VendorRef": {"name": "Software License", "value": "vendor_003"},
                    "TotalAmt": 299.00,
                    "Balance": 0.00,  # Paid
                    "DueDate": "2025-09-20",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "BILL-003",
                    "Line": [{"Id": "3", "Amount": 299.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                }
            ],
            "invoices": [
                {
                    "Id": "invoice_001",
                    "CustomerRef": {"name": "Client A", "value": "customer_001"},
                    "TotalAmt": 2500.00,
                    "Balance": 2500.00,
                    "DueDate": "2025-10-20",
                    "TxnDate": "2025-09-20",
                    "DocNumber": "INV-001",
                    "Line": [{"Id": "1", "Amount": 2500.00, "DetailType": "SalesItemLineDetail"}]
                },
                {
                    "Id": "invoice_002",
                    "CustomerRef": {"name": "Client B", "value": "customer_002"},
                    "TotalAmt": 1200.00,
                    "Balance": 0.00,  # Paid
                    "DueDate": "2025-09-15",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "INV-002",
                    "Line": [{"Id": "2", "Amount": 1200.00, "DetailType": "SalesItemLineDetail"}]
                }
            ],
            "customers": [
                {
                    "Id": "customer_001",
                    "Name": "Client A",
                    "Active": True,
                    "Email": "clienta@example.com",
                    "CompanyName": "Client A Corp"
                },
                {
                    "Id": "customer_002",
                    "Name": "Client B",
                    "Active": True,
                    "Email": "clientb@example.com",
                    "CompanyName": "Client B LLC"
                }
            ],
            "vendors": [
                {
                    "Id": "vendor_001", 
                    "Name": "Office Depot",
                    "Active": True,
                    "Email": "billing@officedepot.com",
                    "CompanyName": "Office Depot Inc."
                },
                {
                    "Id": "vendor_002",
                    "Name": "Internet Provider",
                    "Active": True,
                    "Email": "billing@internet.com",
                    "CompanyName": "Internet Provider LLC"
                },
                {
                    "Id": "vendor_003",
                    "Name": "Software License",
                    "Active": True,
                    "Email": "billing@software.com",
                    "CompanyName": "Software Corp"
                }
            ],
            "accounts": [
                {
                    "Id": "account_001",
                    "Name": "Business Checking",
                    "AccountType": "Bank",
                    "AccountSubType": "Checking",
                    "CurrentBalance": 15000.00
                },
                {
                    "Id": "account_002",
                    "Name": "Business Savings",
                    "AccountType": "Bank", 
                    "AccountSubType": "Savings",
                    "CurrentBalance": 5000.00
                }
            ],
            "company_info": [
                {
                    "Id": "1",
                    "CompanyName": "Small Business LLC",
                    "LegalName": "Small Business LLC",
                    "Country": "US",
                    "FiscalYearStartMonth": "1",
                    "SyncToken": "1"
                }
            ]
        }
    
    def _get_medium_business_data(self) -> Dict[str, Any]:
        """Mock data for medium business (11-50 employees, $1M-$10M revenue)."""
        return {
            "bills": [
                {
                    "Id": "bill_001",
                    "VendorRef": {"name": "Office Supplies Co", "value": "vendor_001"},
                    "TotalAmt": 2500.00,
                    "Balance": 2500.00,
                    "DueDate": "2025-10-15",
                    "TxnDate": "2025-09-15",
                    "DocNumber": "BILL-001",
                    "Line": [{"Id": "1", "Amount": 2500.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_002", 
                    "VendorRef": {"name": "Software Services", "value": "vendor_002"},
                    "TotalAmt": 1500.00,
                    "Balance": 1500.00,
                    "DueDate": "2025-10-01",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "BILL-002",
                    "Line": [{"Id": "2", "Amount": 1500.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_003",
                    "VendorRef": {"name": "Marketing Agency", "value": "vendor_003"},
                    "TotalAmt": 5000.00,
                    "Balance": 0.00,  # Paid
                    "DueDate": "2025-09-20",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "BILL-003",
                    "Line": [{"Id": "3", "Amount": 5000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_004",
                    "VendorRef": {"name": "Legal Services", "value": "vendor_004"},
                    "TotalAmt": 3000.00,
                    "Balance": 3000.00,
                    "DueDate": "2025-11-01",
                    "TxnDate": "2025-09-20",
                    "DocNumber": "BILL-004",
                    "Line": [{"Id": "4", "Amount": 3000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                }
            ],
            "invoices": [
                {
                    "Id": "invoice_001",
                    "CustomerRef": {"name": "Enterprise Client", "value": "customer_001"},
                    "TotalAmt": 15000.00,
                    "Balance": 15000.00,
                    "DueDate": "2025-10-20",
                    "TxnDate": "2025-09-20",
                    "DocNumber": "INV-001",
                    "Line": [{"Id": "1", "Amount": 15000.00, "DetailType": "SalesItemLineDetail"}]
                },
                {
                    "Id": "invoice_002",
                    "CustomerRef": {"name": "Mid-Market Client", "value": "customer_002"},
                    "TotalAmt": 8000.00,
                    "Balance": 0.00,  # Paid
                    "DueDate": "2025-09-15",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "INV-002",
                    "Line": [{"Id": "2", "Amount": 8000.00, "DetailType": "SalesItemLineDetail"}]
                },
                {
                    "Id": "invoice_003",
                    "CustomerRef": {"name": "Retainer Client", "value": "customer_003"},
                    "TotalAmt": 5000.00,
                    "Balance": 5000.00,
                    "DueDate": "2025-10-01",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "INV-003",
                    "Line": [{"Id": "3", "Amount": 5000.00, "DetailType": "SalesItemLineDetail"}]
                }
            ],
            "customers": [
                {
                    "Id": "customer_001",
                    "Name": "Enterprise Client",
                    "Active": True,
                    "Email": "billing@enterprise.com",
                    "CompanyName": "Enterprise Corp"
                },
                {
                    "Id": "customer_002",
                    "Name": "Mid-Market Client",
                    "Active": True,
                    "Email": "billing@midmarket.com",
                    "CompanyName": "Mid-Market LLC"
                },
                {
                    "Id": "customer_003",
                    "Name": "Retainer Client",
                    "Active": True,
                    "Email": "billing@retainer.com",
                    "CompanyName": "Retainer Inc"
                }
            ],
            "vendors": [
                {
                    "Id": "vendor_001", 
                    "Name": "Office Supplies Co",
                    "Active": True,
                    "Email": "billing@officesupplies.com",
                    "CompanyName": "Office Supplies Co Inc"
                },
                {
                    "Id": "vendor_002",
                    "Name": "Software Services",
                    "Active": True,
                    "Email": "billing@software.com",
                    "CompanyName": "Software Services LLC"
                },
                {
                    "Id": "vendor_003",
                    "Name": "Marketing Agency",
                    "Active": True,
                    "Email": "billing@marketing.com",
                    "CompanyName": "Marketing Agency Inc"
                },
                {
                    "Id": "vendor_004",
                    "Name": "Legal Services",
                    "Active": True,
                    "Email": "billing@legal.com",
                    "CompanyName": "Legal Services LLP"
                }
            ],
            "accounts": [
                {
                    "Id": "account_001",
                    "Name": "Business Checking",
                    "AccountType": "Bank",
                    "AccountSubType": "Checking",
                    "CurrentBalance": 75000.00
                },
                {
                    "Id": "account_002",
                    "Name": "Business Savings",
                    "AccountType": "Bank", 
                    "AccountSubType": "Savings",
                    "CurrentBalance": 25000.00
                },
                {
                    "Id": "account_003",
                    "Name": "Money Market",
                    "AccountType": "Bank",
                    "AccountSubType": "MoneyMarket",
                    "CurrentBalance": 100000.00
                }
            ],
            "company_info": [
                {
                    "Id": "1",
                    "CompanyName": "Medium Business Inc",
                    "LegalName": "Medium Business Inc",
                    "Country": "US",
                    "FiscalYearStartMonth": "1",
                    "SyncToken": "1"
                }
            ]
        }
    
    def _get_large_business_data(self) -> Dict[str, Any]:
        """Mock data for large business (50+ employees, $10M+ revenue)."""
        return {
            "bills": [
                {
                    "Id": "bill_001",
                    "VendorRef": {"name": "Enterprise Software", "value": "vendor_001"},
                    "TotalAmt": 25000.00,
                    "Balance": 25000.00,
                    "DueDate": "2025-10-15",
                    "TxnDate": "2025-09-15",
                    "DocNumber": "BILL-001",
                    "Line": [{"Id": "1", "Amount": 25000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_002", 
                    "VendorRef": {"name": "Cloud Services", "value": "vendor_002"},
                    "TotalAmt": 15000.00,
                    "Balance": 15000.00,
                    "DueDate": "2025-10-01",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "BILL-002",
                    "Line": [{"Id": "2", "Amount": 15000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_003",
                    "VendorRef": {"name": "Professional Services", "value": "vendor_003"},
                    "TotalAmt": 50000.00,
                    "Balance": 0.00,  # Paid
                    "DueDate": "2025-09-20",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "BILL-003",
                    "Line": [{"Id": "3", "Amount": 50000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_004",
                    "VendorRef": {"name": "Legal & Compliance", "value": "vendor_004"},
                    "TotalAmt": 30000.00,
                    "Balance": 30000.00,
                    "DueDate": "2025-11-01",
                    "TxnDate": "2025-09-20",
                    "DocNumber": "BILL-004",
                    "Line": [{"Id": "4", "Amount": 30000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                },
                {
                    "Id": "bill_005",
                    "VendorRef": {"name": "Marketing & Advertising", "value": "vendor_005"},
                    "TotalAmt": 40000.00,
                    "Balance": 40000.00,
                    "DueDate": "2025-10-30",
                    "TxnDate": "2025-09-25",
                    "DocNumber": "BILL-005",
                    "Line": [{"Id": "5", "Amount": 40000.00, "DetailType": "AccountBasedExpenseLineDetail"}]
                }
            ],
            "invoices": [
                {
                    "Id": "invoice_001",
                    "CustomerRef": {"name": "Fortune 500 Client", "value": "customer_001"},
                    "TotalAmt": 150000.00,
                    "Balance": 150000.00,
                    "DueDate": "2025-10-20",
                    "TxnDate": "2025-09-20",
                    "DocNumber": "INV-001",
                    "Line": [{"Id": "1", "Amount": 150000.00, "DetailType": "SalesItemLineDetail"}]
                },
                {
                    "Id": "invoice_002",
                    "CustomerRef": {"name": "Enterprise Client A", "value": "customer_002"},
                    "TotalAmt": 80000.00,
                    "Balance": 0.00,  # Paid
                    "DueDate": "2025-09-15",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "INV-002",
                    "Line": [{"Id": "2", "Amount": 80000.00, "DetailType": "SalesItemLineDetail"}]
                },
                {
                    "Id": "invoice_003",
                    "CustomerRef": {"name": "Enterprise Client B", "value": "customer_003"},
                    "TotalAmt": 120000.00,
                    "Balance": 120000.00,
                    "DueDate": "2025-10-01",
                    "TxnDate": "2025-09-01",
                    "DocNumber": "INV-003",
                    "Line": [{"Id": "3", "Amount": 120000.00, "DetailType": "SalesItemLineDetail"}]
                },
                {
                    "Id": "invoice_004",
                    "CustomerRef": {"name": "Government Contract", "value": "customer_004"},
                    "TotalAmt": 200000.00,
                    "Balance": 200000.00,
                    "DueDate": "2025-11-15",
                    "TxnDate": "2025-09-15",
                    "DocNumber": "INV-004",
                    "Line": [{"Id": "4", "Amount": 200000.00, "DetailType": "SalesItemLineDetail"}]
                }
            ],
            "customers": [
                {
                    "Id": "customer_001",
                    "Name": "Fortune 500 Client",
                    "Active": True,
                    "Email": "billing@fortune500.com",
                    "CompanyName": "Fortune 500 Corp"
                },
                {
                    "Id": "customer_002",
                    "Name": "Enterprise Client A",
                    "Active": True,
                    "Email": "billing@enterprisea.com",
                    "CompanyName": "Enterprise A Inc"
                },
                {
                    "Id": "customer_003",
                    "Name": "Enterprise Client B",
                    "Active": True,
                    "Email": "billing@enterpriseb.com",
                    "CompanyName": "Enterprise B LLC"
                },
                {
                    "Id": "customer_004",
                    "Name": "Government Contract",
                    "Active": True,
                    "Email": "billing@govcontract.com",
                    "CompanyName": "Government Agency"
                }
            ],
            "vendors": [
                {
                    "Id": "vendor_001", 
                    "Name": "Enterprise Software",
                    "Active": True,
                    "Email": "billing@enterprisesoftware.com",
                    "CompanyName": "Enterprise Software Corp"
                },
                {
                    "Id": "vendor_002",
                    "Name": "Cloud Services",
                    "Active": True,
                    "Email": "billing@cloudservices.com",
                    "CompanyName": "Cloud Services Inc"
                },
                {
                    "Id": "vendor_003",
                    "Name": "Professional Services",
                    "Active": True,
                    "Email": "billing@profservices.com",
                    "CompanyName": "Professional Services LLC"
                },
                {
                    "Id": "vendor_004",
                    "Name": "Legal & Compliance",
                    "Active": True,
                    "Email": "billing@legalcompliance.com",
                    "CompanyName": "Legal & Compliance LLP"
                },
                {
                    "Id": "vendor_005",
                    "Name": "Marketing & Advertising",
                    "Active": True,
                    "Email": "billing@marketingad.com",
                    "CompanyName": "Marketing & Advertising Inc"
                }
            ],
            "accounts": [
                {
                    "Id": "account_001",
                    "Name": "Primary Checking",
                    "AccountType": "Bank",
                    "AccountSubType": "Checking",
                    "CurrentBalance": 500000.00
                },
                {
                    "Id": "account_002",
                    "Name": "Business Savings",
                    "AccountType": "Bank", 
                    "AccountSubType": "Savings",
                    "CurrentBalance": 200000.00
                },
                {
                    "Id": "account_003",
                    "Name": "Money Market",
                    "AccountType": "Bank",
                    "AccountSubType": "MoneyMarket",
                    "CurrentBalance": 1000000.00
                },
                {
                    "Id": "account_004",
                    "Name": "Investment Account",
                    "AccountType": "Other Current Asset",
                    "AccountSubType": "Investment",
                    "CurrentBalance": 2500000.00
                }
            ],
            "company_info": [
                {
                    "Id": "1",
                    "CompanyName": "Large Enterprise Corp",
                    "LegalName": "Large Enterprise Corporation",
                    "Country": "US",
                    "FiscalYearStartMonth": "1",
                    "SyncToken": "1"
                }
            ]
        }
    
    def _get_mock_response(self, endpoint: str, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Return realistic mock QBO data for testing across different business sizes."""
        # Determine business size based on context (could be enhanced with business_id lookup)
        business_size = self._determine_business_size()
        mock_data = self._get_realistic_mock_data(business_size)
        
        # Return appropriate mock data based on endpoint
        if endpoint == "query":
            # For query endpoints, return QueryResponse format
            if params and "Bill" in str(params.get("query", "")):
                return {"QueryResponse": {"Bill": mock_data["bills"]}}
            elif params and "Invoice" in str(params.get("query", "")):
                return {"QueryResponse": {"Invoice": mock_data["invoices"]}}
            elif params and "Customer" in str(params.get("query", "")):
                return {"QueryResponse": {"Customer": mock_data["customers"]}}
            elif params and "Vendor" in str(params.get("query", "")):
                return {"QueryResponse": {"Vendor": mock_data["vendors"]}}
            elif params and "Account" in str(params.get("query", "")):
                return {"QueryResponse": {"Account": mock_data["accounts"]}}
            else:
                # Default to bills if no specific entity requested
                return {"QueryResponse": {"Bill": mock_data["bills"]}}
        elif endpoint == "companyinfo/1":
            return {"QueryResponse": {"CompanyInfo": mock_data["company_info"]}}
        else:
            # Default response
            return {"QueryResponse": {"Bill": mock_data["bills"]}}
    
    def _get_mock_batch_response(self, batch_queries: List[Dict[str, str]]) -> Dict[str, Any]:
        """Return realistic mock batch response for testing."""
        # Use the same realistic mock data as individual calls
        business_size = self._determine_business_size()
        mock_data = self._get_realistic_mock_data(business_size)
        
        # Build batch response based on queries
        batch_responses = []
        for query in batch_queries:
            bId = query.get("bId", "")
            query_text = query.get("Query", "")
            
            if bId == "bills" or "Bill" in query_text:
                batch_responses.append({
                    "bId": "bills",
                    "QueryResponse": {"Bill": mock_data["bills"]}
                })
            elif bId == "invoices" or "Invoice" in query_text:
                batch_responses.append({
                    "bId": "invoices", 
                    "QueryResponse": {"Invoice": mock_data["invoices"]}
                })
            elif bId == "customers" or "Customer" in query_text:
                batch_responses.append({
                    "bId": "customers",
                    "QueryResponse": {"Customer": mock_data["customers"]}
                })
            elif bId == "vendors" or "Vendor" in query_text:
                batch_responses.append({
                    "bId": "vendors",
                    "QueryResponse": {"Vendor": mock_data["vendors"]}
                })
            elif bId == "accounts" or "Account" in query_text:
                batch_responses.append({
                    "bId": "accounts",
                    "QueryResponse": {"Account": mock_data["accounts"]}
                })
        
        return {"BatchItemResponse": batch_responses}
    
    def _transform_bills(self, bills_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform QBO bills data to standardized format."""
        return [
            {
                "qbo_id": bill["Id"],
                "vendor_ref": bill.get("VendorRef", {}),
                "amount": float(bill.get("TotalAmt", 0)),
                "due_date": bill.get("DueDate"),
                "balance": float(bill.get("Balance", 0)),
                "doc_number": bill.get("DocNumber"),
                "txn_date": bill.get("TxnDate")
            }
            for bill in bills_data
        ]
    
    def _transform_invoices(self, invoices_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform QBO invoices data to standardized format."""
        return [
            {
                "qbo_id": invoice["Id"],
                "customer_ref": invoice.get("CustomerRef", {}),
                "amount": float(invoice.get("TotalAmt", 0)),
                "due_date": invoice.get("DueDate"),
                "balance": float(invoice.get("Balance", 0)),
                "doc_number": invoice.get("DocNumber"),
                "txn_date": invoice.get("TxnDate")
            }
            for invoice in invoices_data
        ]
    
    def _transform_customers(self, customers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform QBO customers data to standardized format."""
        return [
            {
                "qbo_id": customer["Id"],
                "name": customer.get("Name"),
                "display_name": customer.get("DisplayName"),
                "active": customer.get("Active", True),
                "email": customer.get("Email")
            }
            for customer in customers_data
        ]
    
    def _transform_vendors(self, vendors_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform QBO vendors data to standardized format."""
        return [
            {
                "qbo_id": vendor["Id"],
                "name": vendor.get("Name"),
                "display_name": vendor.get("DisplayName"),
                "active": vendor.get("Active", True),
                "email": vendor.get("Email")
            }
            for vendor in vendors_data
        ]
    
    def _transform_accounts(self, accounts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform QBO accounts data to standardized format."""
        return [
            {
                "qbo_id": account["Id"],
                "name": account.get("Name"),
                "account_type": account.get("AccountType"),
                "account_sub_type": account.get("AccountSubType"),
                "current_balance": float(account.get("CurrentBalance", 0))
            }
            for account in accounts_data
        ]
    
    async def _make_api_call(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated QBO API call with intelligent error handling.
        If a 401 Unauthorized is received, it will attempt to refresh the
        token and retry the call once.
        """
        # No mocking
        
        auth_service = QBOAuthService(
            self.db, 
            self.business_id, 
            override_environment=QBOEnvironment.SANDBOX if "sandbox" in self.base_url else None
        )

        try:
            access_token = auth_service.get_valid_access_token()
            if not access_token:
                raise IntegrationError(f"No valid QBO access token for business {self.business_id}")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            url = f"{self.base_url}/{self.realm_id}/{endpoint}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params or {})
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                # Debug: Check response type and json method
                logger.debug(f"Response type: {type(response)}, json method: {type(response.json)}")
                json_data = response.json()
                logger.debug(f"JSON data type: {type(json_data)}")
                # Handle both sync and async response.json() patterns
                if hasattr(json_data, '__await__'):
                    return await json_data
                else:
                    return json_data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.info("Received 401 Unauthorized from QBO. Attempting to refresh token...")
                try:
                    new_access_token = auth_service.force_refresh_and_get_new_token()
                    if not new_access_token:
                        # Provide clear error message with exact steps for manual intervention
                        error_msg = self._generate_token_refresh_error_message()
                        logger.error(f"QBO token refresh failed. Manual intervention required:\n{error_msg}")
                        raise IntegrationError(f"QBO token refresh failed. {error_msg}") from e

                    logger.info("Token refreshed successfully. Retrying API call...")
                    headers["Authorization"] = f"Bearer {new_access_token}"
                    
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        if method.upper() == "GET":
                            response = await client.get(url, headers=headers, params=params or {})
                        else:
                            raise ValueError(f"Unsupported HTTP method: {method}")
                        
                        response.raise_for_status()
                        # Handle both sync and async response.json() patterns
                        json_data = response.json()
                        if hasattr(json_data, '__await__'):
                            return await json_data
                        else:
                            return json_data

                except Exception as retry_exc:
                    logger.error(f"QBO API call failed on retry after token refresh: {retry_exc}")
                    raise IntegrationError("QBO API call failed after token refresh") from retry_exc
            else:
                logger.error(f"QBO API call failed: {e.response.status_code} - {e.response.text}")
                raise IntegrationError(f"QBO API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"QBO API call failed with an unexpected error: {e}")
            raise IntegrationError(f"QBO API call failed: {str(e)}") from e
    
    async def smart_api_call(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a smart QBO API call with rate limiting and caching.
        
        This method provides the same functionality as the old SmartSyncService
        but integrated directly into the QBO client.
        """
        try:
            # Check rate limiting
            if not self._should_allow_call("qbo"):
                return {"status": "rate_limited", "retry_after": self._get_retry_after("qbo")}
            
            # Check for duplicate calls
            call_key = self._generate_call_key(f"{method}:{endpoint}", (params or {},), {})
            if call_key in self.retry_cache:
                cached_result = self.retry_cache[call_key]
                if datetime.now() - cached_result["timestamp"] < timedelta(minutes=5):
                    return cached_result["result"]
            
            # Make the actual call
            result = await self._make_api_call(endpoint, method, params)
            
            # Cache successful results
            self.retry_cache[call_key] = {
                "result": result,
                "timestamp": datetime.now()
            }
            
            return {"status": "success", "data": result}
            
        except Exception as e:
            logger.error(f"Smart QBO API call failed for {endpoint}: {e}", exc_info=True)
            return {"status": "error", "endpoint": endpoint, "error": str(e)}
    
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
    
    async def get_all_data_batch(self) -> Dict[str, Any]:
        """
        Get all QBO data in a single batch operation for efficiency.
        
        This method uses QBO's batch endpoint to retrieve bills, invoices, 
        customers, vendors, and accounts in one API call instead of multiple calls.
        This dramatically improves performance for integration tests.
        """
        try:
            # Create batch request with multiple queries
            batch_queries = [
                {
                    "bId": "bills",
                    "Query": "SELECT * FROM Bill WHERE Balance > '0'"
                },
                {
                    "bId": "invoices", 
                    "Query": "SELECT * FROM Invoice WHERE Balance > '0'"
                },
                {
                    "bId": "customers",
                    "Query": "SELECT * FROM Customer WHERE Active = true"
                },
                {
                    "bId": "vendors",
                    "Query": "SELECT * FROM Vendor WHERE Active = true"
                },
                {
                    "bId": "accounts",
                    "Query": "SELECT * FROM Account WHERE Active = true"
                }
            ]
            
            # Make batch API call
            batch_response = await self._make_batch_api_call(batch_queries)
            
            # Process batch response
            result = {
                "bills": [],
                "invoices": [],
                "customers": [],
                "vendors": [],
                "accounts": [],
                "company_info": {}
            }
            
            # Extract data from batch response
            for batch_item in batch_response.get("BatchItemResponse", []):
                bId = batch_item.get("bId")
                query_response = batch_item.get("QueryResponse", {})
                
                if bId == "bills" and "Bill" in query_response:
                    result["bills"] = self._transform_bills(query_response["Bill"])
                elif bId == "invoices" and "Invoice" in query_response:
                    result["invoices"] = self._transform_invoices(query_response["Invoice"])
                elif bId == "customers" and "Customer" in query_response:
                    result["customers"] = self._transform_customers(query_response["Customer"])
                elif bId == "vendors" and "Vendor" in query_response:
                    result["vendors"] = self._transform_vendors(query_response["Vendor"])
                elif bId == "accounts" and "Account" in query_response:
                    result["accounts"] = self._transform_accounts(query_response["Account"])
            
            # Get company info separately (not supported in batch)
            result["company_info"] = await self.get_company_info()
            
            return result
            
        except Exception as e:
            logger.error(f"Batch data retrieval failed: {e}")
            # Fallback to individual calls if batch fails
            return await self._get_all_data_individual()
    
    async def _make_batch_api_call(self, batch_queries: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make a batch API call to QBO."""
        # Mock response removed - use real API
        
        auth_service = QBOAuthService(self.db, self.business_id)
        access_token = auth_service.get_valid_access_token()
        if not access_token:
            raise IntegrationError(f"No valid QBO access token for business {self.business_id}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{self.realm_id}/batch"
        
        batch_request = {
            "BatchItemRequest": batch_queries
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:  # Reduced from 60s to 20s for batch
                response = await client.post(url, headers=headers, json=batch_request)
                response.raise_for_status()
                # Debug: Check response type and json method
                logger.debug(f"Batch response type: {type(response)}, json method: {type(response.json)}")
                json_data = response.json()
                logger.debug(f"Batch JSON data type: {type(json_data)}")
                # Handle both sync and async response.json() patterns
                if hasattr(json_data, '__await__'):
                    return await json_data
                else:
                    return json_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"QBO batch API call failed: {e.response.status_code} - {e.response.text}")
            raise IntegrationError(f"QBO batch API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"QBO batch API call failed: {e}")
            raise IntegrationError(f"QBO batch API call failed: {str(e)}")
    
    async def _get_all_data_individual(self) -> Dict[str, Any]:
        """Fallback method to get all data using individual API calls."""
        logger.warning("Using individual API calls as fallback - this will be slower")
        
        return {
            "bills": await self.get_bills(),
            "invoices": await self.get_invoices(),
            "customers": await self.get_customers(),
            "vendors": await self.get_vendors(),
            "accounts": await self.get_accounts(),
            "company_info": await self.get_company_info()
        }

    def _generate_token_refresh_error_message(self) -> str:
        """
        Generate a clear, actionable error message for manual token refresh.
        
        This provides exact steps for the LLM coder to follow when manual intervention is needed.
        """
        return QBO_TOKEN_REFRESH_ERROR_MESSAGE


# Factory functions for QBO provider creation
def get_qbo_client(business_id: str, db: Session, realm_id: str = None) -> 'QBOAPIClient':
    """
    Factory function to get QBO provider for real API calls.
    
    Args:
        business_id: Business identifier
        db: Database session
        realm_id: QBO realm/company ID (if None, will be looked up from database)
    
    Returns:
        QBOAPIClient instance for real QBO API calls
    """
    # If realm_id not provided, look it up (for convenience)
    if realm_id is None:
        realm_id = _get_realm_id_for_business(business_id, db)
    
    # Always use real QBO API provider - no more mocks
    return QBOAPIClient(business_id, realm_id, db)


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


def get_real_qbo_client(business_id: str, db: Session, realm_id: str) -> 'QBOAPIClient':
    """
    CRITICAL: Factory function that ALWAYS returns a QBO provider configured
    to hit the REAL Sandbox API, ignoring any mock environment variables.
    This is used by the proof-of-life test to guarantee a real connection.
    """
    provider = QBOAPIClient(business_id, realm_id, db)
    # Explicitly override the base URL to prevent mocking
    provider.base_url = qbo_config.sandbox_api_url
    return provider


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
