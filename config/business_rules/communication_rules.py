"""
Communication Business Rules

Centralized rules for email frequency, contact preferences, and automated
communication workflows for collections and customer engagement.

**Business Context**:
Balance effective collection communication with customer relationship preservation.
Over-communication damages relationships; under-communication reduces collections.

**Industry Standards**:
- Daily: Emergency collections only
- Weekly: Standard past-due follow-up  
- Monthly: Maintenance communication
"""

class CommunicationRules:
    """
    Business rules for customer communication frequency and preferences.
    
    **Service Philosophy**: 
    Oodaloo enables smart collections that preserve customer relationships
    while maintaining effective cash flow management.
    """
    
    # ==================== EMAIL FREQUENCY LIMITS ====================
    # Industry Best Practice: Respect customer communication preferences
    # Source: Collections industry standards for B2B service businesses
    
    FREQUENCY_DAILY_MIN_DAYS = 1          # Daily = minimum 1 day between emails
    FREQUENCY_WEEKLY_MIN_DAYS = 7         # Weekly = minimum 7 days between emails  
    FREQUENCY_MONTHLY_MIN_DAYS = 30       # Monthly = minimum 30 days between emails
    
    # Default communication schedules by customer tier
    DEFAULT_ENTERPRISE_FREQUENCY = "weekly"    # Enterprise customers: weekly max
    DEFAULT_SMB_FREQUENCY = "weekly"           # SMB customers: weekly max
    DEFAULT_INDIVIDUAL_FREQUENCY = "monthly"  # Individual customers: monthly max
    
    # ==================== COLLECTION COMMUNICATION ESCALATION ====================
    # Progressive communication strategy for past-due accounts
    
    # Phase 1: Gentle Reminders (0-30 days past due)
    GENTLE_REMINDER_FREQUENCY = "weekly"
    GENTLE_REMINDER_MAX_ATTEMPTS = 2
    GENTLE_REMINDER_TONE = "friendly"
    
    # Phase 2: Formal Notices (31-60 days past due)  
    FORMAL_NOTICE_FREQUENCY = "weekly"
    FORMAL_NOTICE_MAX_ATTEMPTS = 3
    FORMAL_NOTICE_TONE = "professional"
    
    # Phase 3: Final Demands (61-90 days past due)
    FINAL_DEMAND_FREQUENCY = "weekly" 
    FINAL_DEMAND_MAX_ATTEMPTS = 2
    FINAL_DEMAND_TONE = "urgent"
    
    # Phase 4: Escalation (90+ days past due)
    ESCALATION_FREQUENCY = "immediate"     # Hand-off to manual review
    ESCALATION_THRESHOLD_DAYS = 90
    
    # ==================== COMMUNICATION CHANNEL PREFERENCES ====================
    # Multi-channel communication strategy
    
    # Channel priority order (most to least preferred)
    CHANNEL_PRIORITY = ["email", "phone", "mail", "text"]
    
    # Channel-specific rules
    EMAIL_MAX_PER_WEEK = 2                # Maximum emails per week per customer
    PHONE_MAX_PER_WEEK = 1               # Maximum calls per week per customer  
    TEXT_REQUIRES_CONSENT = True         # SMS requires explicit opt-in
    
    # Business hours for phone communication
    PHONE_HOURS_START = 9                # 9 AM
    PHONE_HOURS_END = 17                 # 5 PM  
    PHONE_TIMEZONE = "business_local"    # Use customer's business timezone
    
    # ==================== RELATIONSHIP PRESERVATION RULES ====================
    # Maintain customer relationships while collecting effectively
    
    # Customer value thresholds (modify communication based on customer value)
    HIGH_VALUE_CUSTOMER_THRESHOLD = 50000    # $50k+ annual revenue = high value
    STRATEGIC_CUSTOMER_THRESHOLD = 100000    # $100k+ annual revenue = strategic
    
    # High-value customer communication adjustments
    HIGH_VALUE_FREQUENCY_REDUCTION = 0.5     # 50% less frequent communication
    STRATEGIC_MANUAL_REVIEW_REQUIRED = True  # Strategic customers require manual review
    
    # Relationship health indicators
    RECENT_PAYMENT_GRACE_DAYS = 7            # Recent payment = 7 day communication pause
    NEW_CUSTOMER_GRACE_PERIOD_DAYS = 45      # New customers get 45-day grace period
    
    # ==================== AUTOMATION LIMITS ====================
    # Prevent over-automation and maintain human oversight
    
    MAX_AUTOMATED_ATTEMPTS = 5              # Maximum automated emails before human review
    MANUAL_REVIEW_TRIGGERS = [
        "high_value_customer",
        "repeated_payment_issues", 
        "customer_complaint",
        "strategic_relationship"
    ]
    
    # Escalation criteria
    ESCALATE_TO_HUMAN_DAYS = 90             # 90+ days past due = human involvement
    ESCALATE_TO_LEGAL_DAYS = 120            # 120+ days past due = legal consideration
    ESCALATE_AMOUNT_THRESHOLD = 10000       # $10k+ = immediate human review
    
    # ==================== CONFIGURABLE PARAMETERS ====================
    # TODO: Make these configurable per business based on:
    # - Industry norms (creative agencies vs consulting vs development)
    # - Customer relationship strategy 
    # - Business size and resource constraints
    
    @classmethod
    def should_allow_communication(cls, customer_tier: str, days_since_contact: int, 
                                 frequency_preference: str) -> bool:
        """
        Determine if communication is allowed based on frequency rules and customer tier.
        
        **Business Logic**:
        Respects customer communication preferences while ensuring effective
        collections. Higher-tier customers get more respectful communication patterns.
        
        Args:
            customer_tier: "enterprise", "smb", "individual"
            days_since_contact: Days since last communication
            frequency_preference: "daily", "weekly", "monthly"
            
        Returns:
            True if communication is allowed, False otherwise
        """
        # Check frequency preference
        if frequency_preference == "daily" and days_since_contact < cls.FREQUENCY_DAILY_MIN_DAYS:
            return False
        elif frequency_preference == "weekly" and days_since_contact < cls.FREQUENCY_WEEKLY_MIN_DAYS:
            return False  
        elif frequency_preference == "monthly" and days_since_contact < cls.FREQUENCY_MONTHLY_MIN_DAYS:
            return False
            
        # Apply tier-specific adjustments
        if customer_tier == "enterprise":
            # Enterprise customers get more respectful communication
            return days_since_contact >= cls.FREQUENCY_WEEKLY_MIN_DAYS
        elif customer_tier == "strategic":
            # Strategic customers require manual approval
            return False  # Always requires human review
            
        return True
    
    @classmethod  
    def get_escalation_phase(cls, days_past_due: int) -> dict:
        """
        Get appropriate communication phase based on how past due the account is.
        
        Returns communication strategy including frequency, tone, and limits.
        """
        if days_past_due <= 30:
            return {
                "phase": "gentle_reminder",
                "frequency": cls.GENTLE_REMINDER_FREQUENCY,
                "max_attempts": cls.GENTLE_REMINDER_MAX_ATTEMPTS,
                "tone": cls.GENTLE_REMINDER_TONE,
                "requires_human_review": False
            }
        elif days_past_due <= 60:
            return {
                "phase": "formal_notice", 
                "frequency": cls.FORMAL_NOTICE_FREQUENCY,
                "max_attempts": cls.FORMAL_NOTICE_MAX_ATTEMPTS,
                "tone": cls.FORMAL_NOTICE_TONE,
                "requires_human_review": False
            }
        elif days_past_due <= 90:
            return {
                "phase": "final_demand",
                "frequency": cls.FINAL_DEMAND_FREQUENCY,
                "max_attempts": cls.FINAL_DEMAND_MAX_ATTEMPTS, 
                "tone": cls.FINAL_DEMAND_TONE,
                "requires_human_review": True
            }
        else:
            return {
                "phase": "escalation",
                "frequency": cls.ESCALATION_FREQUENCY,
                "max_attempts": 0,  # No automated attempts
                "tone": "manual",
                "requires_human_review": True
            }
