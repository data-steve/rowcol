"""
Tray Priority Calculator Service

Canonical service for all tray item prioritization calculations.
This service consolidates tray priority logic from TrayService to eliminate duplication
and provide a single source of truth for tray item prioritization.

Key Responsibilities:
- Calculate priority scores for any tray item type
- Enhance tray items with priority and runway analysis
- Provide specialized priority calculations for different item types
- Integrate with payment and runway calculators for comprehensive analysis
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from domains.core.services.base_service import TenantAwareService
from config.business_rules import TrayPriorities

logger = logging.getLogger(__name__)


class TrayPriorityCalculator(TenantAwareService):
    """Canonical service for tray item prioritization calculations."""
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        super().__init__(db, business_id, validate_business)
        # Import here to avoid circular dependencies
        from runway.core.runway_calculator import RunwayCalculator
        from runway.core.payment_priority_calculator import PaymentPriorityCalculator
        
        self.runway_calculator = RunwayCalculator(db, business_id, validate_business=False)
        self.payment_priority_calculator = PaymentPriorityCalculator(db, business_id, validate_business=False)
        logger.info(f"Initialized TrayPriorityCalculator for business {business_id}")
    
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
            
            # Route to specialized calculators based on item type
            if item_type in ['overdue_bill', 'upcoming_bill', 'bill_approval']:
                return self.calculate_bill_tray_priority(item_data)
            elif item_type in ['overdue_invoice', 'upcoming_invoice', 'invoice_followup']:
                return self.calculate_invoice_tray_priority(item_data)
            else:
                return self._calculate_generic_tray_priority(item_data)
                
        except Exception as e:
            logger.error(f"Failed to calculate tray item priority: {e}")
            return {
                'priority_score': 50.0,
                'priority_level': 'medium',
                'urgency_factors': ['Error calculating priority'],
                'runway_impact': {'impact_days': 0, 'risk_level': 'unknown'},
                'error': str(e)
            }
    
    def calculate_bill_tray_priority(self, bill_item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized priority calculation for bill-related tray items."""
        try:
            # Extract bill data for payment priority calculation
            bill_data = {
                'amount': bill_item_data.get('amount', 0),
                'due_date': bill_item_data.get('due_date'),
                'vendor_name': bill_item_data.get('vendor_name', bill_item_data.get('description', 'Unknown')),
                'vendor_id': bill_item_data.get('vendor_id'),
                'bill_type': bill_item_data.get('bill_type', '')
            }
            
            # Use PaymentPriorityCalculator for bill-specific logic
            payment_analysis = self.payment_priority_calculator.get_payment_decision_analysis(bill_data)
            
            # Convert payment priority to tray priority format
            priority_score = payment_analysis.get('priority_score', 50.0)
            priority_level = payment_analysis.get('priority_level', 'medium')
            
            # Add tray-specific urgency factors
            urgency_factors = payment_analysis.get('decision_factors', [])
            if bill_item_data.get('type') == 'overdue_bill':
                urgency_factors.insert(0, 'Bill is overdue')
            
            return {
                'priority_score': priority_score,
                'priority_level': priority_level,
                'urgency_factors': urgency_factors,
                'runway_impact': payment_analysis.get('runway_impact', {}),
                'payment_category': payment_analysis.get('category', 'must_pay'),
                'payment_recommendation': payment_analysis.get('recommendation', '')
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate bill tray priority: {e}")
            return self._get_default_priority_result()
    
    def calculate_invoice_tray_priority(self, invoice_item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized priority calculation for invoice-related tray items."""
        try:
            score = 50.0  # Base score
            urgency_factors = []
            
            # Time-based urgency for invoices
            if invoice_item_data.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(invoice_item_data['due_date']) if isinstance(invoice_item_data['due_date'], str) else invoice_item_data['due_date']
                    days_overdue = (datetime.now() - due_date).days
                    if days_overdue > 0:
                        score += min(days_overdue * 2, 40)  # Up to +40 for overdue invoices
                        urgency_factors.append(f'Invoice overdue by {days_overdue} days')
                    elif days_overdue > -7:
                        score += 10  # Due soon
                        urgency_factors.append('Invoice due within a week')
                except Exception as e:
                    logger.error(f"Error calculating invoice due date urgency: {e}")
            
            # Amount factor for invoices (higher amounts = higher priority for collection)
            amount = invoice_item_data.get('amount', 0)
            if amount > 5000:
                score += 15
                urgency_factors.append('Large invoice amount (over $5,000)')
            elif amount > 1000:
                score += 8
                urgency_factors.append('Medium invoice amount (over $1,000)')
            
            # Invoice type specific factors
            if invoice_item_data.get('type') == 'overdue_invoice':
                score += 20
                urgency_factors.append('Invoice collection opportunity')
            
            # Calculate runway impact (positive for invoices - they bring in cash)
            runway_impact = self.runway_calculator.calculate_tray_item_runway_impact({
                'amount': amount,
                'type': 'invoice_collection'
            })
            
            priority_level = self._determine_priority_level(score)
            
            return {
                'priority_score': min(score, 100.0),
                'priority_level': priority_level,
                'urgency_factors': urgency_factors,
                'runway_impact': runway_impact
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate invoice tray priority: {e}")
            return self._get_default_priority_result()
    
    def enhance_tray_items_with_priority(self, tray_items: List[Dict[str, Any]], qbo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhance tray items with priority and runway analysis.
        
        This replaces TrayService.get_enhanced_tray_items() calculation logic.
        """
        try:
            enhanced_items = []
            
            for item in tray_items:
                enhanced_item = item.copy()
                
                # Calculate priority for this item
                priority_result = self.calculate_tray_item_priority(item)
                
                # Add priority data to item
                enhanced_item.update({
                    'priority_score': priority_result.get('priority_score', 50.0),
                    'priority_level': priority_result.get('priority_level', 'medium'),
                    'urgency_factors': priority_result.get('urgency_factors', []),
                    'runway_impact': priority_result.get('runway_impact', {}),
                })
                
                # Add payment-specific data for bill items
                if item.get('type') in ['overdue_bill', 'upcoming_bill', 'bill_approval']:
                    enhanced_item.update({
                        'payment_category': priority_result.get('payment_category', 'must_pay'),
                        'payment_recommendation': priority_result.get('payment_recommendation', ''),
                        'urgency_level': 'critical' if priority_result.get('priority_score', 0) >= 80 else 'high' if priority_result.get('priority_score', 0) >= 60 else 'medium'
                    })
                
                enhanced_items.append(enhanced_item)
            
            # Sort by payment category (must_pay first) then by priority score
            enhanced_items.sort(key=lambda x: (
                0 if x.get('payment_category') == 'must_pay' else 1,
                -x.get('priority_score', 0)  # Negative for descending order
            ))
            
            return enhanced_items
            
        except Exception as e:
            logger.error(f"Failed to enhance tray items with priority: {e}")
            return tray_items  # Return original items if enhancement fails
    
    def _calculate_generic_tray_priority(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate priority for generic tray items (non-bill, non-invoice)."""
        try:
            score = 50.0  # Base score
            urgency_factors = []
            
            # Time-based urgency
            if item_data.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(item_data['due_date']) if isinstance(item_data['due_date'], str) else item_data['due_date']
                    days_until_due = (due_date - datetime.now()).days
                    if days_until_due <= 0:
                        score += 40  # Overdue
                        urgency_factors.append('Item is overdue')
                    elif days_until_due <= 3:
                        score += 30  # Due within 3 days
                        urgency_factors.append('Due within 3 days')
                    elif days_until_due <= 7:
                        score += 20  # Due within week
                        urgency_factors.append('Due within a week')
                    elif days_until_due <= 14:
                        score += 10  # Due within 2 weeks
                        urgency_factors.append('Due within 2 weeks')
                except Exception as e:
                    logger.error(f"Error calculating generic due date urgency: {e}")
            
            # Type-based priority weights
            type_weights = {
                'bank_reconciliation': 25,
                'vendor_duplicate': 15,
                'data_quality_issue': 10,
                'system_alert': 20
            }
            
            item_type = item_data.get('type', '')
            if item_type in type_weights:
                score += type_weights[item_type]
                urgency_factors.append(f'{item_type.replace("_", " ").title()} requires attention')
            
            # Calculate basic runway impact
            runway_impact = {
                'impact_days': 0,
                'risk_level': 'low',
                'description': 'Minimal direct runway impact'
            }
            
            priority_level = self._determine_priority_level(score)
            
            return {
                'priority_score': min(score, 100.0),
                'priority_level': priority_level,
                'urgency_factors': urgency_factors,
                'runway_impact': runway_impact
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate generic tray priority: {e}")
            return self._get_default_priority_result()
    
    def _determine_priority_level(self, score: float) -> str:
        """Determine priority level based on score using business rules."""
        if score >= TrayPriorities.URGENT_SCORE:
            return 'urgent'
        elif score >= TrayPriorities.HIGH_SCORE:
            return 'high'
        elif score >= TrayPriorities.MEDIUM_SCORE:
            return 'medium'
        else:
            return 'low'
    
    def _get_default_priority_result(self) -> Dict[str, Any]:
        """Get default priority result for error cases."""
        return {
            'priority_score': 50.0,
            'priority_level': 'medium',
            'urgency_factors': ['Default priority due to calculation error'],
            'runway_impact': {'impact_days': 0, 'risk_level': 'unknown'}
        }
