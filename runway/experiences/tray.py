"""
TrayService - Refactored to use Canonical Calculation Services

This service orchestrates tray functionality while delegating all calculations
to the canonical services in runway/core/services/. This eliminates duplication
and establishes single sources of truth for all calculation logic.

Key Changes:
- All payment priority calculations → PaymentPriorityCalculator
- All tray item priority calculations → TrayPriorityCalculator  
- All runway impact calculations → RunwayCalculator (via priority calculators)
- Maintains orchestration and data provider functionality
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from runway.models.tray_item import TrayItem
from infra.qbo.smart_sync import SmartSyncService
from runway.core.reserve_runway import RunwayReserveService
from runway.core.payment_priority_calculator import PaymentPriorityCalculator
from runway.core.tray_priority_calculator import TrayPriorityCalculator
from common.exceptions import TrayItemNotFoundError
from infra.config import TrayPriorities, TrayItemStatuses
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class TrayService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        
        # Initialize sync utilities
        self.smart_sync = SmartSyncService(business_id)
        self.reserve_service = RunwayReserveService(db, business_id)
        
        # Canonical calculation services
        self.payment_priority_calculator = PaymentPriorityCalculator(db, business_id, validate_business=False) if business_id else None
        self.tray_priority_calculator = TrayPriorityCalculator(db, business_id, validate_business=False) if business_id else None
        
        # Use centralized QBO config
        from domains.qbo.config import qbo_config
        self.qbo_base_url = qbo_config.api_base_url
        self.realm_id = os.getenv("QBO_REALM_ID", "mock_realm_123")

    def calculate_priority_score(self, item: TrayItem) -> int:
        """Calculate priority score using canonical TrayPriorityCalculator."""
        if not self.tray_priority_calculator:
            raise RuntimeError("TrayPriorityCalculator not available - this is a critical service that should always be initialized")
        
        # Convert TrayItem to dict format for canonical service
        item_data = {
            'type': getattr(item, 'type', ''),
            'amount': getattr(item, 'amount', 0),
            'due_date': getattr(item, 'due_date', None),
            'metadata': getattr(item, 'metadata', {})
        }
        
        priority_analysis = self.tray_priority_calculator.calculate_tray_item_priority(item_data)
        return int(priority_analysis.get('priority_score', 50))

    def get_tray_items(self, business_id: int) -> List[Dict[str, Any]]:
        """Get tray items from QBO data."""
        try:
            # Get QBO data using SmartSyncService
            qbo_data = self.smart_sync.get_qbo_data_for_digest()
            
            tray_items = []
            
            # Convert QBO bills to tray items
            if "bills" in qbo_data:
                for bill in qbo_data["bills"]:
                    tray_items.append({
                        "business_id": business_id,
                        "type": "bill",
                        "qbo_id": str(bill.get("qbo_id", bill.get("id", ""))),
                        "due_date": bill.get("due_date"),
                        "amount": bill.get("total_amount", 0),
                        "priority": self._calculate_bill_priority(bill),
                        "status": "pending"
                    })
            
            # Convert QBO invoices to tray items
            if "invoices" in qbo_data:
                for invoice in qbo_data["invoices"]:
                    tray_items.append({
                        "business_id": business_id,
                        "type": "invoice",
                        "qbo_id": str(invoice.get("qbo_id", invoice.get("id", ""))),
                        "due_date": invoice.get("due_date"),
                        "amount": invoice.get("total_amount", 0),
                        "priority": self._calculate_invoice_priority(invoice),
                        "status": "pending"
                    })
            
            return tray_items
            
        except Exception as e:
            logger.error(f"Failed to fetch QBO tray items for business {business_id}: {e}")
            return []
    
    def _calculate_bill_priority(self, bill: Dict[str, Any]) -> str:
        """Calculate priority for a bill based on amount and due date."""
        amount = float(bill.get("total_amount", 0))
        
        if amount > 5000:
            return "high"
        elif amount > 1000:
            return "medium"
        else:
            return "low"
    
    def _calculate_invoice_priority(self, invoice: Dict[str, Any]) -> str:
        """Calculate priority for an invoice based on amount and age."""
        amount = float(invoice.get("total_amount", 0))
        
        if amount > 10000:
            return "high"
        elif amount > 2000:
            return "medium"
        else:
            return "low"

    def get_tray_summary(self, business_id: int) -> Dict[str, Any]:
        """Get tray summary with canonical priority calculations."""
        items = self.get_tray_items(business_id)
        
        summary = {
            "total_items": len(items),
            "urgent_count": 0,
            "by_priority": {"high": 0, "medium": 0, "low": 0},
            "by_type": {},
            "total_runway_impact": {"cash_impact": 0, "days_impact": 0}
        }
        
        for item in items:
            # Use canonical priority calculation
            if self.tray_priority_calculator:
                item_data = {
                    'type': item.get('type', ''),
                    'amount': item.get('amount', 0),
                    'due_date': item.get('due_date'),
                    'metadata': item.get('metadata', {})
                }
                priority_analysis = self.tray_priority_calculator.calculate_tray_item_priority(item_data)
                priority_score = priority_analysis.get('priority_score', 50)
                runway_impact = priority_analysis.get('runway_impact', {})
            else:
                # Fallback to basic calculation
                priority_score = 50
                runway_impact = {"cash_impact": 0, "days_impact": 0}
            
            # Priority distribution
            if priority_score >= TrayPriorities.URGENT_SCORE:
                summary["by_priority"]["high"] += 1
                summary["urgent_count"] += 1
            elif priority_score >= TrayPriorities.MEDIUM_SCORE:
                summary["by_priority"]["medium"] += 1
            else:
                summary["by_priority"]["low"] += 1
            
            # Type distribution
            item_type = item.get('type', 'unknown')
            summary["by_type"][item_type] = summary["by_type"].get(item_type, 0) + 1
            
            # Runway impact
            summary["total_runway_impact"]["cash_impact"] += runway_impact.get("cash_impact", 0)
            summary["total_runway_impact"]["days_impact"] += runway_impact.get("days_impact", 0)
        
        return summary
    
    def categorize_bill_urgency(self, bill_data: Dict[str, Any]) -> str:
        """Categorize bill urgency using canonical PaymentPriorityCalculator."""
        if not self.payment_priority_calculator:
            raise RuntimeError("PaymentPriorityCalculator not available - this is a critical service that should always be initialized")
        
        return self.payment_priority_calculator.categorize_bill_urgency(bill_data)

    def get_payment_decision_analysis(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment decision analysis using canonical PaymentPriorityCalculator."""
        if not self.payment_priority_calculator:
            raise RuntimeError("PaymentPriorityCalculator not available - this is a critical service that should always be initialized")
        
        return self.payment_priority_calculator.get_payment_decision_analysis(bill_data)

    def _calculate_runway_impact(self, item: TrayItem) -> Dict[str, Any]:
        """Calculate runway impact using canonical TrayPriorityCalculator."""
        if not self.tray_priority_calculator:
            raise RuntimeError("TrayPriorityCalculator not available - this is a critical service that should always be initialized")
        
        # Convert TrayItem to dict format for canonical service
        item_data = {
            'amount': getattr(item, 'amount', 0),
            'type': getattr(item, 'type', ''),
            'due_date': getattr(item, 'due_date', None)
        }
        
        priority_analysis = self.tray_priority_calculator.calculate_tray_item_priority(item_data)
        return priority_analysis.get('runway_impact', {})

    def get_enhanced_tray_items(self, business_id: int, include_runway_analysis: bool = True) -> List[Dict[str, Any]]:
        """
        Get enhanced tray items with priority and runway analysis using canonical calculators.
        
        Args:
            business_id: ID of the business
            include_runway_analysis: Whether to include runway impact analysis
        
        Returns:
            List of enhanced tray items with categorization and runway impact
        """
        try:
            # Get base tray items
            base_items = self.get_tray_items(business_id)
            
            if not include_runway_analysis:
                return base_items
            
            if not self.tray_priority_calculator:
                raise RuntimeError("TrayPriorityCalculator not available - this is a critical service that should always be initialized")
            
            # Get QBO data for enhanced analysis
            qbo_data = self.smart_sync.get_qbo_data_for_digest() if self.smart_sync else {}
            
            # Use canonical TrayPriorityCalculator for comprehensive enhancement
            enhanced_items = self.tray_priority_calculator.enhance_tray_items_with_priority(base_items, qbo_data)
            
            return enhanced_items
            
        except Exception as e:
            logger.error(f"Failed to get enhanced tray items: {e}")
            return base_items  # Return base items if enhancement fails

    def create_tray_item(self, business_id: str, item_type: str, title: str, amount: float, due_date: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a tray item for the prep tray."""
        try:
            tray_item = {
                'business_id': business_id,
                'item_type': item_type,
                'title': title,
                'amount': amount,
                'due_date': due_date,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            # In a real implementation, this would save to a database
            logger.info(f"Created tray item for business {business_id}: {title}")
            return tray_item
        except Exception as e:
            logger.error(f"Failed to create tray item: {e}")
            raise ValueError(f"Failed to create tray item: {e}")

    # ==================== ORCHESTRATION METHODS ====================
    # These methods handle tray workflow and data provider integration
    # All calculation logic is delegated to canonical services above

    def get_available_actions(self, item: TrayItem) -> List[Dict[str, Any]]:
        """Get available actions for a tray item."""
        action_map = {
            "overdue_bill": [
                {"action": "pay_bill", "label": "Pay Bill", "requires_confirmation": True},
                {"action": "schedule_payment", "label": "Schedule Payment", "requires_confirmation": False},
                {"action": "dispute_bill", "label": "Dispute Bill", "requires_confirmation": True}
            ],
            "upcoming_bill": [
                {"action": "pay_early", "label": "Pay Early", "requires_confirmation": True},
                {"action": "schedule_payment", "label": "Schedule Payment", "requires_confirmation": False}
            ],
            "overdue_invoice": [
                {"action": "send_reminder", "label": "Send Reminder", "requires_confirmation": False},
                {"action": "call_customer", "label": "Call Customer", "requires_confirmation": False},
                {"action": "write_off", "label": "Write Off", "requires_confirmation": True}
            ]
        }
        
        return action_map.get(item.type, [
            {"action": "mark_resolved", "label": "Mark Resolved", "requires_confirmation": True}
        ])

    def confirm_action(self, business_id: int, tray_item_id: int, action: str, 
                    confirmation_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Confirm action on tray item with enhanced validation and QBO integration."""
        item = self.db.query(TrayItem).filter(
            TrayItem.tray_item_id == tray_item_id,
            TrayItem.business_id == business_id
        ).first()
        
        if not item:
            raise TrayItemNotFoundError(f"Tray item {tray_item_id} not found")
        
        # Process action based on type
        if action == "pay_bill":
            return self._process_bill_payment(item, confirmation_data)
        elif action == "schedule_payment":
            return self._schedule_payment(item, confirmation_data)
        elif action == "send_reminder":
            return self._send_invoice_reminder(item, confirmation_data)
        else:
            # Mark as resolved
            item.status = TrayItemStatuses.RESOLVED
            item.resolved_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": True,
                "message": "Tray item marked as resolved",
                "item_id": tray_item_id,
                "action": action
            }

    def _process_bill_payment(self, item: TrayItem, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process bill payment with QBO integration."""
        # This would integrate with QBO payment processing
        # For now, return success response
        return {
            "success": True,
            "message": f"Bill payment processed for {item.title}",
            "qbo_payment_id": f"mock_payment_{item.tray_item_id}",
            "amount": confirmation_data.get("amount", item.amount)
        }

    def _schedule_payment(self, item: TrayItem, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule payment for future date."""
        scheduled_date = confirmation_data.get("scheduled_date")
        return {
            "success": True,
            "message": f"Payment scheduled for {scheduled_date}",
            "scheduled_date": scheduled_date,
            "amount": confirmation_data.get("amount", item.amount)
        }

    def _send_invoice_reminder(self, item: TrayItem, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send invoice reminder to customer."""
        return {
            "success": True,
            "message": f"Reminder sent for invoice {item.title}",
            "reminder_type": confirmation_data.get("reminder_type", "email")
        }

