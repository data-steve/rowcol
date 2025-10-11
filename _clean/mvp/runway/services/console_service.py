"""
Console Service - Insights and Recommendations

This service provides console functionality for advisors to view
financial insights and recommendations. It uses domain gateways directly
with filtering methods for decision-ready records.
"""

from typing import Dict, Any, List, Optional, Protocol
import logging

logger = logging.getLogger(__name__)

class ConsoleService:
    """Service for console functionality."""
    
    def __init__(self, advisor_id: str, business_id: str, realm_id: str, 
                 bills_gateway, invoices_gateway, balances_gateway):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.realm_id = realm_id
        self.bills_gateway = bills_gateway
        self.invoices_gateway = invoices_gateway
        self.balances_gateway = balances_gateway
        
        logger.info(f"Initialized ConsoleService for advisor {advisor_id}, business {business_id}")
    
    async def get_console_snapshot(self) -> Dict[str, Any]:
        """Get complete financial snapshot for advisor dashboard."""
        from mvp.domains.ap.models import ListBillsQuery
        from mvp.domains.ar.models import ListInvoicesQuery
        from mvp.domains.bank.models import ListBalancesQuery
        
        # Get payment-ready bills using domain gateway filtering
        bills_query = ListBillsQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            realm_id=self.realm_id
        )
        payment_ready_bills = await self.bills_gateway.list_payment_ready(bills_query)
        
        # Get collections-ready invoices using domain gateway filtering
        invoices_query = ListInvoicesQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            realm_id=self.realm_id
        )
        collections_ready_invoices = await self.invoices_gateway.list_collections_ready(invoices_query)
        
        # Get current balances
        balances_query = ListBalancesQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            realm_id=self.realm_id
        )
        balances = await self.balances_gateway.list(balances_query)
        
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "payment_ready_bills": payment_ready_bills,
            "collections_ready_invoices": collections_ready_invoices,
            "balances": balances,
            "cash_position": self._calculate_cash_position(balances),
            "bills_due_this_week": len([bill for bill in payment_ready_bills if self._is_due_this_week(bill)]),
            "total_ap": sum(bill.amount for bill in payment_ready_bills),
            "total_ar": sum(invoice.amount for invoice in collections_ready_invoices),
            "runway_days": self._calculate_runway_days(balances, payment_ready_bills),
            "last_updated": "2024-01-01T00:00:00Z"  # TODO: Get from sync orchestrator
        }
    
    async def get_financial_overview(self) -> Dict[str, Any]:
        """Get financial overview with key metrics."""
        snapshot = await self.get_console_snapshot()
        
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "cash_position": snapshot["cash_position"],
            "bills_due_this_week": snapshot["bills_due_this_week"],
            "total_ap": snapshot["total_ap"],
            "total_ar": snapshot["total_ar"],
            "runway_days": snapshot["runway_days"],
            "health_status": self._calculate_health_status(snapshot),
            "last_updated": snapshot["last_updated"]
        }
    
    def _calculate_cash_position(self, balances: List[Any]) -> float:
        """Calculate current cash position."""
        # TODO: Implement proper cash position calculation
        return sum(balance.amount for balance in balances if balance.account_type == "Bank")
    
    def _is_due_this_week(self, bill) -> bool:
        """Check if bill is due this week."""
        # TODO: Implement proper date logic
        return True  # Simplified for now
    
    def _calculate_runway_days(self, balances: List[Any], bills: List[Any]) -> int:
        """Calculate runway in days."""
        cash_position = self._calculate_cash_position(balances)
        monthly_expenses = sum(bill.amount for bill in bills) * 4  # Simplified
        return int(cash_position / (monthly_expenses / 30)) if monthly_expenses > 0 else 0
    
    def _calculate_health_status(self, snapshot: Dict[str, Any]) -> str:
        """Calculate overall financial health status."""
        runway_days = snapshot.get("runway_days", 0)
        bills_due_this_week = snapshot.get("bills_due_this_week", 0)
        
        if runway_days < 30:
            return "critical"
        elif runway_days < 90 or bills_due_this_week > 10:
            return "warning"
        else:
            return "healthy"
