from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from domains.bank.models.bank_transaction import BankTransaction
from domains.ar.models.invoice import Invoice
from domains.ap.models.bill import Bill
from runway.tray.models.tray_item import TrayItem
from runway.tray.providers import TrayDataProvider, get_tray_data_provider
from common.exceptions import TrayError, TrayItemNotFoundError
from config.business_rules import TrayPriorities, TrayItemStatuses
from datetime import datetime, timedelta
import os

class TrayService:
    def __init__(self, db: Session, data_provider: Optional[TrayDataProvider] = None):
        self.db = db
        self.data_provider = data_provider or get_tray_data_provider()
        self.qbo_base_url = "https://sandbox-quickbooks.api.intuit.com"
        self.realm_id = os.getenv("QBO_REALM_ID", "mock_realm_123")

    def calculate_priority_score(self, item: TrayItem) -> int:
        """Calculate priority score based on urgency, amount, and business impact."""
        score = 50  # Base score
        
        # Time-based urgency (higher score = more urgent)
        if item.due_date:
            days_until_due = (item.due_date - datetime.now()).days
            if days_until_due <= 0:
                score += 40  # Overdue
            elif days_until_due <= 3:
                score += 30  # Due within 3 days
            elif days_until_due <= 7:
                score += 20  # Due within week
            elif days_until_due <= 14:
                score += 10  # Due within 2 weeks
        
        # Type-based priority from data provider
        type_weights = self.data_provider.get_priority_weights()
        score += type_weights.get(item.type, 0)
        
        # Cap at 100
        return min(score, 100)

    def generate_qbo_deep_link(self, item: TrayItem) -> str:
        """Generate mock QBO deep link for tray item."""
        if not item.qbo_id:
            return f"{self.qbo_base_url}/app/homepage"
        
        # Mock QBO deep links based on item type
        link_patterns = {
            "overdue_bill": f"{self.qbo_base_url}/app/bill?txnId={item.qbo_id}",
            "overdue_invoice": f"{self.qbo_base_url}/app/invoice?txnId={item.qbo_id}",
            "bank_reconciliation": f"{self.qbo_base_url}/app/reconcile?accountId={item.qbo_id}",
            "vendor_duplicate": f"{self.qbo_base_url}/app/vendor?vendorId={item.qbo_id}",
        }
        
        return link_patterns.get(item.type, f"{self.qbo_base_url}/app/homepage")

    def get_tray_items(self, business_id: int) -> List[Dict[str, Any]]:
        """Get prioritized tray items with enhanced metadata."""
        items = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.status == TrayItemStatuses.PENDING
        ).all()
        
        # Calculate priority scores and sort
        enhanced_items = []
        for item in items:
            priority_score = self.calculate_priority_score(item)
            qbo_link = self.generate_qbo_deep_link(item)
            
            enhanced_items.append({
                "id": item.id,
                "type": item.type,
                "qbo_id": item.qbo_id,
                "status": item.status,
                "priority": item.priority,
                "priority_score": priority_score,
                "due_date": item.due_date.isoformat() if item.due_date else None,
                "qbo_deep_link": qbo_link,
                "allowed_roles": item.allowed_roles.split(",") if item.allowed_roles else ["owner"],
                "actions": self._get_available_actions(item),
                "runway_impact": self._calculate_runway_impact(item)
            })
        
        # Sort by priority score (highest first)
        enhanced_items.sort(key=lambda x: x["priority_score"], reverse=True)
        return enhanced_items

    def _get_available_actions(self, item: TrayItem) -> List[Dict[str, Any]]:
        """Get available actions based on tray item type."""
        action_map = {
            "overdue_bill": [
                {"action": "approve_payment", "label": "Approve Payment", "requires_confirmation": True},
                {"action": "schedule_payment", "label": "Schedule Payment", "requires_date": True},
                {"action": "dispute", "label": "Dispute Bill", "requires_reason": True}
            ],
            "overdue_invoice": [
                {"action": "send_reminder", "label": "Send Reminder", "requires_confirmation": True},
                {"action": "schedule_call", "label": "Schedule Collection Call", "requires_date": True},
                {"action": "write_off", "label": "Write Off", "requires_confirmation": True}
            ],
            "bank_reconciliation": [
                {"action": "auto_match", "label": "Auto-Match Transactions", "requires_confirmation": True},
                {"action": "manual_review", "label": "Manual Review", "requires_confirmation": False}
            ],
            "vendor_duplicate": [
                {"action": "merge_vendors", "label": "Merge Vendors", "requires_confirmation": True},
                {"action": "keep_separate", "label": "Keep Separate", "requires_reason": True}
            ]
        }
        
        return action_map.get(item.type, [
            {"action": "mark_resolved", "label": "Mark Resolved", "requires_confirmation": True}
        ])

    def _calculate_runway_impact(self, item: TrayItem) -> Dict[str, Any]:
        """Calculate the runway impact of resolving this tray item."""
        return self.data_provider.get_runway_impact(item.type)

    def confirm_action(self, business_id: int, tray_item_id: int, action: str, 
                    confirmation_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Confirm action on tray item with enhanced validation and QBO integration."""
        item = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.id == tray_item_id
        ).first()
        
        if not item:
            raise TrayItemNotFoundError(f"Tray item {tray_item_id} not found for business {business_id}")
        
        # Validate action is available for this item type
        available_actions = [a["action"] for a in self._get_available_actions(item)]
        if action not in available_actions:
            raise ValueError(f"Action '{action}' not available for item type '{item.type}'")
        
        # Process the action
        result = self._process_action(item, action, confirmation_data or {})
        
        # Update item status using constants
        if action in ["approve_payment", "send_reminder", "auto_match", "merge_vendors", "mark_resolved"]:
            item.status = TrayItemStatuses.RESOLVED
        elif action in ["schedule_payment", "schedule_call"]:
            item.status = TrayItemStatuses.SCHEDULED
        elif action in ["dispute", "write_off", "manual_review", "keep_separate"]:
            item.status = TrayItemStatuses.REQUIRES_ATTENTION
        
        self.db.commit()
        
        return {
            "item_id": item.id,
            "action": action,
            "status": item.status,
            "result": result,
            "qbo_sync_status": "mock_success",  # Mock QBO sync
            "timestamp": datetime.now().isoformat()
        }

    def _process_action(self, item: TrayItem, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the specific action via data provider."""
        return self.data_provider.get_action_result(action, item.id, data)

    def get_tray_summary(self, business_id: int) -> Dict[str, Any]:
        """Get summary of tray items by priority and type."""
        items = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.status == TrayItemStatuses.PENDING
        ).all()
        
        summary = {
            "total_items": len(items),
            "by_priority": {"high": 0, "medium": 0, "low": 0},
            "by_type": {},
            "total_runway_impact": {"cash_impact": 0, "days_impact": 0},
            "urgent_count": 0
        }
        
        for item in items:
            # Priority distribution using constants
            priority_score = self.calculate_priority_score(item)
            if priority_score >= TrayPriorities.URGENT_SCORE:
                summary["by_priority"]["high"] += 1
                summary["urgent_count"] += 1
            elif priority_score >= TrayPriorities.MEDIUM_SCORE:
                summary["by_priority"]["medium"] += 1
            else:
                summary["by_priority"]["low"] += 1
            
            # Type distribution
            summary["by_type"][item.type] = summary["by_type"].get(item.type, 0) + 1
            
            # Runway impact
            impact = self._calculate_runway_impact(item)
            summary["total_runway_impact"]["cash_impact"] += impact["cash_impact"]
            summary["total_runway_impact"]["days_impact"] += impact["days_impact"]
        
        return summary
