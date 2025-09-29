"""
Bill Impact Calculator

Stateless service for calculating bill-specific runway impact calculations.
This service receives runway context as parameters to avoid circular dependencies.

Handles:
- Bill payment impact on runway
- Payment timing analysis
- Risk assessment for bill payments
"""

from typing import Dict, Any
from infra.config import RunwayThresholds
import logging

logger = logging.getLogger(__name__)


class BillImpactCalculator:
    """Stateless service for bill-specific runway impact calculations."""
    
    def calculate_bill_runway_impact(self, bill_data: Dict[str, Any], runway_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate runway impact of paying a specific bill.
        
        Args:
            bill_data: {"amount": float, "due_date": str, "vendor_name": str}
            runway_context: Current runway data from RunwayCalculationService
        
        Returns:
            {
                "impact_days": float,
                "runway_after_payment": float,
                "impact_percentage": float,
                "risk_level": str  # "low", "medium", "high"
            }
        """
        try:
            amount = float(bill_data.get('amount', 0))
            
            # Extract runway data from provided context
            current_runway = runway_context.get('base_runway_days', 0)
            daily_burn = runway_context.get('burn_rate', {}).get('daily_burn', 1)
            
            # Calculate impact
            impact_days = amount / daily_burn if daily_burn > 0 else 0
            runway_after_payment = current_runway - impact_days
            impact_percentage = (impact_days / current_runway * 100) if current_runway > 0 else 0
            
            # Determine risk level
            if runway_after_payment < RunwayThresholds.CRITICAL_DAYS:
                risk_level = 'high'
            elif runway_after_payment < RunwayThresholds.WARNING_DAYS:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'impact_days': impact_days,
                'runway_after_payment': runway_after_payment,
                'impact_percentage': impact_percentage,
                'risk_level': risk_level
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate bill runway impact: {e}")
            return {
                'impact_days': 0,
                'runway_after_payment': 0,
                'impact_percentage': 0,
                'risk_level': 'unknown'
            }

    def calculate_payment_impact(self, payment_data: Dict[str, Any], runway_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate runway impact of a payment decision.
        
        Args:
            payment_data: {"amount": float, "payment_date": str, "bill_id": str}
            runway_context: Current runway data from RunwayCalculationService
        
        Returns:
            {
                "impact_days": float,
                "runway_after_payment": float,
                "payment_timing": str  # "early", "on_time", "late"
            }
        """
        try:
            amount = float(payment_data.get('amount', 0))
            
            # Extract runway data from provided context
            current_runway = runway_context.get('base_runway_days', 0)
            daily_burn = runway_context.get('burn_rate', {}).get('daily_burn', 1)
            
            # Calculate impact
            impact_days = amount / daily_burn if daily_burn > 0 else 0
            runway_after_payment = current_runway - impact_days
            
            # Determine payment timing (simplified logic)
            payment_timing = "on_time"  # Could be enhanced with due date analysis
            
            return {
                'impact_days': impact_days,
                'runway_after_payment': runway_after_payment,
                'payment_timing': payment_timing
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate payment impact: {e}")
            return {
                'impact_days': 0,
                'runway_after_payment': 0,
                'payment_timing': 'unknown'
            }
