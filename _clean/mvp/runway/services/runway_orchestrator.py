"""
Runway Orchestrator - Core Business Logic Layer

This module provides the core business logic that orchestrates domain gateways
to provide product features. It follows the architecture pattern:
runway/ → domains/ → infra/ (no back edges)

The orchestrator composes domain gateways and provides high-level business
operations for the MVP product features.
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging

# Domain interfaces
from mvp.domains.ap.gateways import BillsGateway, ListBillsQuery, Bill
from mvp.domains.ar.gateways import InvoicesGateway, ListInvoicesQuery, Invoice
from mvp.domains.bank.gateways import BalancesGateway, ListBalancesQuery, AccountBalance

logger = logging.getLogger(__name__)

class RunwayOrchestrator:
    """
    Core business logic orchestrator for MVP.
    
    This class composes domain gateways and provides high-level business
    operations. It never imports infrastructure directly - only domain interfaces.
    """
    
    def __init__(self, bills_gateway: BillsGateway, invoices_gateway: InvoicesGateway, 
                 balances_gateway: BalancesGateway):
        self.bills_gateway = bills_gateway
        self.invoices_gateway = invoices_gateway
        self.balances_gateway = balances_gateway
        
        logger.info("Initialized RunwayOrchestrator with domain gateways")
    
    async def get_bill_tray(self, advisor_id: str, business_id: str) -> Dict[str, Any]:
        """
        Get bills organized by urgency for advisor review.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            
        Returns:
            Bill tray data organized by urgency
        """
        try:
            # Get bills from domain gateway
            bills_query = ListBillsQuery(
                advisor_id=advisor_id,
                business_id=business_id,
                status="OPEN",
                freshness_hint="CACHED_OK"
            )
            bills = await self.bills_gateway.list(bills_query)
            
            # Organize bills by urgency
            urgent_bills = []
            upcoming_bills = []
            overdue_bills = []
            
            today = date.today()
            total_amount = Decimal('0')
            
            for bill in bills:
                total_amount += bill.amount
                
                if bill.due_date:
                    days_until_due = (bill.due_date - today).days
                    
                    if days_until_due < 0:
                        overdue_bills.append(bill)
                    elif days_until_due <= 7:
                        urgent_bills.append(bill)
                    else:
                        upcoming_bills.append(bill)
                else:
                    # Bills without due dates go to upcoming
                    upcoming_bills.append(bill)
            
            # Calculate runway impact
            runway_impact_days = self._calculate_runway_impact_days(bills)
            
            return {
                "advisor_id": advisor_id,
                "business_id": business_id,
                "urgent_bills": [self._bill_to_dict(bill) for bill in urgent_bills],
                "upcoming_bills": [self._bill_to_dict(bill) for bill in upcoming_bills],
                "overdue_bills": [self._bill_to_dict(bill) for bill in overdue_bills],
                "urgent_count": len(urgent_bills),
                "upcoming_count": len(upcoming_bills),
                "overdue_count": len(overdue_bills),
                "total_amount": str(total_amount),
                "runway_impact_days": runway_impact_days,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get bill tray: {e}")
            raise
    
    async def get_console_snapshot(self, advisor_id: str, business_id: str) -> Dict[str, Any]:
        """
        Get complete financial snapshot for advisor dashboard.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            
        Returns:
            Console snapshot with financial overview
        """
        try:
            # Get all data from domain gateways
            bills_query = ListBillsQuery(
                advisor_id=advisor_id,
                business_id=business_id,
                status="OPEN",
                freshness_hint="CACHED_OK"
            )
            bills = await self.bills_gateway.list(bills_query)
            
            invoices_query = ListInvoicesQuery(
                advisor_id=advisor_id,
                business_id=business_id,
                status="OPEN",
                freshness_hint="CACHED_OK"
            )
            invoices = await self.invoices_gateway.list(invoices_query)
            
            balances_query = BalancesQuery(
                advisor_id=advisor_id,
                business_id=business_id,
                freshness_hint="CACHED_OK"
            )
            balances = await self.balances_gateway.get(balances_query)
            
            # Calculate financial metrics
            cash_position = sum(balance.available for balance in balances)
            total_ap = sum(bill.amount for bill in bills)
            total_ar = sum(invoice.amount for invoice in invoices)
            
            # Calculate bills due this week
            today = date.today()
            week_end = today + timedelta(days=7)
            bills_due_this_week = len([
                bill for bill in bills 
                if bill.due_date and today <= bill.due_date <= week_end
            ])
            
            # Calculate runway days
            runway_days = self._calculate_runway_days(bills, balances)
            
            # Get hygiene flags
            hygiene_flags = self._get_hygiene_flags(advisor_id, business_id)
            
            return {
                "advisor_id": advisor_id,
                "business_id": business_id,
                "cash_position": cash_position,
                "bills_due_this_week": bills_due_this_week,
                "total_ap": str(total_ap),
                "total_ar": str(total_ar),
                "runway_days": runway_days,
                "hygiene_flags": hygiene_flags,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get console snapshot: {e}")
            raise
    
    async def get_weekly_digest(self, advisor_id: str, business_id: str) -> Dict[str, Any]:
        """
        Get weekly summary of data quality and business insights.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            
        Returns:
            Weekly digest with insights and recommendations
        """
        try:
            # Get console snapshot data
            console_data = await self.get_console_snapshot(advisor_id, business_id)
            
            # Calculate data quality score
            data_quality_score = self._calculate_data_quality_score(advisor_id, business_id)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(console_data)
            
            return {
                "advisor_id": advisor_id,
                "business_id": business_id,
                "cash_position": console_data["cash_position"],
                "total_ap": console_data["total_ap"],
                "total_ar": console_data["total_ar"],
                "runway_days": console_data["runway_days"],
                "data_quality_score": data_quality_score,
                "hygiene_flags": console_data["hygiene_flags"],
                "recommendations": recommendations,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get weekly digest: {e}")
            raise
    
    async def fix_bill_hygiene(self, advisor_id: str, business_id: str, bill_id: str, 
                              fixes: Dict[str, Any]) -> bool:
        """
        Fix hygiene issues in QBO bill data.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            bill_id: Bill identifier
            fixes: Dictionary of field updates
            
        Returns:
            True if update was successful
        """
        try:
            # Update bill via domain gateway
            from mvp.domains.ap.gateways import UpdateBillRequest
            
            update_request = UpdateBillRequest(
                bill_id=bill_id,
                advisor_id=advisor_id,
                business_id=business_id,
                updates=fixes
            )
            
            success = await self.bills_gateway.update_bill(update_request)
            
            if success:
                logger.info(f"Successfully updated bill {bill_id} with fixes: {fixes}")
            else:
                logger.warning(f"Failed to update bill {bill_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to fix bill hygiene: {e}")
            raise
    
    async def fix_invoice_hygiene(self, advisor_id: str, business_id: str, invoice_id: str,
                                 fixes: Dict[str, Any]) -> bool:
        """
        Fix hygiene issues in QBO invoice data.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            invoice_id: Invoice identifier
            fixes: Dictionary of field updates
            
        Returns:
            True if update was successful
        """
        try:
            # Update invoice via domain gateway
            from mvp.domains.ar.gateways import UpdateInvoiceRequest
            
            update_request = UpdateInvoiceRequest(
                invoice_id=invoice_id,
                advisor_id=advisor_id,
                business_id=business_id,
                updates=fixes
            )
            
            success = await self.invoices_gateway.update_invoice(update_request)
            
            if success:
                logger.info(f"Successfully updated invoice {invoice_id} with fixes: {fixes}")
            else:
                logger.warning(f"Failed to update invoice {invoice_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to fix invoice hygiene: {e}")
            raise
    
    def _calculate_runway_impact_days(self, bills: List[Bill]) -> int:
        """Calculate runway impact in days based on bills."""
        if not bills:
            return 0
        
        # Simple calculation: sum of bill amounts divided by average daily burn
        total_amount = sum(bill.amount for bill in bills)
        
        # Assume average daily burn of $1000 (this would come from historical data)
        avg_daily_burn = Decimal('1000')
        
        if avg_daily_burn > 0:
            return int(total_amount / avg_daily_burn)
        
        return 0
    
    def _calculate_runway_days(self, bills: List[Bill], balances: List[AccountBalance]) -> int:
        """Calculate cash runway in days."""
        if not balances:
            return 0
        
        # Get total cash position
        total_cash = sum(balance.available for balance in balances)
        
        if total_cash <= 0:
            return 0
        
        # Calculate monthly burn from bills
        total_monthly_bills = sum(bill.amount for bill in bills)
        
        # Convert to daily burn (assume 30 days per month)
        daily_burn = total_monthly_bills / Decimal('30')
        
        if daily_burn > 0:
            return int(total_cash / daily_burn)
        
        return 0
    
    def _get_hygiene_flags(self, advisor_id: str, business_id: str) -> List[str]:
        """Get hygiene flags for data quality issues."""
        # This would integrate with the sync orchestrator to get hygiene flags
        # For now, return empty list
        return []
    
    def _calculate_data_quality_score(self, advisor_id: str, business_id: str) -> int:
        """Calculate data quality score (0-100)."""
        # This would analyze data completeness, accuracy, etc.
        # For now, return a placeholder score
        return 85
    
    def _generate_recommendations(self, console_data: Dict[str, Any]) -> List[str]:
        """Generate business recommendations based on console data."""
        recommendations = []
        
        runway_days = console_data.get("runway_days", 0)
        bills_due_this_week = console_data.get("bills_due_this_week", 0)
        
        if runway_days < 30:
            recommendations.append("Low cash runway - consider accelerating receivables")
        
        if bills_due_this_week > 5:
            recommendations.append("High number of bills due this week - review payment schedule")
        
        if not recommendations:
            recommendations.append("Financial position looks healthy")
        
        return recommendations
    
    def _bill_to_dict(self, bill: Bill) -> Dict[str, Any]:
        """Convert Bill domain object to dictionary."""
        return {
            "bill_id": bill.bill_id,
            "vendor_name": bill.vendor_name or "Unknown Vendor",
            "due_date": bill.due_date.isoformat() if bill.due_date else None,
            "amount": str(bill.amount),
            "status": bill.status,
            "days_until_due": self._calculate_days_until_due(bill.due_date) if bill.due_date else None
        }
    
    def _calculate_days_until_due(self, due_date: date) -> int:
        """Calculate days until due date."""
        today = date.today()
        return (due_date - today).days
