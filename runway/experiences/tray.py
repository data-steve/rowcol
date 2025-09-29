"""
TrayService - Refactored to use Data Orchestrator Pattern and Focused Calculation Services

This service orchestrates tray functionality using the Data Orchestrator Pattern
and focused calculation services. This eliminates duplication and establishes
single sources of truth for all calculation logic.

Key Changes:
- Data orchestrator handles data pulling + state management
- RunwayCalculationService handles pure runway calculations
- PriorityCalculationService handles all priority scoring
- BillImpactCalculator handles bill-specific impact calculations (stateless)
- TrayItemImpactCalculator handles tray item impact calculations (stateless)
- Maintains orchestration and data provider functionality
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from runway.models.tray_item import TrayItem
from runway.core.data_orchestrators.hygiene_tray_data_orchestrator import HygieneTrayDataOrchestrator
from runway.core.runway_calculation_service import RunwayCalculationService
from runway.core.priority_calculation_service import PriorityCalculationService
from runway.core.bill_impact_calculator import BillImpactCalculator
from runway.core.tray_item_impact_calculator import TrayItemImpactCalculator
from runway.core.reserve_runway import RunwayReserveService
from common.exceptions import TrayItemNotFoundError
from infra.config import TrayPriorities, TrayItemStatuses
from datetime import datetime
import os
import logging

# Domain services handle all database operations - no direct model imports needed

logger = logging.getLogger(__name__)

class TrayService:
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        
        # Data orchestrator handles data pulling + state management
        self.data_orchestrator = HygieneTrayDataOrchestrator(db)
        self.reserve_service = RunwayReserveService(db, business_id)
        
        # Calculation services handle business logic
        self.runway_calculator = RunwayCalculationService(db, business_id, validate_business=False) if business_id else None
        self.priority_calculator = PriorityCalculationService(db, business_id, validate_business=False) if business_id else None
        
        # Stateless impact calculators (no dependencies)
        self.bill_impact_calculator = BillImpactCalculator()
        self.tray_item_impact_calculator = TrayItemImpactCalculator()
        
        # Use centralized QBO config
        from infra.qbo.config import qbo_config
        self.qbo_base_url = qbo_config.api_base_url
        self.realm_id = os.getenv("QBO_REALM_ID")

    def calculate_priority_score(self, item: TrayItem) -> int:
        """Calculate priority score using centralized PriorityCalculationService."""
        if not self.priority_calculator:
            raise RuntimeError("PriorityCalculationService not available - this is a critical service that should always be initialized")
        
        # Convert TrayItem to dict format for canonical service
        item_data = {
            'type': getattr(item, 'type', ''),
            'amount': getattr(item, 'amount', 0),
            'due_date': getattr(item, 'due_date', None),
            'metadata': getattr(item, 'metadata', {})
        }
        
        priority_analysis = self.priority_calculator.calculate_tray_item_priority(item_data)
        return int(priority_analysis.get('priority_score', 50))

    async def get_tray_items(self, business_id: str) -> List[Dict[str, Any]]:
        """Get tray items using data orchestrator and calculation services."""
        try:
            # Get data from orchestrator
            tray_data = await self.data_orchestrator.get_tray_data(business_id)
            
            # Get runway context for impact calculations
            runway_context = None
            if self.runway_calculator:
                runway_context = self.runway_calculator.calculate_current_runway(tray_data)
            
            tray_items = []
            
            # Convert bills to tray items with impact calculations
            if "bills" in tray_data:
                for bill in tray_data["bills"]:
                    bill_data = {
                        "amount": bill.get("total_amount", 0),
                        "due_date": bill.get("due_date"),
                        "vendor_name": bill.get("vendor_name", ""),
                        "qbo_id": str(bill.get("qbo_id", bill.get("id", "")))
                    }
                    
                    # Calculate priority using centralized service
                    priority_score = 50  # Default
                    if self.priority_calculator:
                        priority_score = self.priority_calculator.calculate_bill_priority_score(bill_data)
                    
                    # Calculate impact using stateless calculator
                    impact_data = {}
                    if runway_context:
                        impact_data = self.bill_impact_calculator.calculate_bill_runway_impact(bill_data, runway_context)
                    
                    tray_items.append({
                        "business_id": business_id,
                        "type": "bill",
                        "qbo_id": str(bill.get("qbo_id", bill.get("id", ""))),
                        "due_date": bill.get("due_date"),
                        "amount": bill.get("total_amount", 0),
                        "priority": self._score_to_priority_level(priority_score),
                        "priority_score": priority_score,
                        "impact_data": impact_data,
                        "status": "pending"
                    })
            
            # Convert invoices to tray items with impact calculations
            if "invoices" in tray_data:
                for invoice in tray_data["invoices"]:
                    invoice_data = {
                        "amount": invoice.get("total_amount", 0),
                        "due_date": invoice.get("due_date"),
                        "customer_name": invoice.get("customer_name", ""),
                        "qbo_id": str(invoice.get("qbo_id", invoice.get("id", "")))
                    }
                    
                    # Calculate priority using centralized service
                    priority_score = 50  # Default
                    if self.priority_calculator:
                        priority_score = self.priority_calculator.calculate_invoice_priority_score(invoice_data)
                    
                    # Calculate impact using stateless calculator
                    impact_data = {}
                    if runway_context:
                        item_data = {
                            "amount": invoice.get("total_amount", 0),
                            "type": "invoice",
                            "issue_type": "incomplete_data"  # Could be enhanced with actual issue detection
                        }
                        impact_data = self.tray_item_impact_calculator.calculate_tray_item_runway_impact(item_data, runway_context)
                    
                    tray_items.append({
                        "business_id": business_id,
                        "type": "invoice",
                        "qbo_id": str(invoice.get("qbo_id", invoice.get("id", ""))),
                        "due_date": invoice.get("due_date"),
                        "amount": invoice.get("total_amount", 0),
                        "priority": self._score_to_priority_level(priority_score),
                        "priority_score": priority_score,
                        "impact_data": impact_data,
                        "status": "pending"
                    })
            
            return tray_items
            
        except Exception as e:
            logger.error(f"Failed to fetch QBO tray items for business {business_id}: {e}")
            return []
    
    def _score_to_priority_level(self, score: float) -> str:
        """Convert priority score to priority level."""
        if score >= 80:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"
    

    async def get_tray_summary(self, business_id: str) -> Dict[str, Any]:
        """Get tray summary using new calculation architecture."""
        items = await self.get_tray_items(business_id)
        
        summary = {
            "total_items": len(items),
            "urgent_count": 0,
            "by_priority": {"high": 0, "medium": 0, "low": 0},
            "by_type": {},
            "total_runway_impact": {"cash_impact": 0, "days_impact": 0}
        }
        
        for item in items:
            # Use priority score from new architecture
            priority_score = item.get('priority_score', 50)
            impact_data = item.get('impact_data', {})
            
            # Priority distribution
            if priority_score >= 80:
                summary["by_priority"]["high"] += 1
                summary["urgent_count"] += 1
            elif priority_score >= 50:
                summary["by_priority"]["medium"] += 1
            else:
                summary["by_priority"]["low"] += 1
            
            # Type distribution
            item_type = item.get('type', 'unknown')
            summary["by_type"][item_type] = summary["by_type"].get(item_type, 0) + 1
            
            # Runway impact
            summary["total_runway_impact"]["cash_impact"] += impact_data.get("cash_impact", 0)
            summary["total_runway_impact"]["days_impact"] += impact_data.get("days_impact", 0)
        
        return summary
    
    def categorize_bill_urgency(self, bill_data: Dict[str, Any]) -> str:
        """Categorize bill urgency using centralized PriorityCalculationService."""
        if not self.priority_calculator:
            raise RuntimeError("PriorityCalculationService not available - this is a critical service that should always be initialized")
        
        priority_score = self.priority_calculator.calculate_bill_priority_score(bill_data)
        return self._score_to_priority_level(priority_score)

    def get_payment_decision_analysis(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment decision analysis using new calculation architecture."""
        if not self.priority_calculator or not self.runway_calculator:
            raise RuntimeError("Required calculation services not available")
        
        # Get priority score
        priority_score = self.priority_calculator.calculate_bill_priority_score(bill_data)
        
        # Get runway context for impact calculation
        runway_context = self.runway_calculator.calculate_current_runway({})
        
        # Calculate impact using stateless calculator
        impact_data = self.bill_impact_calculator.calculate_bill_runway_impact(bill_data, runway_context)
        
        return {
            "priority_score": priority_score,
            "priority_level": self._score_to_priority_level(priority_score),
            "impact_data": impact_data
        }

    def _calculate_runway_impact(self, item: TrayItem) -> Dict[str, Any]:
        """Calculate runway impact using new calculation architecture."""
        if not self.runway_calculator:
            raise RuntimeError("RunwayCalculationService not available - this is a critical service that should always be initialized")
        
        # Convert TrayItem to dict format
        item_data = {
            'amount': getattr(item, 'amount', 0),
            'type': getattr(item, 'type', ''),
            'due_date': getattr(item, 'due_date', None),
            'issue_type': 'unknown'  # Could be enhanced with actual issue detection
        }
        
        # Get runway context
        runway_context = self.runway_calculator.calculate_current_runway({})
        
        # Calculate impact using stateless calculator
        return self.tray_item_impact_calculator.calculate_tray_item_runway_impact(item_data, runway_context)

    async def get_enhanced_tray_items(self, business_id: str, include_runway_analysis: bool = True) -> List[Dict[str, Any]]:
        """
        Get enhanced tray items with priority and runway analysis using new calculation architecture.
        
        Args:
            business_id: ID of the business
            include_runway_analysis: Whether to include runway impact analysis
        
        Returns:
            List of enhanced tray items with categorization and runway impact
        """
        try:
            # Get base tray items (already includes priority and impact calculations)
            enhanced_items = await self.get_tray_items(business_id)
            
            if not include_runway_analysis:
                # Remove impact data if not needed
                for item in enhanced_items:
                    item.pop('impact_data', None)
            
            return enhanced_items
            
        except Exception as e:
            logger.error(f"Failed to get enhanced tray items: {e}")
            return []  # Return empty list if enhancement fails

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
        """Process bill payment with real QBO integration."""
        try:
            from domains.ap.services.bill_ingestion import BillService
            
            # Use real BillService for payment processing
            bill_service = BillService(self.db, self.business_id, validate_business=False)
            
            # Get the actual bill from database using BillService
            bill = bill_service.get_bill_by_qbo_id(item.qbo_id)
            
            if not bill:
                return {
                    "success": False,
                    "message": f"Bill not found for {item.title}",
                    "error": "bill_not_found"
                }
            
            # Use real bill approval and scheduling
            if bill_service.approve_bill_entity(bill, "api_user", "Approved via tray"):
                if bill_service.schedule_bill_payment(bill, datetime.utcnow()):
                    return {
                        "success": True,
                        "message": f"Bill payment processed for {item.title}",
                        "qbo_bill_id": bill.qbo_bill_id,
                        "amount": float(bill.amount)
                    }
            
            return {
                "success": False,
                "message": f"Failed to process payment for {item.title}",
                "error": "payment_processing_failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to process bill payment: {e}")
            return {
                "success": False,
                "message": f"Payment processing error: {str(e)}",
                "error": "system_error"
            }

    def _schedule_payment(self, item: TrayItem, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule payment for future date using real BillService."""
        try:
            from domains.ap.services.bill_ingestion import BillService
            from datetime import datetime
            
            scheduled_date = confirmation_data.get("scheduled_date")
            if not scheduled_date:
                return {
                    "success": False,
                    "message": "Scheduled date is required",
                    "error": "missing_scheduled_date"
                }
            
            # Parse scheduled date
            if isinstance(scheduled_date, str):
                scheduled_date = datetime.fromisoformat(scheduled_date)
            
            # Use real BillService for payment scheduling
            bill_service = BillService(self.db, self.business_id, validate_business=False)
            
            # Get the actual bill from database using BillService
            bill = bill_service.get_bill_by_qbo_id(item.qbo_id)
            
            if not bill:
                return {
                    "success": False,
                    "message": f"Bill not found for {item.title}",
                    "error": "bill_not_found"
                }
            
            # Use real bill approval and scheduling
            if bill_service.approve_bill_entity(bill, "api_user", "Scheduled via tray"):
                if bill_service.schedule_bill_payment(bill, scheduled_date):
                    return {
                        "success": True,
                        "message": f"Payment scheduled for {scheduled_date.isoformat()}",
                        "scheduled_date": scheduled_date.isoformat(),
                        "qbo_bill_id": bill.qbo_bill_id,
                        "amount": float(bill.amount)
                    }
            
            return {
                "success": False,
                "message": f"Failed to schedule payment for {item.title}",
                "error": "scheduling_failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule payment: {e}")
            return {
                "success": False,
                "message": f"Payment scheduling error: {str(e)}",
                "error": "system_error"
            }

    def _send_invoice_reminder(self, item: TrayItem, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send invoice reminder using real ARPlanService."""
        try:
            from runway.core.ar_collections_service import ARCollectionsService
            from domains.ar.services.invoice import InvoiceService
            
            # Use real services for reminder sending
            ar_collections_service = ARCollectionsService(self.db)
            invoice_service = InvoiceService(self.db, self.business_id)
            
            # Get the actual invoice from database using InvoiceService
            invoice = invoice_service.get_invoice_by_qbo_id(item.qbo_id)
            
            if not invoice:
                return {
                    "success": False,
                    "message": f"Invoice not found for {item.title}",
                    "error": "invoice_not_found"
                }
            
            # Use real AR collections service to send reminder
            updated_invoice = ar_collections_service.send_reminder(self.business_id, invoice.invoice_id)
            
            return {
                "success": True,
                "message": f"Reminder sent for invoice {item.title}",
                "reminder_type": confirmation_data.get("reminder_type", "email"),
                "qbo_invoice_id": invoice.qbo_invoice_id,
                "invoice_status": updated_invoice.status
            }
            
        except Exception as e:
            logger.error(f"Failed to send invoice reminder: {e}")
            return {
                "success": False,
                "message": f"Reminder sending error: {str(e)}",
                "error": "system_error"
            }

