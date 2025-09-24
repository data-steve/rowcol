"""
Risk Assessment Business Rules

Centralized rules for customer and vendor risk scoring, credit assessment,
and relationship management decisions.

**Business Context**:
Service agencies need to assess both customer credit risk (for payment terms)
and vendor risk (for payment timing and relationship management).

**Industry Standards**:
- Credit scoring follows standard FICO-like methodology  
- Payment behavior is primary risk indicator
- Multiple risk factors must be considered together
"""

class RiskAssessmentRules:
    """
    Business rules for customer and vendor risk assessment.
    
    **Risk Philosophy**:
    Use data-driven risk assessment to optimize business relationships
    while protecting cash flow and minimizing bad debt exposure.
    """
    
    # ==================== CUSTOMER RISK ASSESSMENT ====================
    # Multi-factor customer credit risk scoring
    
    # Risk factor weights (must sum to 100%)
    CUSTOMER_RISK_WEIGHT_PAYMENT_RELIABILITY = 0.4    # 40% - most important
    CUSTOMER_RISK_WEIGHT_OUTSTANDING_BALANCE = 0.3    # 30% - exposure amount  
    CUSTOMER_RISK_WEIGHT_PAYMENT_RECENCY = 0.3        # 30% - recent behavior
    
    # Payment reliability risk buckets
    PAYMENT_RELIABILITY_EXCELLENT = 95                # 95%+ = minimal risk
    PAYMENT_RELIABILITY_GOOD = 80                     # 80-94% = low risk
    PAYMENT_RELIABILITY_FAIR = 60                     # 60-79% = medium risk
    PAYMENT_RELIABILITY_POOR = 40                     # 40-59% = high risk
    # Below 40% = critical risk
    
    # Outstanding balance risk thresholds
    BALANCE_RISK_CRITICAL = 20000                     # $20k+ = critical exposure
    BALANCE_RISK_HIGH = 10000                         # $10k-$20k = high exposure
    BALANCE_RISK_MEDIUM = 5000                        # $5k-$10k = medium exposure  
    BALANCE_RISK_LOW = 1000                           # $1k-$5k = low exposure
    # Below $1k = minimal exposure
    
    # Payment recency risk thresholds (days since last payment)
    PAYMENT_RECENCY_CRITICAL = 120                    # 120+ days = critical risk
    PAYMENT_RECENCY_HIGH = 90                         # 90-119 days = high risk
    PAYMENT_RECENCY_MEDIUM = 60                       # 60-89 days = medium risk
    PAYMENT_RECENCY_LOW = 30                          # 30-59 days = low risk
    # Below 30 days = minimal risk
    
    # Risk score thresholds
    CUSTOMER_RISK_LOW = 25                            # 0-25 = low risk customer
    CUSTOMER_RISK_MEDIUM = 50                         # 26-50 = medium risk customer
    CUSTOMER_RISK_HIGH = 75                           # 51-75 = high risk customer
    # 76-100 = critical risk customer
    
    # ==================== VENDOR RISK ASSESSMENT ====================
    # Vendor reliability and relationship risk scoring
    
    # Vendor reliability factors
    VENDOR_RELIABILITY_EXCELLENT = 90                 # 90+ = excellent vendor
    VENDOR_RELIABILITY_GOOD = 70                      # 70-89 = good vendor
    VENDOR_RELIABILITY_FAIR = 50                      # 50-69 = fair vendor
    VENDOR_RELIABILITY_POOR = 30                      # 30-49 = poor vendor
    # Below 30 = problematic vendor
    
    # Vendor relationship importance tiers
    VENDOR_TIER_STRATEGIC = "strategic"               # Critical to operations
    VENDOR_TIER_IMPORTANT = "important"               # Important but replaceable
    VENDOR_TIER_STANDARD = "standard"                 # Standard relationship
    VENDOR_TIER_COMMODITY = "commodity"               # Easily replaceable
    
    # ==================== RISK-BASED DECISION RULES ====================
    # How risk scores affect business decisions
    
    # Customer credit limit rules based on risk
    CREDIT_LIMIT_LOW_RISK_MULTIPLIER = 3.0            # Low risk = 3x monthly average
    CREDIT_LIMIT_MEDIUM_RISK_MULTIPLIER = 2.0         # Medium risk = 2x monthly average
    CREDIT_LIMIT_HIGH_RISK_MULTIPLIER = 1.0           # High risk = 1x monthly average
    CREDIT_LIMIT_CRITICAL_RISK_MULTIPLIER = 0.5       # Critical risk = 0.5x monthly average
    
    # Payment terms based on customer risk
    PAYMENT_TERMS_LOW_RISK = 45                       # Low risk = NET 45
    PAYMENT_TERMS_MEDIUM_RISK = 30                    # Medium risk = NET 30
    PAYMENT_TERMS_HIGH_RISK = 15                      # High risk = NET 15
    PAYMENT_TERMS_CRITICAL_RISK = 0                   # Critical risk = Payment on delivery
    
    # Collection strategy based on customer risk
    COLLECTION_FREQUENCY_LOW_RISK = "monthly"         # Low risk = monthly reminders
    COLLECTION_FREQUENCY_MEDIUM_RISK = "weekly"       # Medium risk = weekly follow-up
    COLLECTION_FREQUENCY_HIGH_RISK = "weekly"         # High risk = weekly calls
    COLLECTION_FREQUENCY_CRITICAL_RISK = "daily"      # Critical risk = daily contact
    
    # Vendor payment strategy based on reliability
    VENDOR_PAYMENT_STRATEGIC_EARLY = True             # Strategic vendors = pay early
    VENDOR_PAYMENT_IMPORTANT_ONTIME = True            # Important vendors = pay on time
    VENDOR_PAYMENT_STANDARD_OPTIMIZE = True           # Standard vendors = optimize timing
    VENDOR_PAYMENT_COMMODITY_DELAY = True             # Commodity vendors = can delay
    
    # ==================== RISK CALCULATION METHODS ====================
    
    @classmethod
    def calculate_customer_risk_score(cls, payment_reliability: float, 
                                    outstanding_balance: float, 
                                    days_since_payment: int) -> float:
        """
        Calculate comprehensive customer risk score.
        
        **Methodology**:
        Uses weighted multi-factor analysis based on credit industry standards.
        Higher score = higher risk.
        
        Args:
            payment_reliability: Historical payment rate (0-100)
            outstanding_balance: Current outstanding amount
            days_since_payment: Days since last payment
            
        Returns:
            Risk score (0-100, higher = more risky)
        """
        risk_score = 0.0
        
        # Payment reliability risk (40% weight)
        reliability_risk = (100 - payment_reliability) * cls.CUSTOMER_RISK_WEIGHT_PAYMENT_RELIABILITY
        risk_score += reliability_risk
        
        # Outstanding balance risk (30% weight)
        if outstanding_balance >= cls.BALANCE_RISK_CRITICAL:
            balance_risk = 30
        elif outstanding_balance >= cls.BALANCE_RISK_HIGH:
            balance_risk = 20
        elif outstanding_balance >= cls.BALANCE_RISK_MEDIUM:
            balance_risk = 15
        elif outstanding_balance >= cls.BALANCE_RISK_LOW:
            balance_risk = 10
        else:
            balance_risk = 0
        risk_score += balance_risk
        
        # Payment recency risk (30% weight)
        if days_since_payment >= cls.PAYMENT_RECENCY_CRITICAL:
            recency_risk = 30
        elif days_since_payment >= cls.PAYMENT_RECENCY_HIGH:
            recency_risk = 25
        elif days_since_payment >= cls.PAYMENT_RECENCY_MEDIUM:
            recency_risk = 20
        elif days_since_payment >= cls.PAYMENT_RECENCY_LOW:
            recency_risk = 15
        else:
            recency_risk = 0
        risk_score += recency_risk
        
        return min(risk_score, 100.0)
    
    @classmethod
    def get_risk_category(cls, risk_score: float) -> str:
        """
        Categorize risk score into business-friendly labels.
        
        Returns: "low", "medium", "high", or "critical"
        """
        if risk_score <= cls.CUSTOMER_RISK_LOW:
            return "low"
        elif risk_score <= cls.CUSTOMER_RISK_MEDIUM:
            return "medium"
        elif risk_score <= cls.CUSTOMER_RISK_HIGH:
            return "high"
        else:
            return "critical"
    
    @classmethod
    def get_recommended_credit_limit(cls, risk_score: float, 
                                   monthly_average_invoicing: float) -> float:
        """
        Calculate recommended credit limit based on risk assessment.
        
        **Business Logic**:
        Credit limits scaled by customer risk to minimize bad debt exposure
        while enabling business growth with good customers.
        """
        if risk_score <= cls.CUSTOMER_RISK_LOW:
            return monthly_average_invoicing * cls.CREDIT_LIMIT_LOW_RISK_MULTIPLIER
        elif risk_score <= cls.CUSTOMER_RISK_MEDIUM:
            return monthly_average_invoicing * cls.CREDIT_LIMIT_MEDIUM_RISK_MULTIPLIER
        elif risk_score <= cls.CUSTOMER_RISK_HIGH:
            return monthly_average_invoicing * cls.CREDIT_LIMIT_HIGH_RISK_MULTIPLIER
        else:
            return monthly_average_invoicing * cls.CREDIT_LIMIT_CRITICAL_RISK_MULTIPLIER
    
    @classmethod
    def get_recommended_payment_terms(cls, risk_score: float) -> int:
        """
        Get recommended payment terms (days) based on customer risk.
        
        Returns payment terms in days (e.g., 30 for NET 30).
        """
        if risk_score <= cls.CUSTOMER_RISK_LOW:
            return cls.PAYMENT_TERMS_LOW_RISK
        elif risk_score <= cls.CUSTOMER_RISK_MEDIUM:
            return cls.PAYMENT_TERMS_MEDIUM_RISK
        elif risk_score <= cls.CUSTOMER_RISK_HIGH:
            return cls.PAYMENT_TERMS_HIGH_RISK
        else:
            return cls.PAYMENT_TERMS_CRITICAL_RISK
    
    # ==================== CONFIGURABLE PARAMETERS ====================
    # TODO: Make these configurable per business based on:
    # - Industry risk tolerance
    # - Business cash flow patterns  
    # - Historical bad debt experience
    # - Customer relationship strategies
