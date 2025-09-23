"""
Payment Priority Intelligence Service

This service provides intelligence for prioritizing payments based on various factors
such as due dates, vendor relationships, and cash flow considerations.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from domains.core.services.base_service import TenantAwareService
from domains.ap.models.bill import Bill, BillStatus
from domains.ap.models.vendor import Vendor
from config.business_rules.payment_rules import PaymentRules

logger = logging.getLogger(__name__)

class PaymentPriorityIntelligenceService(TenantAwareService):
    """
    Service for determining payment priorities based on business rules and intelligence.
    """
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        logger.info(f"Initialized PaymentPriorityIntelligenceService for business {business_id}")

    def prioritize_bills_for_payment(self, bills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize bills for payment based on multiple factors.
        
        Args:
            bills: List of bill dictionaries to prioritize
        
        Returns:
            List of bill dictionaries with added priority field
        """
        try:
            prioritized_bills = []
            for bill in bills:
                priority_score = self.calculate_payment_priority_score(bill)
                bill['priority_score'] = priority_score
                bill['priority'] = self.determine_priority_level(priority_score)
                prioritized_bills.append(bill)
            
            # Sort by priority score descending (higher score = higher priority)
            return sorted(prioritized_bills, key=lambda x: x['priority_score'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to prioritize bills: {e}")
            return []

    def calculate_payment_priority_score(self, bill: Dict[str, Any]) -> float:
        """
        Calculate a priority score for a bill based on multiple factors.
        Higher score means higher payment priority.
        
        Args:
            bill: Dictionary containing bill data
        
        Returns:
            float: Priority score (0-100)
        """
        score = 0.0
        
        # Due date urgency factor
        if bill.get('due_date'):
            try:
                due_date = datetime.fromisoformat(bill['due_date']) if isinstance(bill['due_date'], str) else bill['due_date']
                days_until_due = (due_date - datetime.now()).days
                if days_until_due < 0:
                    score += 30.0  # Overdue bills get highest boost
                    score += abs(days_until_due) * 1.5  # More overdue = higher priority
                elif days_until_due < 7:
                    score += 20.0  # Due within a week
                elif days_until_due < 14:
                    score += 10.0  # Due within two weeks
            except Exception as e:
                logger.error(f"Error calculating due date urgency for bill {bill.get('qbo_id')}: {e}")
        
        # Amount factor - high amounts get slightly higher priority
        amount = bill.get('amount', 0.0)
        if amount > PaymentRules.HIGH_AMOUNT_THRESHOLD:
            score += 10.0
        elif amount > PaymentRules.HIGH_AMOUNT_THRESHOLD / 2:
            score += 5.0
        
        # Vendor relationship factor - will need vendor data
        # This is a placeholder for when we integrate vendor reliability scores
        if bill.get('vendor_id'):
            vendor = self.db.query(Vendor).filter(
                Vendor.vendor_id == bill['vendor_id'],
                Vendor.business_id == self.business_id
            ).first()
            if vendor and getattr(vendor, 'is_critical', False):
                score += 15.0
            if vendor and getattr(vendor, 'payment_reliability_score', 0) is not None:
                reliability_score = getattr(vendor, 'payment_reliability_score', 0)
                if reliability_score >= PaymentRules.HIGH_RELIABILITY_THRESHOLD:
                    score += 5.0
        
        return min(score, 100.0)

    def determine_priority_level(self, score: float) -> str:
        """
        Determine priority level based on score.
        
        Args:
            score: Priority score (0-100)
        
        Returns:
            str: Priority level ('urgent', 'high', 'medium', 'low')
        """
        if score >= 60.0:
            return 'urgent'
        elif score >= 40.0:
            return 'high'
        elif score >= 20.0:
            return 'medium'
        else:
            return 'low'

    def get_payment_ready_bills(self, max_amount: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get bills that are ready for payment, prioritized.
        
        Args:
            max_amount: Maximum total amount to consider for payment (optional)
        
        Returns:
            List of prioritized bill dictionaries
        """
        try:
            bills = self.db.query(Bill).filter(
                Bill.business_id == self.business_id,
                Bill.status.in_([BillStatus.APPROVED, 'approved'])
            ).all()
            
            bill_dicts = [
                {
                    'qbo_id': bill.qbo_bill_id,
                    'amount': float(bill.amount_cents / 100) if bill.amount_cents else 0.0,
                    'due_date': bill.due_date.isoformat() if bill.due_date else None,
                    'vendor_id': bill.vendor_id,
                    'status': bill.status
                }
                for bill in bills
            ]
            
            prioritized = self.prioritize_bills_for_payment(bill_dicts)
            
            if max_amount is not None:
                total = 0.0
                filtered = []
                for bill in prioritized:
                    if total + bill['amount'] <= max_amount:
                        filtered.append(bill)
                        total += bill['amount']
                    else:
                        break
                return filtered
            
            return prioritized
        except Exception as e:
            logger.error(f"Failed to get payment-ready bills: {e}")
            return []
