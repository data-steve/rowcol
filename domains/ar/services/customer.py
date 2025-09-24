"""
Customer Service - AR Customer Management with Payment History and Risk Scoring

This service handles customer business logic for accounts receivable management:
- Customer payment history tracking and reliability scoring
- Collection preferences and communication management
- Risk assessment and credit scoring calculations
- Collection contact scheduling and tracking
- Integration with QBO customer data
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from domains.ar.models.customer import Customer
from domains.core.services.base_service import TenantAwareService
from config.business_rules import CollectionsRules, CommunicationRules, RiskAssessmentRules

import logging

logger = logging.getLogger(__name__)

class CustomerService(TenantAwareService):
    """
    Service for managing AR customers and their payment behavior.
    
    Handles customer risk assessment, collection preferences, and payment history
    for effective accounts receivable management.
    """
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        self.db = db
    
    # ==================== SMART SYNC DATA METHODS ====================
    
    def get_active_customers(self) -> List[Dict[str, Any]]:
        """Get all active customers for digest/sync purposes."""
        try:
            customers = self.db.query(Customer).filter(
                Customer.business_id == self.business_id,
                Customer.is_active
            ).all()
            
            return [
                {
                    "qbo_id": customer.qbo_customer_id,
                    "name": customer.name,
                    "is_active": customer.is_active,
                    "balance": 0,  # Would need to calculate from unpaid invoices
                    "contact_info": {
                        "email": customer.email,
                        "phone": customer.phone
                    }
                }
                for customer in customers
            ]
        except Exception as e:
            logger.error(f"Failed to get active customers: {e}")
            return []
    
    def get_customers_for_digest(self) -> List[Dict[str, Any]]:
        """Get customers formatted for digest generation."""
        return self.get_active_customers()
    
    def calculate_collection_priority_score(self, customer: Customer) -> float:
        """
        Calculate collection priority score based on multiple factors.
        Higher score = higher priority for collections.
        
        Args:
            customer: Customer instance
            
        Returns:
            Priority score (0-100)
        """
        score = 0.0
        
        # Outstanding balance factor - uses centralized business rules
        balance = self.get_outstanding_balance(customer)
        if balance > CollectionsRules.BALANCE_HIGH_PRIORITY:
            score += CollectionsRules.BALANCE_POINTS_HIGH
        elif balance > CollectionsRules.BALANCE_MEDIUM_PRIORITY:
            score += CollectionsRules.BALANCE_POINTS_MEDIUM
        elif balance > CollectionsRules.BALANCE_LOW_PRIORITY:
            score += CollectionsRules.BALANCE_POINTS_LOW
        
        # Payment reliability factor (0-25 points, inverse)
        reliability_penalty = (100 - customer.payment_reliability_score) / 4
        score += reliability_penalty
        
        # Days since last payment factor - uses centralized business rules
        days_since_payment = self.get_days_since_last_payment(customer) or 0
        if days_since_payment > CollectionsRules.PAYMENT_RECENCY_CRITICAL:
            score += CollectionsRules.PAYMENT_RECENCY_POINTS_CRITICAL
        elif days_since_payment > CollectionsRules.PAYMENT_RECENCY_HIGH:
            score += CollectionsRules.PAYMENT_RECENCY_POINTS_HIGH
        elif days_since_payment > CollectionsRules.PAYMENT_RECENCY_MEDIUM:
            score += CollectionsRules.PAYMENT_RECENCY_POINTS_MEDIUM
        
        # Risk score factor (0-20 points)
        score += customer.risk_score / 5
        
        return min(score, 100.0)
    
    def get_outstanding_balance(self, customer: Customer) -> float:
        """Calculate outstanding balance (invoiced - paid)."""
        return customer.total_invoiced_ytd - customer.total_paid_ytd
    
    def get_days_since_last_payment(self, customer: Customer) -> Optional[int]:
        """Calculate days since last payment."""
        if customer.last_payment_date:
            return (datetime.utcnow() - customer.last_payment_date).days
        return None
    
    def update_payment_history(self, customer: Customer, payment_amount: float, payment_date: datetime = None):
        """
        Update customer payment history with new payment.
        
        Args:
            customer: Customer instance
            payment_amount: Amount of payment received
            payment_date: Date of payment (defaults to now)
        """
        if payment_date is None:
            payment_date = datetime.utcnow()
        
        # Update totals
        customer.total_paid_ytd += payment_amount
        customer.last_payment_date = payment_date
        
        # Recalculate payment reliability score
        self._recalculate_payment_reliability(customer)
        
        # Update risk assessment
        self._update_risk_assessment(customer)
        
        self.db.commit()
    
    def record_collection_contact(self, customer: Customer, contact_type: str, notes: str = None):
        """
        Record a collection contact attempt.
        
        Args:
            customer: Customer instance
            contact_type: Type of contact (email, phone, letter)
            notes: Optional notes about the contact
        """
        contact_record = {
            "date": datetime.utcnow().isoformat(),
            "type": contact_type,
            "notes": notes
        }
        
        if customer.communication_log is None:
            customer.communication_log = []
        
        customer.communication_log.append(contact_record)
        customer.last_collection_contact = datetime.utcnow()
        
        # Keep only last 50 contacts
        if len(customer.communication_log) > 50:
            customer.communication_log = customer.communication_log[-50:]
        
        self.db.commit()
    
    def get_collection_preferences(self, customer: Customer) -> Dict[str, Any]:
        """Get customer collection preferences with defaults."""
        defaults = {
            "email_frequency": "weekly",
            "phone_contact_allowed": True,
            "preferred_contact_time": "business_hours",
            "max_contacts_per_week": 3
        }
        
        if customer.collection_preferences:
            defaults.update(customer.collection_preferences)
        
        return defaults
    
    def should_contact_for_collections(self, customer: Customer) -> bool:
        """
        Determine if customer should be contacted for collections.
        
        Args:
            customer: Customer instance
            
        Returns:
            bool: True if contact is appropriate, False otherwise
        """
        if customer.do_not_contact:
            return False
        
        preferences = self.get_collection_preferences(customer)
        
        # Check communication frequency using centralized business rules
        if customer.last_collection_contact:
            days_since_contact = (datetime.utcnow() - customer.last_collection_contact).days
            
            # Use CommunicationRules for consistent frequency management
            return CommunicationRules.should_allow_communication(
                customer_tier=customer.tier or "standard",
                days_since_contact=days_since_contact,
                frequency_preference=preferences["email_frequency"]
            )
        
        # Check weekly contact limits
        if customer.communication_log:
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_contacts = [
                contact for contact in customer.communication_log
                if datetime.fromisoformat(contact["date"].replace('Z', '+00:00')) > week_ago
            ]
            
            if len(recent_contacts) >= preferences["max_contacts_per_week"]:
                return False
        
        return True
    
    def get_customers_for_collections(self, 
                                    min_balance: float = 0.0,
                                    min_days_overdue: int = 0,
                                    risk_categories: List[str] = None) -> List[Customer]:
        """
        Get customers that need collection attention.
        
        Args:
            min_balance: Minimum outstanding balance
            min_days_overdue: Minimum days since last payment
            risk_categories: List of risk categories to include
            
        Returns:
            List of customers needing collections
        """
        query = self.db.query(Customer).filter(
            Customer.business_id == self.business_id,
            Customer.is_active,
            Customer.do_not_contact.is_(False)
        )
        
        customers = []
        for customer in query.all():
            outstanding = self.get_outstanding_balance(customer)
            days_overdue = self.get_days_since_last_payment(customer) or 0
            
            # Apply filters
            if outstanding < min_balance:
                continue
            if days_overdue < min_days_overdue:
                continue
            if risk_categories and customer.risk_category not in risk_categories:
                continue
            
            # Check if we should contact
            if self.should_contact_for_collections(customer):
                customers.append(customer)
        
        # Sort by collection priority
        return sorted(customers, 
                     key=lambda c: self.calculate_collection_priority_score(c), 
                     reverse=True)
    
    def update_customer_preferences(self, customer: Customer, preferences: Dict[str, Any]):
        """
        Update customer collection preferences.
        
        Args:
            customer: Customer instance
            preferences: New preference settings
        """
        if customer.collection_preferences is None:
            customer.collection_preferences = {}
        
        customer.collection_preferences.update(preferences)
        self.db.commit()
    
    def _recalculate_payment_reliability(self, customer: Customer):
        """
        Recalculate payment reliability using industry-standard methodology.
        
        **Industry Standard**: Uses credit scoring methodology where payment rate
        directly correlates to creditworthiness. This is consistent with how
        major credit agencies and AR platforms calculate reliability scores.
        
        **Business Context**: Payment reliability is the strongest predictor of
        future payment behavior for B2B service relationships.
        """
        # Calculate payment rate based on actual payment history
        if customer.total_invoiced_ytd and customer.total_invoiced_ytd > 0:
            payment_rate = (customer.total_paid_ytd / customer.total_invoiced_ytd) * 100
        else:
            payment_rate = 0.0
        
        # Use centralized reliability scoring from CollectionsRules
        customer.payment_reliability_score = CollectionsRules.get_payment_reliability_score(payment_rate)
    
    def _update_risk_assessment(self, customer: Customer):
        """Update risk score and category based on current data."""
        risk_score = 0.0
        
        # Use centralized risk assessment methodology from RiskAssessmentRules
        balance = self.get_outstanding_balance(customer)
        days_since_payment = self.get_days_since_last_payment(customer) or 0
        
        # Calculate risk using industry-standard methodology
        risk_score = RiskAssessmentRules.calculate_customer_risk_score(
            payment_reliability=customer.payment_reliability_score,
            outstanding_balance=balance,
            days_since_payment=days_since_payment
        )
        
        customer.risk_score = risk_score
        
        # Update risk category
        if customer.risk_score >= 70:
            customer.risk_category = "high"
            customer.credit_status = "poor"
        elif customer.risk_score >= 50:
            customer.risk_category = "medium"
            customer.credit_status = "fair"
        elif customer.risk_score >= 30:
            customer.risk_category = "low"
            customer.credit_status = "good"
        else:
            customer.risk_category = "low"
            customer.credit_status = "excellent"
    
    def get_customer_summary(self, customer: Customer) -> Dict[str, Any]:
        """
        Get comprehensive customer summary for collections.
        
        Args:
            customer: Customer instance
            
        Returns:
            Dictionary with customer summary data
        """
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "outstanding_balance": self.get_outstanding_balance(customer),
            "days_since_last_payment": self.get_days_since_last_payment(customer),
            "payment_reliability_score": customer.payment_reliability_score,
            "risk_score": customer.risk_score,
            "risk_category": customer.risk_category,
            "collection_priority_score": self.calculate_collection_priority_score(customer),
            "should_contact": self.should_contact_for_collections(customer),
            "last_collection_contact": customer.last_collection_contact,
            "collection_preferences": self.get_collection_preferences(customer)
        }

    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID (QBO customer ID)."""
        try:
            return self.db.query(Customer).filter(
                Customer.business_id == self.business_id,
                Customer.qbo_customer_id == customer_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {e}")
            return None

    def get_customer_email(self, customer_id: str) -> Optional[str]:
        """Get customer email from database."""
        customer = self.get_customer_by_id(customer_id)
        return customer.email if customer else None

    def get_customer_phone(self, customer_id: str) -> Optional[str]:
        """Get customer phone from database."""
        customer = self.get_customer_by_id(customer_id)
        return customer.phone if customer else None
