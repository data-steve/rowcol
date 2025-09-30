"""
Smart AR Adjustment Service for Oodaloo

PURPOSE: Intelligent credit memo management for business owners
- Smart credit memo creation for overpayments and adjustments
- Automatic runway impact calculations  
- Simple approval rules for high-value adjustments
- Clear insights: "This credit reduces next month's AR by $500"

DOMAIN DECISION: AR (not AP) because:
1. Test uses `invoice_id` parameter → customer invoices → AR domain
2. Smart AR needs credit memos for partial payment handling
3. Integration with collections: stop reminders when partial payment + credit memo created
4. Runway impact is about AR collection timing, not AP payment timing

SCOPE: Oodaloo Phase 2 Smart AR (single business owner)
NOT: Multi-client allocation, complex workflows (that's RowCol complexity)

This is CORE Smart AR functionality - reducing cognitive load around
customer payment adjustments and their runway impact.
"""

from sqlalchemy.orm import Session
from domains.core.services.base_service import TenantAwareService
from typing import Optional

class AdjustmentService(TenantAwareService):
    """
    Smart AR Adjustment Service for Oodaloo business owners.
    
    Provides intelligent credit memo management with runway impact insights.
    """
    
    def __init__(self, db: Session, business_id: Optional[str] = None, validate_business: bool = True):
        if business_id:
            super().__init__(db, business_id, validate_business)
        else:
            # Legacy compatibility for tests that don't provide business_id
            self.db = db
            self.business_id = None
            self.business = None
    
    def create_credit_memo(self, business_id: str, invoice_id: str, amount: float, reason: str):
        """
        Create a smart credit memo with automatic approval rules and runway impact.
        
        Smart Features:
        - Automatic approval for amounts < $1000 (reduces cognitive load)
        - High-value amounts flagged for review (risk management)
        - Runway impact calculation (shows cash flow effect)
        - Clear reason tracking for business insights
        """
        # Smart approval logic - TODO: Implement real approval workflow
        # For now, raise NotImplementedError to prevent fake status updates
        raise NotImplementedError(
            "Credit memo approval workflow not implemented. "
            "This requires real approval logic based on business rules, "
            "not just amount thresholds. See build_plan_v5.md Phase 2: Smart AR."
        )
        
        # Calculate runway impact (Phase 2 enhancement)
        runway_impact_days = self._calculate_runway_impact(amount)
        
        # Smart credit memo object
        class SmartCreditMemo:
            def __init__(self, business_id: str, amount: float, reason: str, status: str, runway_impact_days: int):
                self.business_id = business_id
                self.amount = amount
                self.reason = reason
                self.status = status
                self.runway_impact_days = runway_impact_days
                self.insight = f"This credit reduces your AR by ${amount:,.2f}, protecting {runway_impact_days} days of runway"
        
        return SmartCreditMemo(business_id, amount, reason, status, runway_impact_days)
    
    def _calculate_runway_impact(self, credit_amount: float) -> int:
        """
        Calculate how many days of runway this credit memo protects.
        
        Phase 2: Integrate with actual runway calculations
        Phase 1: Simple approximation for testing
        """
        # Simple approximation: $1000 credit = 1 day runway protection
        # Phase 2: Use actual business burn rate from runway service
        return max(1, int(credit_amount / 1000))

# TODO: Phase 2 Smart AR Enhancements
# - Integrate with actual runway calculations from RunwayService
# - Add overpayment detection and automatic credit memo suggestions
# - Smart categorization of credit reasons (refund, discount, error correction)
# - Integration with payment matching service

# TODO: Phase 3 Smart AR Advanced Features  
# - Predictive credit memo suggestions based on payment patterns
# - Integration with customer payment profiles
# - Automated follow-up for high-value credits needing review

# PARKED for RowCol:
# - Multi-client credit memo allocation
# - Complex approval workflows for CAS firms
# - Advanced audit trails and compliance reporting
# - Integration with third-party accounting systems