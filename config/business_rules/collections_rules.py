"""
Collections Business Rules

Centralized business logic for AR collections, customer risk assessment,
and payment reliability scoring.

**Business Context**: 
Service agencies ($1M-$5M revenue) typically have 30-60 day payment terms
with customers ranging from small businesses to enterprise clients.

**Industry Standards**:
- Payment reliability >95% = Excellent credit risk
- 30+ days past due = Collection action needed  
- 90+ days past due = High risk customer
"""

class CollectionsRules:
    """
    Business rules for AR collections and customer risk assessment.
    
    Based on industry standards for service agency collections.
    """
    
    # ==================== PAYMENT RELIABILITY SCORING ====================
    # Industry Standard: Payment Rate to Credit Score Mapping
    # Source: Credit scoring models used by major AR platforms
    
    PAYMENT_RELIABILITY_EXCELLENT = 95    # 95%+ payment rate = excellent (90-100 score)
    PAYMENT_RELIABILITY_GOOD = 80         # 80-94% payment rate = good (70-89 score)  
    PAYMENT_RELIABILITY_FAIR = 60         # 60-79% payment rate = fair (40-69 score)
    # Below 60% = Poor credit risk (0-39 score)
    
    # Score calculation factors
    RELIABILITY_WEIGHT_95_PLUS = 90       # Base score for excellent payers
    RELIABILITY_WEIGHT_80_PLUS = 70       # Base score for good payers  
    RELIABILITY_WEIGHT_60_PLUS = 40       # Base score for fair payers
    RELIABILITY_MULTIPLIER_EXCELLENT = 1.0   # (rate - 95) * 1.0 for bonus
    RELIABILITY_MULTIPLIER_GOOD = 1.33       # (rate - 80) * 1.33 for scaling
    RELIABILITY_MULTIPLIER_FAIR = 1.5        # (rate - 60) * 1.5 for scaling
    RELIABILITY_MULTIPLIER_POOR = 0.67       # rate * 0.67 for penalty
    
    # ==================== COLLECTION PRIORITY SCORING ====================
    # Business Logic: Prioritize collections based on amount, age, and reliability
    
    # Outstanding balance thresholds (30-point scale)
    BALANCE_HIGH_PRIORITY = 10000         # $10k+ = 30 points (highest priority)
    BALANCE_MEDIUM_PRIORITY = 5000        # $5k-$10k = 20 points
    BALANCE_LOW_PRIORITY = 1000           # $1k-$5k = 10 points
    # Below $1k = 0 points (lowest priority)
    
    BALANCE_POINTS_HIGH = 30
    BALANCE_POINTS_MEDIUM = 20  
    BALANCE_POINTS_LOW = 10
    
    # Days since last payment thresholds (25-point scale)
    PAYMENT_RECENCY_CRITICAL = 90         # 90+ days = 25 points (critical)
    PAYMENT_RECENCY_HIGH = 60             # 60-89 days = 20 points
    PAYMENT_RECENCY_MEDIUM = 30           # 30-59 days = 15 points
    # Below 30 days = 0 points
    
    PAYMENT_RECENCY_POINTS_CRITICAL = 25
    PAYMENT_RECENCY_POINTS_HIGH = 20
    PAYMENT_RECENCY_POINTS_MEDIUM = 15
    
    # ==================== RISK ASSESSMENT ====================
    # Multi-factor risk scoring for customer creditworthiness
    
    # Risk factor weights (must sum to 100%)
    RISK_WEIGHT_PAYMENT_RELIABILITY = 0.4    # 40% - most important factor
    RISK_WEIGHT_OUTSTANDING_BALANCE = 0.3    # 30% - financial exposure
    RISK_WEIGHT_PAYMENT_RECENCY = 0.3        # 30% - recent behavior
    
    # Outstanding balance risk thresholds
    RISK_BALANCE_CRITICAL = 20000         # $20k+ = 30 risk points
    RISK_BALANCE_HIGH = 10000             # $10k-$20k = 20 risk points
    RISK_BALANCE_MEDIUM = 5000            # $5k-$10k = 15 risk points
    RISK_BALANCE_LOW = 1000               # $1k-$5k = 10 risk points
    # Below $1k = 0 risk points
    
    RISK_POINTS_CRITICAL = 30
    RISK_POINTS_HIGH = 20
    RISK_POINTS_MEDIUM = 15  
    RISK_POINTS_LOW = 10
    
    # Payment recency risk thresholds  
    RISK_RECENCY_CRITICAL = 120           # 120+ days = 30 risk points
    RISK_RECENCY_HIGH = 90                # 90-119 days = 25 risk points
    RISK_RECENCY_MEDIUM = 60              # 60-89 days = 20 risk points
    RISK_RECENCY_LOW = 30                 # 30-59 days = 15 risk points
    # Below 30 days = 0 risk points
    
    RISK_RECENCY_POINTS_CRITICAL = 30
    RISK_RECENCY_POINTS_HIGH = 25
    RISK_RECENCY_POINTS_MEDIUM = 20
    RISK_RECENCY_POINTS_LOW = 15
    
    # ==================== CONFIGURABLE PARAMETERS ====================
    # TODO: Make these configurable per business based on industry/size
    
    # Collection schedule preferences
    DEFAULT_COLLECTION_SCHEDULE = "weekly"   # weekly, bi-weekly, monthly
    MAX_COLLECTION_ATTEMPTS = 3             # Before escalation
    
    # Industry-specific adjustments  
    # TODO: Adjust thresholds based on:
    # - Service agency vs product business
    # - Contract terms (NET 30 vs NET 60)
    # - Customer size (SMB vs Enterprise)
    
    @classmethod
    def get_payment_reliability_score(cls, payment_rate: float) -> float:
        """
        Calculate payment reliability score based on historical payment rate.
        
        **Business Logic**: 
        Uses industry-standard credit scoring methodology where payment
        rate directly correlates to creditworthiness.
        
        Args:
            payment_rate: Percentage of invoices paid (0-100)
            
        Returns:
            Reliability score (0-100, higher = more reliable)
        """
        if payment_rate >= cls.PAYMENT_RELIABILITY_EXCELLENT:
            return cls.RELIABILITY_WEIGHT_95_PLUS + (payment_rate - cls.PAYMENT_RELIABILITY_EXCELLENT) * cls.RELIABILITY_MULTIPLIER_EXCELLENT
        elif payment_rate >= cls.PAYMENT_RELIABILITY_GOOD:
            return cls.RELIABILITY_WEIGHT_80_PLUS + (payment_rate - cls.PAYMENT_RELIABILITY_GOOD) * cls.RELIABILITY_MULTIPLIER_GOOD
        elif payment_rate >= cls.PAYMENT_RELIABILITY_FAIR:
            return cls.RELIABILITY_WEIGHT_60_PLUS + (payment_rate - cls.PAYMENT_RELIABILITY_FAIR) * cls.RELIABILITY_MULTIPLIER_FAIR
        else:
            return payment_rate * cls.RELIABILITY_MULTIPLIER_POOR
