"""
Payment Business Rules

Centralized business logic for AP payment decisions, vendor relationships,
and payment optimization strategies.

**Business Context**:
Service agencies need to optimize cash flow by timing payments strategically
while maintaining vendor relationships and avoiding late fees.

**Industry Standards**:
- NET 30 terms are standard for most vendors
- Early payment discounts typically 2/10 NET 30
- Large payments ($5k+) require additional approval
"""

class PaymentRules:
    """
    Business rules for AP payment decisions and vendor management.
    
    **Payment Philosophy**:
    Optimize cash runway while maintaining strategic vendor relationships
    and avoiding unnecessary fees or relationship damage.
    """
    
    # ==================== PAYMENT AMOUNT THRESHOLDS ====================
    # Risk management: Larger payments require additional scrutiny
    
    HIGH_AMOUNT_THRESHOLD = 5000.0         # $5k+ = high-value payment requiring approval
    CRITICAL_AMOUNT_THRESHOLD = 10000.0    # $10k+ = critical payment requiring multiple approvals
    AUTO_APPROVAL_THRESHOLD = 1000.0       # $1k and under = can be auto-approved
    
    # ==================== VENDOR RELIABILITY THRESHOLDS ====================
    # Vendor relationship management based on payment history and reliability
    
    HIGH_RELIABILITY_THRESHOLD = 80        # 80+ reliability score = trusted vendor
    MEDIUM_RELIABILITY_THRESHOLD = 60      # 60-79 = standard vendor
    LOW_RELIABILITY_THRESHOLD = 40         # 40-59 = requires monitoring
    # Below 40 = high-risk vendor requiring special handling
    
    # ==================== PAYMENT TIMING OPTIMIZATION ====================
    # Strategic payment timing to optimize cash flow
    
    # Early payment discount thresholds
    EARLY_PAYMENT_DISCOUNT_MIN = 0.02      # 2% minimum discount to consider early payment
    EARLY_PAYMENT_DISCOUNT_OPTIMAL = 0.03  # 3%+ discount = always take early payment
    EARLY_PAYMENT_MAX_DAYS = 10            # Take discounts only if 10+ days early
    
    # Late payment risk thresholds  
    LATE_PAYMENT_WARNING_DAYS = 3          # Warn if payment due within 3 days
    LATE_PAYMENT_CRITICAL_DAYS = 1         # Critical if payment due within 1 day
    LATE_PAYMENT_FEE_THRESHOLD = 0.015     # 1.5% late fee = prioritize payment
    
    # Cash flow optimization
    CASH_RUNWAY_CRITICAL_DAYS = 30         # If runway < 30 days, optimize all payments
    CASH_RUNWAY_WARNING_DAYS = 60          # If runway < 60 days, optimize large payments
    
    # ==================== VENDOR RELATIONSHIP TIERS ====================
    # Different payment strategies based on vendor importance
    
    # Strategic vendors (critical to operations)
    STRATEGIC_VENDOR_EARLY_PAYMENT = True          # Always pay strategic vendors early
    STRATEGIC_VENDOR_DISCOUNT_MIN = 0.01           # Take even 1% discounts for strategic vendors
    STRATEGIC_VENDOR_LATE_TOLERANCE = 0            # Never pay strategic vendors late
    
    # Standard vendors (regular operations)
    STANDARD_VENDOR_EARLY_PAYMENT = False          # Only if good discount
    STANDARD_VENDOR_DISCOUNT_MIN = 0.02            # Require 2%+ discount
    STANDARD_VENDOR_LATE_TOLERANCE = 3             # Can be up to 3 days late if needed
    
    # Commodity vendors (easily replaceable)  
    COMMODITY_VENDOR_EARLY_PAYMENT = False         # Never pay early unless great discount
    COMMODITY_VENDOR_DISCOUNT_MIN = 0.03           # Require 3%+ discount
    COMMODITY_VENDOR_LATE_TOLERANCE = 7            # Can be up to 7 days late if needed
    
    # ==================== APPROVAL WORKFLOW RULES ====================
    # Who can approve what level of payments
    
    # Auto-approval rules
    AUTO_APPROVE_CONDITIONS = {
        "amount_under": AUTO_APPROVAL_THRESHOLD,
        "vendor_reliability_over": HIGH_RELIABILITY_THRESHOLD,
        "within_payment_terms": True,
        "sufficient_cash_runway": CASH_RUNWAY_WARNING_DAYS
    }
    
    # Manual approval requirements
    REQUIRE_APPROVAL_CONDITIONS = [
        "amount_over_threshold",      # Amount > AUTO_APPROVAL_THRESHOLD
        "low_vendor_reliability",     # Vendor reliability < HIGH_RELIABILITY_THRESHOLD
        "outside_payment_terms",      # Paying very early or very late
        "low_cash_runway",           # Cash runway < CASH_RUNWAY_WARNING_DAYS
        "first_time_vendor",         # New vendor relationship
        "disputed_invoice"           # Invoice has been disputed
    ]
    
    # ==================== CASH FLOW OPTIMIZATION RULES ====================
    # Dynamic payment timing based on cash position
    
    @classmethod
    def get_payment_priority_score(cls, amount: float, vendor_reliability: float, 
                                 days_until_due: int, available_discount: float = 0.0) -> float:
        """
        Calculate payment priority score (0-100, higher = pay sooner).
        
        **Business Logic**:
        Balances multiple factors to optimize cash flow:
        - Large amounts get lower priority (preserve cash)
        - Reliable vendors get higher priority (relationship preservation)
        - Near-due payments get higher priority (avoid late fees)
        - Good discounts get higher priority (capture savings)
        
        Args:
            amount: Payment amount in dollars
            vendor_reliability: Vendor reliability score (0-100)
            days_until_due: Days until payment due date
            available_discount: Early payment discount percentage (0.0-1.0)
            
        Returns:
            Priority score (0-100, higher = pay sooner)
        """
        score = 50.0  # Base score
        
        # Amount factor (larger amounts = lower priority)
        if amount > cls.CRITICAL_AMOUNT_THRESHOLD:
            score -= 20
        elif amount > cls.HIGH_AMOUNT_THRESHOLD:
            score -= 10
        elif amount < cls.AUTO_APPROVAL_THRESHOLD:
            score += 10
            
        # Vendor reliability factor
        if vendor_reliability > cls.HIGH_RELIABILITY_THRESHOLD:
            score += 15
        elif vendor_reliability < cls.LOW_RELIABILITY_THRESHOLD:
            score -= 10
            
        # Due date urgency factor
        if days_until_due <= cls.LATE_PAYMENT_CRITICAL_DAYS:
            score += 30  # Pay immediately
        elif days_until_due <= cls.LATE_PAYMENT_WARNING_DAYS:
            score += 20  # Pay soon
        elif days_until_due > 30:
            score -= 10  # Can wait
            
        # Early payment discount factor
        if available_discount >= cls.EARLY_PAYMENT_DISCOUNT_OPTIMAL:
            score += 25  # Great discount, pay early
        elif available_discount >= cls.EARLY_PAYMENT_DISCOUNT_MIN:
            score += 15  # Good discount, consider early payment
            
        return max(0, min(100, score))
    
    @classmethod
    def should_auto_approve(cls, amount: float, vendor_reliability: float, 
                          days_until_due: int, cash_runway_days: int) -> bool:
        """
        Determine if payment can be auto-approved based on business rules.
        
        Returns True if payment meets all auto-approval criteria.
        """
        return (
            amount <= cls.AUTO_APPROVAL_THRESHOLD and
            vendor_reliability >= cls.HIGH_RELIABILITY_THRESHOLD and
            1 <= days_until_due <= 30 and  # Within reasonable payment window
            cash_runway_days >= cls.CASH_RUNWAY_WARNING_DAYS
        )
    
    # ==================== CONFIGURABLE PARAMETERS ====================
    # TODO: Make these configurable per business based on:
    # - Industry payment norms
    # - Business size and cash flow patterns
    # - Vendor relationship strategies
    # - Risk tolerance levels
