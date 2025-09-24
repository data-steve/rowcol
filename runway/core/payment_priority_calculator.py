"""
Payment Priority Calculator Service

Canonical service for all payment prioritization and urgency calculations.
This service consolidates payment priority logic from TrayService, PaymentPriorityIntelligenceService,
and RunwayCalculator to eliminate duplication and provide a single source of truth.

Key Responsibilities:
- Calculate bill priority scores based on multiple factors
- Categorize bills as 'must_pay' vs 'can_delay'
- Generate comprehensive payment decision analysis
- Provide payment scenarios and recommendations
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from domains.core.services.base_service import TenantAwareService
from domains.ap.models.vendor import Vendor
from config.business_rules.payment_rules import PaymentRules
from config.business_rules.core_thresholds import RunwayThresholds

logger = logging.getLogger(__name__)


class PaymentPriorityCalculator(TenantAwareService):
    """Canonical service for all payment prioritization calculations."""
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        super().__init__(db, business_id, validate_business)
        # Import here to avoid circular dependency
        from runway.core.runway_calculator import RunwayCalculator
        self.runway_calculator = RunwayCalculator(db, business_id, validate_business=False)
        logger.info(f"Initialized PaymentPriorityCalculator for business {business_id}")
    
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
        
        Business Logic:
            - Overdue: +30 base + 1.5 * days_overdue
            - Due within 7 days: +20
            - Due within 14 days: +10
            - High amount (>$5000): +10
            - Medium amount (>$2500): +5
            - Critical vendor: +15
            - High reliability vendor: +5
        """
        try:
            score = 0.0
            
            # Due date urgency factor
            if bill_data.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(bill_data['due_date']) if isinstance(bill_data['due_date'], str) else bill_data['due_date']
                    days_until_due = (due_date - datetime.now()).days
                    if days_until_due < 0:
                        score += 30.0  # Overdue bills get highest boost
                        score += abs(days_until_due) * 1.5  # More overdue = higher priority
                    elif days_until_due < 7:
                        score += 20.0  # Due within a week
                    elif days_until_due < 14:
                        score += 10.0  # Due within two weeks
                except Exception as e:
                    logger.error(f"Error calculating due date urgency for bill: {e}")
            
            # Amount factor - high amounts get higher priority
            amount = bill_data.get('amount', 0.0)
            if amount > PaymentRules.HIGH_AMOUNT_THRESHOLD:
                score += 10.0
            elif amount > PaymentRules.HIGH_AMOUNT_THRESHOLD / 2:
                score += 5.0
            
            # Vendor relationship factor
            if bill_data.get('vendor_id'):
                vendor = self.db.query(Vendor).filter(
                    Vendor.vendor_id == bill_data['vendor_id'],
                    Vendor.business_id == self.business_id
                ).first()
                if vendor and getattr(vendor, 'is_critical', False):
                    score += 15.0
                if vendor and getattr(vendor, 'payment_reliability_score', 0) is not None:
                    reliability_score = getattr(vendor, 'payment_reliability_score', 0)
                    if reliability_score >= PaymentRules.HIGH_RELIABILITY_THRESHOLD:
                        score += 5.0
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate bill priority score: {e}")
            return 50.0  # Default medium priority
    
    def categorize_bill_urgency(self, bill_data: Dict[str, Any]) -> str:
        """
        Categorize bill as 'must_pay' or 'can_delay' based on business rules.
        
        Args:
            bill_data: Same as calculate_bill_priority_score
        
        Returns:
            str: "must_pay" or "can_delay"
        
        Business Logic:
            Must Pay Criteria (any one triggers):
            - Already overdue
            - Critical vendors (utilities, rent, payroll, taxes)
            - Critical bill types (payroll, tax, insurance, rent, utilities)
            - Large runway impact (>15% of current runway)
            - Due within 3 days
            - Would put runway below 30 days
            
            Can Delay Criteria:
            - Due >14 days with runway >60 days
            - Small amount (<5 days burn) with runway >45 days
            - Non-critical vendor with runway >90 days and due >7 days
        """
        try:
            amount = float(bill_data.get('amount', 0))
            due_date_str = bill_data.get('due_date')
            vendor_name = bill_data.get('vendor_name', '').lower()
            bill_type = bill_data.get('bill_type', '').lower()
            
            # Get current runway calculation
            runway_data = self.runway_calculator.calculate_current_runway({})
            current_runway = runway_data.get('base_runway_days', 0)
            burn_rate_data = runway_data.get('burn_rate', {})
            daily_burn = burn_rate_data.get('daily_burn', 1) if isinstance(burn_rate_data, dict) else 1
            
            # Calculate days until due
            days_until_due = 0
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str) if isinstance(due_date_str, str) else due_date_str
                    days_until_due = (due_date - datetime.now()).days
                except (ValueError, TypeError):
                    days_until_due = 0
            
            # MUST PAY criteria (any one triggers must pay)
            if days_until_due < 0:
                return 'must_pay'
            
            critical_vendors = ['electric', 'gas', 'water', 'rent', 'lease', 'payroll', 'irs', 'tax', 'insurance']
            if any(keyword in vendor_name for keyword in critical_vendors):
                return 'must_pay'
            
            critical_types = ['payroll', 'tax', 'insurance', 'rent', 'utilities']
            if any(keyword in bill_type for keyword in critical_types):
                return 'must_pay'
            
            runway_impact_days = amount / daily_burn if daily_burn > 0 else 0
            if runway_impact_days > (current_runway * 0.15):
                return 'must_pay'
            
            if days_until_due <= 3:
                return 'must_pay'
            
            runway_after_payment = current_runway - runway_impact_days
            if runway_after_payment < RunwayThresholds.CRITICAL_DAYS:
                return 'must_pay'
            
            # CAN DELAY criteria
            if days_until_due > 14 and current_runway > 60:
                return 'can_delay'
            
            if amount < (daily_burn * 5) and current_runway > 45:
                return 'can_delay'
            
            if current_runway > 90 and days_until_due > 7:
                return 'can_delay'
            
            # Default to must_pay for safety
            return 'must_pay'
            
        except Exception as e:
            logger.error(f"Failed to categorize bill urgency: {e}")
            return 'must_pay'  # Conservative default
    
    def prioritize_bills_for_payment(self, bills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize list of bills for payment.
        
        Args:
            bills: List of bill data dicts
        
        Returns:
            List of bills with added fields:
            - priority_score: float
            - priority_level: str ("urgent", "high", "medium", "low")
            - urgency_category: str ("must_pay", "can_delay")
        """
        try:
            prioritized_bills = []
            for bill in bills:
                priority_score = self.calculate_bill_priority_score(bill)
                urgency_category = self.categorize_bill_urgency(bill)
                priority_level = self._determine_priority_level(priority_score)
                
                enhanced_bill = bill.copy()
                enhanced_bill.update({
                    'priority_score': priority_score,
                    'priority_level': priority_level,
                    'urgency_category': urgency_category
                })
                prioritized_bills.append(enhanced_bill)
            
            # Sort by priority score descending (higher score = higher priority)
            return sorted(prioritized_bills, key=lambda x: x['priority_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to prioritize bills: {e}")
            return bills  # Return original list if prioritization fails
    
    def get_payment_decision_analysis(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive payment decision analysis.
        
        Args:
            bill_data: Bill data dict
        
        Returns:
            {
                "category": str,  # "must_pay" or "can_delay"
                "priority_score": float,
                "priority_level": str,
                "runway_impact": Dict[str, Any],  # From RunwayCalculator
                "scenarios": {
                    "pay_now": Dict[str, Any],
                    "pay_on_due_date": Dict[str, Any],
                    "delay_30_days": Dict[str, Any]
                },
                "recommendation": str,
                "decision_factors": List[str]
            }
        """
        try:
            # Get basic categorization and priority
            category = self.categorize_bill_urgency(bill_data)
            priority_score = self.calculate_bill_priority_score(bill_data)
            priority_level = self._determine_priority_level(priority_score)
            
            # Get runway impact from RunwayCalculator
            runway_impact = self.runway_calculator.calculate_bill_runway_impact(bill_data)
            
            # Get current runway data for scenarios
            runway_data = self.runway_calculator.calculate_current_runway({})
            current_runway = runway_data.get('base_runway_days', 0)
            runway_data.get('burn_rate', {}).get('daily_burn', 1)
            available_cash = runway_data.get('cash_position', 0)
            
            amount = float(bill_data.get('amount', 0))
            due_date_str = bill_data.get('due_date')
            vendor_name = bill_data.get('vendor_name', 'Unknown')
            
            # Calculate timing
            days_until_due = 0
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str) if isinstance(due_date_str, str) else due_date_str
                    days_until_due = (due_date - datetime.now()).days
                except (ValueError, TypeError):
                    days_until_due = 0
            
            # Generate payment scenarios
            runway_after_payment = current_runway - runway_impact.get('impact_days', 0)
            cash_after_payment = available_cash - amount
            
            scenarios = {
                'pay_now': {
                    'runway_days': runway_after_payment,
                    'cash_remaining': cash_after_payment,
                    'risk_level': 'low' if runway_after_payment > 60 else 'medium' if runway_after_payment > 30 else 'high'
                },
                'pay_on_due_date': {
                    'runway_days': runway_after_payment,
                    'cash_remaining': cash_after_payment,
                    'additional_risk': 'penalty' if days_until_due < 0 else 'none'
                },
                'delay_30_days': {
                    'runway_days': runway_after_payment,
                    'cash_remaining': cash_after_payment,
                    'risk_level': 'high' if days_until_due <= 0 else 'medium',
                    'potential_penalties': 'late_fees' if days_until_due <= 30 else 'relationship_damage'
                }
            }
            
            # Generate recommendation
            recommendation = self._generate_payment_recommendation(
                category, days_until_due, vendor_name, current_runway, runway_impact.get('impact_days', 0)
            )
            
            # Get decision factors
            decision_factors = self.get_decision_factors(bill_data, category, runway_data)
            
            return {
                'category': category,
                'priority_score': priority_score,
                'priority_level': priority_level,
                'runway_impact': runway_impact,
                'scenarios': scenarios,
                'recommendation': recommendation,
                'decision_factors': decision_factors
            }
            
        except Exception as e:
            logger.error(f"Failed to generate payment decision analysis: {e}")
            return {
                'category': 'must_pay',
                'priority_score': 50.0,
                'priority_level': 'medium',
                'runway_impact': {'impact_days': 0, 'risk_level': 'unknown'},
                'scenarios': {},
                'recommendation': 'Pay immediately (analysis failed)',
                'decision_factors': ['Analysis error - defaulting to conservative approach'],
                'error': str(e)
            }
    
    def get_decision_factors(self, bill_data: Dict[str, Any], category: str, runway_metrics: Dict[str, Any]) -> List[str]:
        """Generate human-readable decision factors."""
        factors = []
        
        try:
            amount = float(bill_data.get('amount', 0))
            vendor_name = bill_data.get('vendor_name', '').lower()
            due_date_str = bill_data.get('due_date')
            current_runway = runway_metrics.get('base_runway_days', 0)
            
            # Calculate days until due
            days_until_due = 0
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str) if isinstance(due_date_str, str) else due_date_str
                    days_until_due = (due_date - datetime.now()).days
                except (ValueError, TypeError):
                    days_until_due = 0
            
            # Due date factors
            if days_until_due < 0:
                factors.append('Bill is overdue')
            elif days_until_due <= 3:
                factors.append('Due within 3 days')
            
            # Vendor factors
            critical_vendors = ['electric', 'gas', 'water', 'rent', 'lease', 'payroll', 'irs', 'tax', 'insurance']
            if any(keyword in vendor_name for keyword in critical_vendors):
                factors.append('Critical vendor (utilities, rent, taxes, etc.)')
            
            # Runway factors
            if current_runway < RunwayThresholds.CRITICAL_DAYS:
                factors.append(f'Critical runway (less than {RunwayThresholds.CRITICAL_DAYS} days)')
            elif current_runway < RunwayThresholds.WARNING_DAYS:
                factors.append(f'Low runway (less than {RunwayThresholds.WARNING_DAYS} days)')
            elif current_runway > 90:
                factors.append('Strong runway (more than 90 days)')
            
            # Amount factors
            if amount > PaymentRules.HIGH_AMOUNT_THRESHOLD:
                factors.append(f'Large amount (over ${PaymentRules.HIGH_AMOUNT_THRESHOLD:,.0f})')
            elif amount < 500:
                factors.append('Small amount (under $500)')
            
            # Default factor if no specific factors identified
            if category == 'must_pay' and not factors:
                factors.append('Conservative approach - default to must pay')
            
            return factors
            
        except Exception as e:
            logger.error(f"Failed to generate decision factors: {e}")
            return ['Error generating decision factors']
    
    def _determine_priority_level(self, score: float) -> str:
        """Determine priority level based on score."""
        if score >= 60.0:
            return 'urgent'
        elif score >= 40.0:
            return 'high'
        elif score >= 20.0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_payment_recommendation(self, category: str, days_until_due: int, vendor_name: str, 
                                       current_runway: float, runway_impact_days: float) -> str:
        """Generate payment recommendation text."""
        if category == 'must_pay':
            if days_until_due <= 0:
                return f'PAY IMMEDIATELY - {vendor_name} bill is overdue'
            elif days_until_due <= 3:
                return f'PAY TODAY - {vendor_name} bill due in {days_until_due} days'
            else:
                return f'PAY BY DUE DATE - Critical payment for {vendor_name}'
        else:
            if current_runway > 90:
                return f'CAN DELAY - Strong runway position allows flexibility with {vendor_name}'
            elif current_runway > 60:
                return f'MONITOR - Can delay but watch runway impact ({runway_impact_days:.1f} days)'
            else:
                return 'CAUTION - Delay only if necessary, limited runway buffer'
