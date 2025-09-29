"""
AR Collections Service

Business logic for managing collections, reminders, and overdue invoice tracking.
Integrates with SmartSyncService for QBO data and supports runway impact analysis.

This service handles:
- Overdue invoice identification and prioritization
- Collection reminder sending and tracking
- Aging bucket analysis
- Customer payment history and reliability scoring
- Integration with communication systems (email, SMS)

Business Context:
Collections is critical for cash flow management. This service provides:
- Automated overdue detection with aging buckets (30/60/90+ days)
- Priority scoring based on amount, customer history, and business rules
- Communication tracking to avoid over-contacting customers
- Integration with runway calculations to show cash flow impact
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime

from infra.qbo.smart_sync import SmartSyncService
from domains.core.services.base_service import TenantAwareService
from common.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class CollectionsService(TenantAwareService):
    """Service for managing AR collections and overdue invoice workflows."""
    
    def __init__(self, db: Session, business_id: str = None):
        super().__init__(db, business_id)
        self.smart_sync = SmartSyncService(business_id, "", db) if business_id else None
    
    async def get_overdue_invoices(self, days_overdue_min: int = 1, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get overdue invoices with priority scoring and collection recommendations.
        
        Args:
            days_overdue_min: Minimum days overdue to include
            priority: Filter by priority level (critical, high, medium, low)
        
        Returns:
            List of overdue invoice dictionaries with collection metadata
        """
        try:
            if not self.smart_sync:
                raise ValidationError("SmartSyncService not available - business_id required")
            
            # Use SmartSyncService for data retrieval
            # QBOClient import removed - using SmartSyncService directly
            
            # Get invoices using SmartSyncService
            invoices = await self.smart_sync.get_invoices()
            
            today = datetime.utcnow()
            overdue_invoices = []
            
            for invoice_data in invoices:
                balance = float(invoice_data.get("Balance", 0))
                if balance <= 0:
                    continue  # Skip paid invoices
                
                due_date_str = invoice_data.get("DueDate")
                if not due_date_str:
                    continue
                
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_overdue = (today - due_date).days
                    
                    if days_overdue < days_overdue_min:
                        continue
                    
                    # Calculate priority and collection score
                    invoice_priority = self._calculate_invoice_priority(balance, days_overdue, invoice_data)
                    
                    # Filter by priority if specified
                    if priority and invoice_priority != priority:
                        continue
                    
                    # Get customer information
                    customer_ref = invoice_data.get("CustomerRef", {})
                    customer_id = customer_ref.get("value")
                    customer_name = customer_ref.get("name", "Unknown")
                    
                    # Build overdue invoice record
                    overdue_invoice = {
                        "invoice_id": invoice_data.get("Id"),
                        "invoice_number": invoice_data.get("DocNumber"),
                        "customer": {
                            "id": customer_id,
                            "name": customer_name,
                            "email": self._get_customer_email(customer_id),
                            "phone": self._get_customer_phone(customer_id)
                        },
                        "amount": balance,
                        "original_amount": float(invoice_data.get("TotalAmt", balance)),
                        "issue_date": invoice_data.get("TxnDate"),
                        "due_date": due_date_str,
                        "days_overdue": days_overdue,
                        "priority": invoice_priority,
                        "collection_score": self._calculate_collection_score(balance, days_overdue, customer_id),
                        "last_reminder_sent": None,  # TODO: Track in database
                        "reminder_count": 0,         # TODO: Track in database
                        "recommended_action": self._get_recommended_action(days_overdue, 0),  # TODO: Use actual reminder count
                        "contact_attempts": []       # TODO: Track in database
                    }
                    
                    overdue_invoices.append(overdue_invoice)
                    
                except Exception as e:
                    logger.warning(f"Error processing invoice {invoice_data.get('Id')}: {str(e)}")
                    continue
            
            # Sort by collection score (highest priority first)
            overdue_invoices.sort(key=lambda x: x["collection_score"], reverse=True)
            
            return overdue_invoices
            
        except Exception as e:
            logger.error(f"Failed to get overdue invoices: {str(e)}")
            raise ValidationError(f"Failed to retrieve overdue invoices: {str(e)}")
    
    def send_reminder(self, invoice_id: str, reminder_type: str = "email", custom_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a collection reminder for an overdue invoice.
        
        Args:
            invoice_id: QBO invoice ID
            reminder_type: Type of reminder (email, sms, phone_call)
            custom_message: Custom message to include in reminder
        
        Returns:
            Dictionary with reminder details and status
        """
        try:
            # Get invoice details
            overdue_invoices = self.get_overdue_invoices(days_overdue_min=0)
            target_invoice = next((inv for inv in overdue_invoices if inv["invoice_id"] == invoice_id), None)
            
            if not target_invoice:
                raise ValidationError(f"Invoice {invoice_id} not found or not overdue")
            
            # TODO: Implement actual reminder sending logic
            # This would integrate with email service, SMS service, etc.
            
            raise NotImplementedError(
                "Collections reminder sending is not yet implemented. "
                "This feature requires integration with email service and QBO collections API. "
                "See build_plan_v5.md Phase 2: Smart AR & Collections for implementation plan."
            )
            
            # Record activity for smart sync
            if self.smart_sync:
                self.smart_sync.record_user_activity("collection_reminder_sent")
            
            return reminder_result
            
        except Exception as e:
            logger.error(f"Failed to send reminder for invoice {invoice_id}: {str(e)}")
            raise ValidationError(f"Failed to send reminder: {str(e)}")
    
    async def get_aging_report(self) -> Dict[str, Any]:
        """
        Generate aging report with buckets and totals.
        
        Returns:
            Dictionary with aging buckets and summary statistics
        """
        try:
            if not self.smart_sync:
                raise ValidationError("SmartSyncService not available - business_id required")
            
            # Use SmartSyncService for data retrieval
            # QBOClient import removed - using SmartSyncService directly
            
            # Get invoices using SmartSyncService
            invoices = await self.smart_sync.get_invoices()
            
            today = datetime.utcnow()
            aging_buckets = {
                "current": {"count": 0, "amount": 0, "invoices": []},
                "1_30_days": {"count": 0, "amount": 0, "invoices": []},
                "31_60_days": {"count": 0, "amount": 0, "invoices": []},
                "61_90_days": {"count": 0, "amount": 0, "invoices": []},
                "over_90_days": {"count": 0, "amount": 0, "invoices": []}
            }
            
            total_outstanding = 0
            
            for invoice_data in invoices:
                balance = float(invoice_data.get("Balance", 0))
                if balance <= 0:
                    continue  # Skip paid invoices
                
                due_date_str = invoice_data.get("DueDate")
                if not due_date_str:
                    continue
                
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_overdue = (today - due_date).days
                    
                    invoice_summary = {
                        "invoice_id": invoice_data.get("Id"),
                        "customer": invoice_data.get("CustomerRef", {}).get("name", "Unknown"),
                        "amount": balance,
                        "days_overdue": days_overdue
                    }
                    
                    # Categorize into aging buckets
                    if days_overdue <= 0:
                        bucket = "current"
                    elif days_overdue <= 30:
                        bucket = "1_30_days"
                    elif days_overdue <= 60:
                        bucket = "31_60_days"
                    elif days_overdue <= 90:
                        bucket = "61_90_days"
                    else:
                        bucket = "over_90_days"
                    
                    aging_buckets[bucket]["count"] += 1
                    aging_buckets[bucket]["amount"] += balance
                    aging_buckets[bucket]["invoices"].append(invoice_summary)
                    
                    total_outstanding += balance
                    
                except Exception as e:
                    logger.warning(f"Error processing invoice {invoice_data.get('Id')} for aging: {str(e)}")
                    continue
            
            return {
                "aging_buckets": aging_buckets,
                "summary": {
                    "total_outstanding": total_outstanding,
                    "total_overdue": sum(bucket["amount"] for key, bucket in aging_buckets.items() if key != "current"),
                    "overdue_count": sum(bucket["count"] for key, bucket in aging_buckets.items() if key != "current"),
                    "current_count": aging_buckets["current"]["count"],
                    "current_amount": aging_buckets["current"]["amount"]
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate aging report: {str(e)}")
            raise ValidationError(f"Failed to generate aging report: {str(e)}")
    
    async def get_customer_payment_history(self, customer_id: str) -> Dict[str, Any]:
        """
        Get payment history and reliability score for a customer.
        
        Args:
            customer_id: QBO customer ID
        
        Returns:
            Dictionary with payment history and reliability metrics
        """
        try:
            if not self.smart_sync:
                raise ValidationError("SmartSyncService not available - business_id required")
            
            # Use SmartSyncService for data retrieval
            # QBOClient import removed - using SmartSyncService directly
            
            # Get invoices using SmartSyncService
            invoices = await self.smart_sync.get_invoices()
            
            customer_invoices = []
            total_invoiced = 0
            total_paid = 0
            payment_days = []
            
            for invoice_data in invoices:
                if invoice_data.get("CustomerRef", {}).get("value") != customer_id:
                    continue
                
                invoice_amount = float(invoice_data.get("TotalAmt", 0))
                balance = float(invoice_data.get("Balance", 0))
                paid_amount = invoice_amount - balance
                
                invoice_record = {
                    "invoice_id": invoice_data.get("Id"),
                    "amount": invoice_amount,
                    "balance": balance,
                    "paid_amount": paid_amount,
                    "issue_date": invoice_data.get("TxnDate"),
                    "due_date": invoice_data.get("DueDate"),
                    "is_paid": balance <= 0
                }
                
                customer_invoices.append(invoice_record)
                total_invoiced += invoice_amount
                total_paid += paid_amount
                
                # Calculate payment days for paid invoices
                if balance <= 0 and invoice_data.get("DueDate"):
                    # TODO: Get actual payment date from QBO payment records
                    # For now, estimate based on current data
                    pass
            
            # Calculate reliability metrics
            payment_rate = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0
            avg_payment_days = sum(payment_days) / len(payment_days) if payment_days else 0
            
            # Simple reliability score calculation
            reliability_score = min(100, payment_rate * 0.7 + (max(0, 30 - avg_payment_days) / 30) * 30)
            
            return {
                "customer_id": customer_id,
                "summary": {
                    "total_invoiced": total_invoiced,
                    "total_paid": total_paid,
                    "payment_rate_percent": round(payment_rate, 2),
                    "average_payment_days": round(avg_payment_days, 1),
                    "reliability_score": round(reliability_score, 1),
                    "invoice_count": len(customer_invoices)
                },
                "invoices": customer_invoices,
                "payment_behavior": self._analyze_payment_behavior(customer_invoices)
            }
            
        except Exception as e:
            logger.error(f"Failed to get customer payment history for {customer_id}: {str(e)}")
            raise ValidationError(f"Failed to retrieve customer payment history: {str(e)}")
    
    def _calculate_invoice_priority(self, amount: float, days_overdue: int, invoice_data: Dict) -> str:
        """Calculate priority level for an overdue invoice."""
        if days_overdue > 90 or amount > 5000:
            return "critical"
        elif days_overdue > 60 or amount > 2000:
            return "high"
        elif days_overdue > 30 or amount > 500:
            return "medium"
        else:
            return "low"
    
    def _calculate_collection_score(self, amount: float, days_overdue: int, customer_id: str) -> float:
        """Calculate collection priority score (0-100, higher = more urgent)."""
        # Base score from amount (0-40 points)
        amount_score = min(40, (amount / 1000) * 10)
        
        # Days overdue score (0-40 points)
        days_score = min(40, days_overdue * 0.5)
        
        # Customer reliability score (0-20 points)
        # TODO: Get actual customer reliability from payment history
        customer_score = 10  # Default neutral score
        
        return amount_score + days_score + customer_score
    
    def _get_recommended_action(self, days_overdue: int, reminder_count: int) -> str:
        """Get recommended collection action based on overdue days and reminder history."""
        if reminder_count == 0:
            return "send_first_reminder"
        elif days_overdue < 30:
            return "email_reminder"
        elif days_overdue < 60:
            return "phone_call"
        elif days_overdue < 90:
            return "formal_notice"
        else:
            return "collection_agency"
    
    def _generate_reminder_message(self, invoice: Dict, reminder_type: str) -> str:
        """Generate reminder message based on invoice details and type."""
        customer_name = invoice["customer"]["name"]
        amount = invoice["amount"]
        days_overdue = invoice["days_overdue"]
        
        if reminder_type == "email":
            return f"Dear {customer_name}, your invoice for ${amount:.2f} is {days_overdue} days overdue. Please remit payment at your earliest convenience."
        elif reminder_type == "sms":
            return f"Reminder: Invoice ${amount:.2f} is {days_overdue} days overdue. Please contact us to arrange payment."
        else:
            return f"Collection reminder for {customer_name}: ${amount:.2f}, {days_overdue} days overdue"
    
    def _record_reminder_sent(self, invoice_id: str, reminder_type: str, reminder_result: Dict):
        """Record reminder in database for tracking purposes."""
        # TODO: Implement database tracking of collection activities
        logger.info(f"Reminder sent for invoice {invoice_id}: {reminder_type}")
    
    def _get_customer_email(self, customer_id: str) -> Optional[str]:
        """Get customer email from database."""
        from domains.ar.services.customer import CustomerService
        customer_service = CustomerService(self.db, self.business_id)
        return customer_service.get_customer_email(customer_id)
    
    def _get_customer_phone(self, customer_id: str) -> Optional[str]:
        """Get customer phone from database."""
        from domains.ar.services.customer import CustomerService
        customer_service = CustomerService(self.db, self.business_id)
        return customer_service.get_customer_phone(customer_id)
    
    def _analyze_payment_behavior(self, invoices: List[Dict]) -> Dict[str, Any]:
        """Analyze customer payment behavior patterns."""
        paid_invoices = [inv for inv in invoices if inv["is_paid"]]
        overdue_invoices = [inv for inv in invoices if not inv["is_paid"]]
        
        return {
            "payment_pattern": "consistent" if len(paid_invoices) > len(overdue_invoices) else "irregular",
            "typical_payment_delay": "on_time",  # TODO: Calculate from actual payment dates
            "risk_level": "low" if len(overdue_invoices) == 0 else "medium"
        }
