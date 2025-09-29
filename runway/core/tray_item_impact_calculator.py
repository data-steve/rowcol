"""
Tray Item Impact Calculator

Stateless service for calculating tray item-specific runway impact calculations.
This service receives runway context as parameters to avoid circular dependencies.

Handles bills and invoices with **blocking data quality issues** that prevent them from being ready for decision-making:

AP Hygiene Issues (Bills):
- Missing due dates on bills → Can't schedule payment timing
- Missing vendor information → Can't process payment
- Missing line item details → Can't verify bill accuracy
- Malformed data from QBO sync → Can't process bill

AR Hygiene Issues (Invoices):
- Incomplete customer data → Can't send invoice
- Missing line item details → Can't send invoice
- Unmatched AR payments → Can't identify truly overdue invoices (prevents false overdue calls)
- Malformed data from QBO sync → Can't process invoice

Purpose: Calculate runway impact of fixing these blocking issues before decision-making
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TrayItemImpactCalculator:
    """Stateless service for tray item-specific runway impact calculations."""
    
    def calculate_tray_item_runway_impact(self, item_data: Dict[str, Any], runway_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate runway impact of resolving a tray item (data quality issue).
        
        Args:
            item_data: {"amount": float, "type": str, "issue_type": str}
            runway_context: Current runway data from RunwayCalculationService
        
        Returns:
            {
                "cash_impact": float,
                "days_impact": float,
                "impact_type": str,  # "positive", "negative"
                "issue_resolution_value": float,
                "runway_improvement_days": float
            }
        """
        try:
            amount = float(item_data.get('amount', 0))
            item_type = item_data.get('type', '')
            issue_type = item_data.get('issue_type', '')
            
            # Extract runway data from provided context
            daily_burn = runway_context.get('burn_rate', {}).get('daily_burn', 1)
            
            # Calculate impact based on item type
            if 'invoice' in item_type or 'collection' in item_type:
                # Invoices add to runway (positive impact)
                days_impact = amount / daily_burn if daily_burn > 0 else 0
                impact_type = 'positive'
            else:
                # Bills and other items reduce runway (negative impact)
                days_impact = -(amount / daily_burn) if daily_burn > 0 else 0
                impact_type = 'negative'
            
            # Calculate issue resolution value (how much runway improvement from fixing the issue)
            issue_resolution_value = self._calculate_issue_resolution_value(issue_type, amount, daily_burn)
            runway_improvement_days = issue_resolution_value / daily_burn if daily_burn > 0 else 0
            
            return {
                'cash_impact': float(amount),
                'days_impact': float(days_impact),
                'impact_type': impact_type,
                'issue_resolution_value': issue_resolution_value,
                'runway_improvement_days': runway_improvement_days
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate tray item runway impact: {e}")
            return {
                'cash_impact': 0,
                'days_impact': 0,
                'impact_type': 'unknown',
                'issue_resolution_value': 0,
                'runway_improvement_days': 0
            }

    def _calculate_issue_resolution_value(self, issue_type: str, amount: float, daily_burn: float) -> float:
        """
        Calculate the value of resolving a specific data quality issue.
        
        Args:
            issue_type: Type of data quality issue
            amount: Amount associated with the item
            daily_burn: Daily burn rate for runway calculations
        
        Returns:
            Estimated value of resolving the issue
        """
        # Base value is the amount itself
        base_value = amount
        
        # Apply multipliers based on issue type
        if issue_type == 'missing_due_dates':
            # Missing due dates prevent optimal payment timing
            return base_value * 0.1  # 10% improvement from better timing
        elif issue_type == 'missing_vendor_info':
            # Missing vendor info prevents payment processing
            return base_value * 0.05  # 5% improvement from processing
        elif issue_type == 'unmatched_payments':
            # Unmatched payments prevent accurate AR tracking
            return base_value * 0.15  # 15% improvement from accurate tracking
        elif issue_type == 'incomplete_customer_data':
            # Incomplete customer data prevents invoice sending
            return base_value * 0.2  # 20% improvement from sending invoices
        else:
            # Default improvement for other issues
            return base_value * 0.1
