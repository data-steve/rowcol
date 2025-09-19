from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from runway.tray.models.tray_item import TrayItem
from runway.tray.providers import TrayDataProvider, get_tray_data_provider
from domains.integrations.smart_sync import SmartSyncService
from runway.reserves.services.runway_reserve_service import RunwayReserveService
from common.exceptions import TrayItemNotFoundError
from config.business_rules import TrayPriorities, TrayItemStatuses
from datetime import datetime
import os

class TrayService:
    def __init__(self, db: Session, business_id: str = None, data_provider: Optional[TrayDataProvider] = None):
        self.db = db
        self.business_id = business_id
        self.data_provider = data_provider or get_tray_data_provider()
        self.smart_sync = SmartSyncService(db, business_id) if business_id else None
        self.reserve_service = RunwayReserveService(db, business_id) if business_id else None
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
    
    def categorize_bill_urgency(self, bill_data: Dict[str, Any]) -> str:
        """
        Categorize a bill as 'must_pay' or 'can_delay' based on business rules.
        
        Args:
            bill_data: Dictionary containing bill information (amount, due_date, vendor, etc.)
        
        Returns:
            String: 'must_pay' or 'can_delay'
        """
        if not self.reserve_service:
            return "must_pay"  # Conservative default
        
        try:
            amount = float(bill_data.get("amount", 0))
            due_date_str = bill_data.get("due_date")
            vendor_name = bill_data.get("vendor_name", "").lower()
            bill_type = bill_data.get("type", "").lower()
            
            # Get current runway calculation
            runway_calc = self.reserve_service.calculate_runway_with_reserves()
            current_runway = runway_calc.get("runway_days", 0)
            daily_burn = runway_calc.get("daily_burn", 1)
            
            # Calculate days until due
            days_until_due = 0
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_until_due = (due_date - datetime.utcnow()).days
                except:
                    days_until_due = 0
            
            # MUST PAY criteria (any one triggers must pay)
            
            # 1. Already overdue
            if days_until_due < 0:
                return "must_pay"
            
            # 2. Critical vendors (utilities, rent, payroll, taxes)
            critical_vendors = ["electric", "gas", "water", "rent", "lease", "payroll", "irs", "tax", "insurance"]
            if any(keyword in vendor_name for keyword in critical_vendors):
                return "must_pay"
            
            # 3. Critical bill types
            critical_types = ["payroll", "tax", "insurance", "rent", "utilities"]
            if any(keyword in bill_type for keyword in critical_types):
                return "must_pay"
            
            # 4. Large amounts that would significantly impact runway
            runway_impact_days = amount / daily_burn if daily_burn > 0 else 0
            if runway_impact_days > (current_runway * 0.15):  # More than 15% of runway
                return "must_pay"
            
            # 5. Due within 3 days (urgent)
            if days_until_due <= 3:
                return "must_pay"
            
            # 6. Would put runway below critical threshold (30 days)
            runway_after_payment = current_runway - runway_impact_days
            if runway_after_payment < 30:
                return "must_pay"
            
            # CAN DELAY criteria (all others)
            
            # 7. Due in more than 14 days with sufficient runway
            if days_until_due > 14 and current_runway > 60:
                return "can_delay"
            
            # 8. Small amounts with good runway
            if amount < (daily_burn * 5) and current_runway > 45:  # Less than 5 days of burn
                return "can_delay"
            
            # 9. Non-critical vendors with good runway buffer
            if current_runway > 90 and days_until_due > 7:
                return "can_delay"
            
            # Default to must_pay for safety
            return "must_pay"
            
        except Exception:
            # If any error occurs, default to conservative must_pay
            return "must_pay"
    
    def get_payment_decision_analysis(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide comprehensive analysis for payment decision making.
        
        Args:
            bill_data: Dictionary containing bill information
        
        Returns:
            Dictionary with categorization, runway impact, and recommendations
        """
        if not self.reserve_service:
            return {
                "category": "must_pay",
                "runway_impact": {"error": "Runway service not available"},
                "recommendation": "Pay immediately (no runway analysis available)"
            }
        
        try:
            # Get basic categorization
            category = self.categorize_bill_urgency(bill_data)
            
            # Get runway calculations
            runway_calc = self.reserve_service.calculate_runway_with_reserves()
            current_runway = runway_calc.get("runway_days", 0)
            daily_burn = runway_calc.get("daily_burn", 1)
            available_cash = runway_calc.get("available_cash", 0)
            
            amount = float(bill_data.get("amount", 0))
            due_date_str = bill_data.get("due_date")
            vendor_name = bill_data.get("vendor_name", "Unknown")
            
            # Calculate runway impact
            runway_impact_days = amount / daily_burn if daily_burn > 0 else 0
            runway_after_payment = current_runway - runway_impact_days
            cash_after_payment = available_cash - amount
            
            # Calculate days until due
            days_until_due = 0
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_until_due = (due_date - datetime.utcnow()).days
                except:
                    days_until_due = 0
            
            # Generate payment scenarios
            scenarios = {
                "pay_now": {
                    "runway_days": runway_after_payment,
                    "cash_remaining": cash_after_payment,
                    "risk_level": "low" if runway_after_payment > 60 else "medium" if runway_after_payment > 30 else "high"
                },
                "pay_on_due_date": {
                    "runway_days": runway_after_payment,  # Same impact, different timing
                    "cash_remaining": cash_after_payment,
                    "additional_risk": "penalty" if days_until_due < 0 else "none"
                },
                "delay_30_days": {
                    "runway_days": runway_after_payment,
                    "cash_remaining": cash_after_payment,
                    "risk_level": "high" if days_until_due <= 0 else "medium",
                    "potential_penalties": "late_fees" if days_until_due <= 30 else "relationship_damage"
                }
            }
            
            # Generate recommendation
            if category == "must_pay":
                if days_until_due <= 0:
                    recommendation = f"PAY IMMEDIATELY - {vendor_name} bill is overdue"
                elif days_until_due <= 3:
                    recommendation = f"PAY TODAY - {vendor_name} bill due in {days_until_due} days"
                else:
                    recommendation = f"PAY BY DUE DATE - Critical payment for {vendor_name}"
            else:
                if current_runway > 90:
                    recommendation = f"CAN DELAY - Strong runway position allows flexibility with {vendor_name}"
                elif current_runway > 60:
                    recommendation = f"MONITOR - Can delay but watch runway impact ({runway_impact_days:.1f} days)"
                else:
                    recommendation = "CAUTION - Delay only if necessary, limited runway buffer"
            
            return {
                "category": category,
                "vendor_name": vendor_name,
                "amount": amount,
                "days_until_due": days_until_due,
                "runway_impact": {
                    "current_runway_days": current_runway,
                    "impact_days": runway_impact_days,
                    "runway_after_payment": runway_after_payment,
                    "impact_percentage": (runway_impact_days / current_runway * 100) if current_runway > 0 else 0
                },
                "scenarios": scenarios,
                "recommendation": recommendation,
                "decision_factors": self._get_decision_factors(bill_data, category, current_runway, days_until_due)
            }
            
        except Exception as e:
            return {
                "category": "must_pay",
                "error": str(e),
                "recommendation": "Pay immediately (error in analysis)"
            }
    
    def get_enhanced_tray_items(self, business_id: int, include_runway_analysis: bool = True) -> List[Dict[str, Any]]:
        """
        Get tray items with enhanced Must Pay vs Can Delay categorization and runway impact.
        
        Args:
            business_id: Business identifier
            include_runway_analysis: Whether to include detailed runway impact analysis
        
        Returns:
            List of enhanced tray items with categorization and runway impact
        """
        try:
            # Get base tray items
            base_items = self.get_tray_items(business_id)
            
            if not include_runway_analysis or not self.smart_sync:
                return base_items
            
            # Get QBO data for enhanced analysis
            qbo_data = self.smart_sync.get_qbo_data_for_digest()
            bills_data = qbo_data.get("bills", [])
            
            enhanced_items = []
            
            for item in base_items:
                enhanced_item = dict(item)  # Copy base item
                
                # Find corresponding bill data if it's a bill-related item
                if item.get("type") in ["overdue_bill", "upcoming_bill", "bill_approval"]:
                    bill_data = None
                    
                    # Try to match with QBO bill data
                    if item.get("qbo_id"):
                        bill_data = next((b for b in bills_data if b.get("Id") == item.get("qbo_id")), None)
                    
                    # Create bill data structure for analysis
                    if bill_data:
                        analysis_data = {
                            "amount": float(bill_data.get("TotalAmt", 0)),
                            "due_date": bill_data.get("DueDate"),
                            "vendor_name": bill_data.get("VendorRef", {}).get("name", "Unknown"),
                            "type": item.get("type", "")
                        }
                    else:
                        # Use tray item data as fallback
                        analysis_data = {
                            "amount": item.get("amount", 0),
                            "due_date": item.get("due_date"),
                            "vendor_name": item.get("description", "Unknown"),
                            "type": item.get("type", "")
                        }
                    
                    # Get payment decision analysis
                    decision_analysis = self.get_payment_decision_analysis(analysis_data)
                    
                    # Enhance the tray item
                    enhanced_item.update({
                        "payment_category": decision_analysis["category"],
                        "runway_impact": decision_analysis.get("runway_impact", {}),
                        "payment_recommendation": decision_analysis.get("recommendation", ""),
                        "decision_factors": decision_analysis.get("decision_factors", []),
                        "payment_scenarios": decision_analysis.get("scenarios", {})
                    })
                    
                    # Update priority based on categorization
                    if decision_analysis["category"] == "must_pay":
                        enhanced_item["priority"] = "high"
                        enhanced_item["urgency_level"] = "critical" if decision_analysis.get("days_until_due", 0) <= 0 else "high"
                    else:
                        enhanced_item["urgency_level"] = "low"
                
                enhanced_items.append(enhanced_item)
            
            # Sort by payment category (must_pay first) then by priority
            enhanced_items.sort(key=lambda x: (
                0 if x.get("payment_category") == "must_pay" else 1,
                {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1)
            ))
            
            return enhanced_items
            
        except Exception:
            # Return base items if enhancement fails
            return self.get_tray_items(business_id)
    
    def _get_decision_factors(self, bill_data: Dict[str, Any], category: str, current_runway: float, days_until_due: int) -> List[str]:
        """Get list of factors that influenced the payment decision."""
        factors = []
        
        amount = float(bill_data.get("amount", 0))
        vendor_name = bill_data.get("vendor_name", "").lower()
        
        if days_until_due < 0:
            factors.append("Bill is overdue")
        elif days_until_due <= 3:
            factors.append("Due within 3 days")
        
        critical_vendors = ["electric", "gas", "water", "rent", "lease", "payroll", "irs", "tax", "insurance"]
        if any(keyword in vendor_name for keyword in critical_vendors):
            factors.append("Critical vendor (utilities, rent, taxes, etc.)")
        
        if current_runway < 30:
            factors.append("Low runway (less than 30 days)")
        elif current_runway > 90:
            factors.append("Strong runway (more than 90 days)")
        
        if amount > 5000:
            factors.append("Large amount (over $5,000)")
        elif amount < 500:
            factors.append("Small amount (under $500)")
        
        if category == "must_pay" and not factors:
            factors.append("Conservative approach - default to must pay")
        
        return factors
