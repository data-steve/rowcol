from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from domains.core.models.business import Business

load_dotenv()

class QBOIntegrationService:
    """Production-grade QBO integration service with automatic token refresh."""
    
    def __init__(self, business: Business):
        self.business = business
        self.tenant_id = business.qbo_id
        self.auth_client = AuthClient(
            os.getenv("QBO_CLIENT_ID"),
            os.getenv("QBO_CLIENT_SECRET"),
            os.getenv("QBO_REDIRECT_URI"),
            environment="sandbox"
        )
        self.auth_client.refresh_token = os.getenv("QBO_REFRESH_TOKEN")
        
        # Set base URL for QBO API
        self.base_url = "https://sandbox-quickbooks.api.intuit.com/v3/company"
        self.realm_id = os.getenv("QBO_REALM_ID")
        self.api_url = f"{self.base_url}/{self.realm_id}"
        
        # Current access token (will be refreshed as needed)
        self._access_token = None
        self._token_expires_at = None
    
    def _ensure_valid_token(self) -> str:
        """Ensure we have a valid access token, refreshing if necessary."""
        now = datetime.now()
        
        # If we don't have a token or it's expired/expiring soon, refresh it
        if (not self._access_token or 
            not self._token_expires_at or 
            now >= self._token_expires_at - timedelta(minutes=5)):
            
            try:
                self._refresh_access_token()
            except Exception as e:
                raise ValueError(f"Failed to refresh QBO access token: {str(e)}")
        
        return self._access_token
    
    def _refresh_access_token(self):
        """Refresh the QBO access token using the refresh token."""
        try:
            # Refresh the token
            self.auth_client.refresh()
            
            # Update our stored tokens
            self._access_token = self.auth_client.access_token
            self._token_expires_at = datetime.now() + timedelta(hours=1)  # QBO tokens typically last 1 hour
            
            # Update environment variables for other services
            os.environ["QBO_ACCESS_TOKEN"] = self._access_token
            os.environ["QBO_REFRESH_TOKEN"] = self.auth_client.refresh_token
            
            print("✅ QBO access token refreshed successfully")
            
        except Exception as e:
            raise ValueError(f"Token refresh failed: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with current access token."""
        return {
            "Authorization": f"Bearer {self._ensure_valid_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_transactions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch transactions from QBO with automatic retry and token refresh."""
        headers = self._get_headers()
        
        # For now, let's fetch basic purchase and sales transactions
        try:
            transactions = []
            
            # Fetch purchases
            response = requests.get(
                f"{self.api_url}/query",
                headers=headers,
                params={"query": "SELECT * FROM Purchase"}
            )
            response.raise_for_status()
            purchase_data = response.json()
            purchases = self._parse_purchase_transactions(purchase_data)
            transactions.extend(purchases)
            
            # Fetch sales receipts
            response = requests.get(
                f"{self.api_url}/query",
                headers=headers,
                params={"query": "SELECT * FROM SalesReceipt"}
            )
            response.raise_for_status()
            sales_data = response.json()
            sales = self._parse_sales_transactions(sales_data)
            transactions.extend(sales)
            
            return transactions
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch QBO transactions: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs (classes) from QBO."""
        headers = self._get_headers()
        
        try:
            response = requests.get(
                f"{self.api_url}/query",
                headers=headers,
                params={"query": "SELECT * FROM Class"}
            )
            response.raise_for_status()
            
            data = response.json()
            return self._parse_jobs(data)
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch QBO jobs: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_vendors(self) -> List[Dict[str, Any]]:
        """Fetch vendors from QBO."""
        headers = self._get_headers()
        
        try:
            response = requests.get(
                f"{self.api_url}/query",
                headers=headers,
                params={"query": "SELECT * FROM Vendor"}
            )
            response.raise_for_status()
            
            data = response.json()
            return self._parse_vendors(data)
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch QBO vendors: {str(e)}")
    
    def _parse_purchase_transactions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse QBO purchase transactions."""
        transactions = []
        
        if "QueryResponse" in data and "Purchase" in data["QueryResponse"]:
            for purchase in data["QueryResponse"]["Purchase"]:
                transaction = {
                    "txn_id": purchase.get("Id", ""),
                    "date": purchase.get("TxnDate", ""),
                    "type": "expense",
                    "amount": float(purchase.get("TotalAmt", 0)),
                    "memo": purchase.get("PrivateNote", ""),
                    "vendor_ref": purchase.get("EntityRef", {}).get("name", "") if purchase.get("EntityRef") else ""
                }
                transactions.append(transaction)
        
        return transactions
    
    def _parse_sales_transactions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse QBO sales transactions."""
        transactions = []
        
        if "QueryResponse" in data and "SalesReceipt" in data["QueryResponse"]:
            for sale in data["QueryResponse"]["SalesReceipt"]:
                transaction = {
                    "txn_id": sale.get("Id", ""),
                    "date": sale.get("TxnDate", ""),
                    "type": "deposit",
                    "amount": float(sale.get("TotalAmt", 0)),
                    "memo": sale.get("PrivateNote", ""),
                    "customer_ref": sale.get("CustomerRef", {}).get("name", "") if sale.get("CustomerRef") else ""
                }
                transactions.append(transaction)
        
        return transactions
    
    ## NOTE: WE'RE NOT DOING JOB Related stuff now
    # def _parse_jobs(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    #     """Parse QBO jobs (classes) response."""
    #     jobs = []
        
    #     if "QueryResponse" in data and "Class" in data["QueryResponse"]:
    #         for job in data["QueryResponse"]["Class"]:
    #             jobs.append({
    #                 "job_id": job.get("Id", ""),  # Parked for Phase 0
    #                 "name": job.get("Name", ""),
    #                 "active": job.get("Active", True),
    #                 "sub_class": job.get("SubClass", False)
    #             })
        
    #     return jobs
    
    def _parse_vendors(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse QBO vendors response."""
        vendors = []
        
        if "QueryResponse" in data and "Vendor" in data["QueryResponse"]:
            for vendor in data["QueryResponse"]["Vendor"]:
                vendors.append({
                    "vendor_id": vendor.get("Id", ""),
                    "name": vendor.get("DisplayName", ""),
                    "email": vendor.get("PrimaryEmailAddr", {}).get("Address", ""),
                    "active": vendor.get("Active", True)
                })
        
        return vendors
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the QBO connection and return status."""
        try:
            # Try to fetch a simple endpoint
            headers = self._get_headers()
            response = requests.get(
                f"{self.api_url}/companyinfo/{self.realm_id}",
                headers=headers
            )
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "QBO connection successful",
                "realm_id": self.realm_id,
                "access_token_valid": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"QBO connection failed: {str(e)}",
                "realm_id": self.realm_id,
                "access_token_valid": False
            }
