"""
Priority Calculation Service - Centralized priority logic for runway product

This service consolidates ALL priority calculation logic from domain services
into a single source of truth. Moved from scattered implementations across
domain services to maintain ADR-001 compliance.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from domains.core.services.base_service import TenantAwareService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PriorityCalculator(TenantAwareService):
    """
    Centralized service for all priority calculations across the runway product.
    
    Consolidates priority logic from:
    - Bill priority calculations (AP domain)
    - Invoice priority calculations (AR domain) 
    - Tray item priority calculations (runway experiences)
    - Collection priority calculations (AR domain)
    """
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        super().__init__(db, business_id, validate_business)
        logger.info(f"Initialized PriorityCalculationService for business {business_id}")
    
    def calculate_bill_priority_score(self, bill_data: Dict[str, Any]) -> float:
        """
        Calculate priority score (0-100) for a bill based on multiple factors.
        Higher score means higher payment priority.
        
        Args:
            bill_data: {
                "amount": float,
                "due_date": str,
                "vendor_name": str,
                "vendor_id": Optional[str],
                "bill_type": Optional[str]
            }
        
        Returns:
            float: Priority score (0-100, higher = more urgent)
        """
        try:
            score = 0.0
            
            # Due date urgency factor
            if bill_data.get('due_date'):
                due_date = datetime.fromisoformat(bill_data['due_date'].replace('Z', '+00:00'))
                days_until_due = (due_date - datetime.now()).days
                
                if days_until_due < 0:
                    # Overdue: +30 base + 1.5 * days_overdue
                    score += 30 + (abs(days_until_due) * 1.5)
                elif days_until_due <= 7:
                    # Due within 7 days: +20
                    score += 20
                elif days_until_due <= 14:
                    # Due within 14 days: +10
                    score += 10
            
            # Amount factor
            amount = bill_data.get('amount', 0)
            if amount > 5000:
                score += 10  # High amount boost
            elif amount > 2500:
                score += 5   # Medium amount boost
            
            # Vendor factor (if available)
            vendor_name = bill_data.get('vendor_name', '').lower()
            if 'critical' in vendor_name or 'essential' in vendor_name:
                score += 15  # Critical vendor boost
            elif 'reliable' in vendor_name or 'preferred' in vendor_name:
                score += 5   # Reliable vendor boost
            
            return min(score, 100.0)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Failed to calculate bill priority score: {e}")
            return 50.0  # Default medium priority
    
    def calculate_invoice_priority_score(self, invoice_data: Dict[str, Any]) -> float:
        """
        Calculate priority score (0-100) for an invoice based on collection urgency.
        Higher score means higher collection priority.
        
        Args:
            invoice_data: {
                "amount": float,
                "due_date": str,
                "customer_name": str,
                "customer_id": Optional[str],
                "days_overdue": Optional[int]
            }
        
        Returns:
            float: Priority score (0-100, higher = more urgent)
        """
        try:
            score = 0.0
            
            # Overdue factor
            days_overdue = invoice_data.get('days_overdue', 0)
            if days_overdue > 0:
                if days_overdue >= 90:
                    score += 40  # Very overdue
                elif days_overdue >= 60:
                    score += 30  # Overdue
                elif days_overdue >= 30:
                    score += 20  # Recently overdue
                else:
                    score += 10  # Just overdue
            
            # Amount factor
            amount = invoice_data.get('amount', 0)
            if amount > 10000:
                score += 25  # High amount
            elif amount > 5000:
                score += 15  # Medium-high amount
            elif amount > 1000:
                score += 10  # Medium amount
            else:
                score += 5   # Low amount
            
            # Customer factor (if available)
            customer_name = invoice_data.get('customer_name', '').lower()
            if 'problem' in customer_name or 'difficult' in customer_name:
                score += 15  # Problem customer boost
            elif 'reliable' in customer_name or 'good' in customer_name:
                score += 5   # Reliable customer boost
            
            return min(score, 100.0)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Failed to calculate invoice priority score: {e}")
            return 50.0  # Default medium priority
    
    def calculate_tray_item_priority(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate priority for any tray item type.
        
        Args:
            item_data: {
                "type": str,  # "overdue_bill", "overdue_invoice", etc.
                "amount": Optional[float],
                "due_date": Optional[str],
                "qbo_id": Optional[str],
                "metadata": Dict[str, Any]
            }
        
        Returns:
            {
                "priority_score": float,  # 0-100
                "priority_level": str,    # "urgent", "high", "medium", "low"
                "urgency_factors": List[str],
                "runway_impact": Dict[str, Any]
            }
        """
        try:
            item_type = item_data.get('type', '')
            amount = item_data.get('amount', 0)
            
            # Route to specialized calculators based on item type
            if item_type in ['overdue_bill', 'upcoming_bill', 'bill_approval']:
                score = self.calculate_bill_priority_score(item_data)
            elif item_type in ['overdue_invoice', 'upcoming_invoice', 'invoice_followup']:
                score = self.calculate_invoice_priority_score(item_data)
            else:
                # Generic calculation
                score = 50.0
            
            # Determine priority level
            if score >= 80:
                priority_level = "urgent"
                urgency_factors = ["High priority item requiring immediate attention"]
            elif score >= 60:
                priority_level = "high"
                urgency_factors = ["Important item requiring prompt action"]
            elif score >= 40:
                priority_level = "medium"
                urgency_factors = ["Standard priority item"]
            else:
                priority_level = "low"
                urgency_factors = ["Low priority item"]
            
            # Calculate runway impact (simplified)
            runway_impact = {
                "impact_days": amount / 1000 if amount > 0 else 0,  # Rough estimate
                "risk_level": "high" if score >= 80 else "medium" if score >= 60 else "low"
            }
            
            return {
                "priority_score": score,
                "priority_level": priority_level,
                "urgency_factors": urgency_factors,
                "runway_impact": runway_impact
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate tray item priority: {e}")
            return {
                "priority_score": 50.0,
                "priority_level": "medium",
                "urgency_factors": ["Error calculating priority"],
                "runway_impact": {"impact_days": 0, "risk_level": "unknown"}
            }
    
    def calculate_collection_priority_score(self, customer_data: Dict[str, Any]) -> float:
        """
        Calculate collection priority score based on customer payment history.
        Higher score = higher priority for collections.
        
        Args:
            customer_data: {
                "outstanding_balance": float,
                "days_since_last_payment": int,
                "payment_reliability_score": float,
                "risk_score": float
            }
        
        Returns:
            float: Priority score (0-100)
        """
        try:
            score = 0.0
            
            # Outstanding balance factor
            balance = customer_data.get('outstanding_balance', 0)
            if balance > 10000:
                score += 30
            elif balance > 5000:
                score += 20
            elif balance > 1000:
                score += 10
            else:
                score += 5
            
            # Payment reliability factor (0-25 points, inverse)
            reliability = customer_data.get('payment_reliability_score', 50)
            reliability_penalty = (100 - reliability) / 4
            score += reliability_penalty
            
            # Days since last payment factor
            days_since_payment = customer_data.get('days_since_last_payment', 0)
            if days_since_payment > 90:
                score += 25
            elif days_since_payment > 60:
                score += 20
            elif days_since_payment > 30:
                score += 15
            elif days_since_payment > 14:
                score += 10
            else:
                score += 5
            
            # Risk score factor (0-20 points)
            risk_score = customer_data.get('risk_score', 50)
            score += risk_score / 5
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate collection priority score: {e}")
            return 50.0
