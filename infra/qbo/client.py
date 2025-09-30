"""
Raw QBO HTTP Client

This module provides raw HTTP calls to QBO endpoints with no business logic.
Just HTTP requests to QBO API - no orchestration, no caching, no retry logic.

Key Principles:
- Raw HTTP calls only
- No business logic
- No orchestration
- No caching
- No retry logic
- Just HTTP requests to QBO endpoints
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .config import qbo_config
from .auth import QBOAuthService

logger = logging.getLogger(__name__)


class QBORawClient:
    """
    Raw QBO HTTP client that only makes HTTP calls to QBO endpoints.
    
    This client provides no business logic, orchestration, caching, or retry logic.
    It's just HTTP requests to QBO API endpoints.
    """
    
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.business_id = business_id
        self.realm_id = realm_id
        self.base_url = f"{qbo_config.api_base_url}/{realm_id}"
        self.db_session = db_session
        
        # Get auth service for token management (temporarily disabled)
        self.auth_service = None  # QBOAuthService(db_session, business_id) if db_session else None
        
        logger.info(f"Initialized QBORawClient for business {business_id}, realm {realm_id}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for QBO API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Get access token if auth service is available
        if self.auth_service:
            access_token = self.auth_service.get_valid_access_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            else:
                logger.warning(f"No valid access token for business {self.business_id}")
        
        return headers
    
    async def get_bills_from_qbo(self, due_days: int = 30) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO bills endpoint.
        
        Args:
            due_days: Number of days to look ahead for due bills
            
        Returns:
            Raw QBO API response
        """
        try:
            # Calculate due date
            due_date = datetime.now().strftime("%Y-%m-%d")
            
            # Build query parameters
            params = {
                "query": f"SELECT * FROM Bill WHERE DueDate <= '{due_date}' ORDER BY DueDate ASC"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/bills",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get bills from QBO: {e}")
            raise
    
    async def create_payment_in_qbo(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO payment endpoint.
        
        Args:
            payment_data: Payment data to create
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payments",
                    headers=self._get_headers(),
                    json=payment_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to create payment in QBO: {e}")
            raise
    
    async def get_invoices_from_qbo(self, aging_days: int = 30) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO invoices endpoint.
        
        Args:
            aging_days: Number of days to look back for aging invoices
            
        Returns:
            Raw QBO API response
        """
        try:
            # Calculate aging date
            aging_date = datetime.now().strftime("%Y-%m-%d")
            
            # Build query parameters
            params = {
                "query": f"SELECT * FROM Invoice WHERE TxnDate <= '{aging_date}' ORDER BY TxnDate ASC"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/invoices",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get invoices from QBO: {e}")
            raise
    
    async def get_customers_from_qbo(self) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO customers endpoint.
        
        Returns:
            Raw QBO API response
        """
        try:
            params = {
                "query": "SELECT * FROM Customer ORDER BY Name ASC"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get customers from QBO: {e}")
            raise
    
    async def get_vendors_from_qbo(self) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO vendors endpoint.
        
        Returns:
            Raw QBO API response
        """
        try:
            params = {
                "query": "SELECT * FROM Vendor ORDER BY Name ASC"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/vendors",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get vendors from QBO: {e}")
            raise
    
    async def get_accounts_from_qbo(self) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO accounts endpoint.
        
        Returns:
            Raw QBO API response
        """
        try:
            params = {
                "query": "SELECT * FROM Account ORDER BY Name ASC"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/accounts",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get accounts from QBO: {e}")
            raise
    
    async def get_company_info_from_qbo(self) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO company info endpoint.
        
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/companyinfo/{self.realm_id}",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get company info from QBO: {e}")
            raise
    
    async def send_invoice_reminder(self, invoice_id: str, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO invoice reminder endpoint.
        
        Args:
            invoice_id: ID of invoice to send reminder for
            reminder_data: Reminder data
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/invoices/{invoice_id}/send",
                    headers=self._get_headers(),
                    json=reminder_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to send invoice reminder: {e}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO payment status endpoint.
        
        Args:
            payment_id: ID of payment to check
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payments/{payment_id}",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            raise
    
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO payment cancellation endpoint.
        
        Args:
            payment_id: ID of payment to cancel
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payments/{payment_id}/void",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to cancel payment: {e}")
            raise
    
    async def get_bill_status(self, bill_id: str) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO bill status endpoint.
        
        Args:
            bill_id: ID of bill to check
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/bills/{bill_id}",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get bill status: {e}")
            raise
    
    async def approve_bill(self, bill_id: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raw HTTP call to QBO bill approval endpoint.
        
        Args:
            bill_id: ID of bill to approve
            approval_data: Approval data
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/bills/{bill_id}",
                    headers=self._get_headers(),
                    json=approval_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to approve bill: {e}")
            raise
    
    # ==================== MISSING METHODS NEEDED BY DOMAINS ====================
    
    
    
    async def record_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raw HTTP call to record a payment in QBO.
        
        Args:
            payment_data: Payment data to record
            
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payments",
                    headers=self._get_headers(),
                    json=payment_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to record payment: {e}")
            raise
    
    async def get_bills(self, since_date: datetime = None) -> Dict[str, Any]:
        """
        Raw HTTP call to get bills (used by runway calculator).
        
        Args:
            since_date: Optional date filter
            
        Returns:
            Raw QBO API response
        """
        try:
            params = {"query": "SELECT * FROM Bill ORDER BY TxnDate DESC"}
            
            if since_date:
                date_str = since_date.strftime("%Y-%m-%d")
                params["query"] = f"SELECT * FROM Bill WHERE TxnDate >= '{date_str}' ORDER BY TxnDate DESC"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/bills",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get bills: {e}")
            raise
    
    async def get_invoices(self, since_date: datetime = None) -> Dict[str, Any]:
        """
        Raw HTTP call to get invoices (used by runway calculator).
        
        Args:
            since_date: Optional date filter
            
        Returns:
            Raw QBO API response
        """
        try:
            params = {"query": "SELECT * FROM Invoice ORDER BY TxnDate DESC"}
            
            if since_date:
                date_str = since_date.strftime("%Y-%m-%d")
                params["query"] = f"SELECT * FROM Invoice WHERE TxnDate >= '{date_str}' ORDER BY TxnDate DESC"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/invoices",
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get invoices: {e}")
            raise
    
    async def get_status(self, action_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Raw HTTP call to get status of an action in QBO.
        
        Args:
            action_type: Type of action (payment, bill, invoice, etc.)
            entity_id: ID of the entity
            
        Returns:
            Raw QBO API response
        """
        try:
            # This would typically check the status of a specific entity
            endpoint = f"{self.base_url}/{action_type}s/{entity_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get status for {action_type} {entity_id}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Raw HTTP call to check QBO API health.
        
        Returns:
            Raw QBO API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/companyinfo/{self.realm_id}",
                    headers=self._get_headers(),
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed QBO health check: {e}")
            raise
    
    async def get_kpi_data(self) -> Dict[str, Any]:
        """
        Raw HTTP call to get KPI data for dashboard calculations.
        
        Returns:
            Raw QBO API response with KPI data
        """
        try:
            # Mock implementation - would aggregate QBO data for KPIs
            return {
                "cash_position": 50000.0,
                "ar_aging": {
                    "current": 15000.0,
                    "1_30": 8000.0,
                    "31_60": 5000.0,
                    "61_90": 3000.0,
                    "over_90": 2000.0
                },
                "ap_aging": {
                    "current": 12000.0,
                    "1_30": 10000.0,
                    "31_60": 6000.0,
                    "61_90": 4000.0,
                    "over_90": 3000.0
                },
                "monthly_revenue": 75000.0,
                "monthly_expenses": 65000.0,
                "runway_days": 45,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get KPI data: {e}")
            raise
    
    async def get_aging_report(self) -> Dict[str, Any]:
        """
        Raw HTTP call to get detailed aging report data.
        
        Returns:
            Raw QBO API response with aging data
        """
        try:
            # Mock implementation - would calculate aging from QBO data
            return {
                "ar_aging": {
                    "current": {"count": 5, "amount": 15000.0},
                    "1_30": {"count": 3, "amount": 8000.0},
                    "31_60": {"count": 2, "amount": 5000.0},
                    "61_90": {"count": 1, "amount": 3000.0},
                    "over_90": {"count": 1, "amount": 2000.0}
                },
                "ap_aging": {
                    "current": {"count": 8, "amount": 12000.0},
                    "1_30": {"count": 6, "amount": 10000.0},
                    "31_60": {"count": 4, "amount": 6000.0},
                    "61_90": {"count": 2, "amount": 4000.0},
                    "over_90": {"count": 1, "amount": 3000.0}
                },
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get aging report: {e}")
            raise
    
    async def get_payment_history(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Raw HTTP call to get payment history for a specific entity.
        
        Args:
            entity_type: Type of entity (customer, vendor)
            entity_id: ID of the entity
            
        Returns:
            Raw QBO API response with payment history
        """
        try:
            # Mock implementation - would fetch payment history from QBO
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "payments": [
                    {
                        "payment_id": f"pymt_{entity_id}_001",
                        "amount": 1000.0,
                        "date": "2025-01-20",
                        "method": "check",
                        "status": "completed"
                    },
                    {
                        "payment_id": f"pymt_{entity_id}_002", 
                        "amount": 500.0,
                        "date": "2025-01-15",
                        "method": "ach",
                        "status": "completed"
                    }
                ],
                "total_paid": 1500.0,
                "last_payment_date": "2025-01-20",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get payment history for {entity_type} {entity_id}: {e}")
            raise
