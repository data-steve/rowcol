"""
Runway Calculation Service

Pure runway calculation service for calculating runway metrics and cash flow projections.
This service contains ONLY pure runway calculations - no entity-specific logic.

Key Calculations:
- Current runway days based on cash position and burn rate
- Scenario impact analysis (what-if scenarios)
- Historical runway analysis for trend analysis
- Weekly runway analysis for digest reports
- Utility functions for extracting financial data

This service is stateless and receives all data as parameters.
Entity-specific impact calculations are handled by separate services.
"""

from sqlalchemy.orm import Session
from domains.core.services.base_service import TenantAwareService
from infra.config import RunwayAnalysisSettings, RunwayThresholds
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RunwayCalculationService(TenantAwareService):
    """Pure runway calculation service - no entity-specific logic."""
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        super().__init__(db, business_id, validate_business)
    
    def calculate_current_runway(self, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate current runway based on provided financial data.
        
        Args:
            qbo_data: Dictionary containing bills, invoices, and balances data
            
        Returns:
            Dict containing current runway days, burn rate, cash position, etc.
        """
        # Validate input data
        if qbo_data is None:
            raise ValueError("qbo_data is required - RunwayCalculator is now a pure calculation service")
        
        try:
            # Extract financial components from provided data
            cash_position = self._calculate_cash_position(qbo_data)
            burn_rate = self._calculate_burn_rate(qbo_data)
            ar_position = self._calculate_ar_position(qbo_data)
            ap_position = self._calculate_ap_position(qbo_data)
            
            # Calculate base runway
            net_position = cash_position + ar_position - ap_position
            base_runway_days = net_position / burn_rate["daily_burn"] if burn_rate["daily_burn"] > 0 else 0
            
            # Calculate optimized runway (with timing improvements)
            optimization_impact = self._calculate_optimization_impact(qbo_data, burn_rate["daily_burn"])
            optimized_runway_days = base_runway_days + optimization_impact["total_optimization"]["additional_days"]
            
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "cash_position": cash_position,
                "ar_expected": ar_position,  # Expected AR collections
                "ap_due": ap_position,       # AP due for payment
                "net_position": net_position,
                "burn_rate": burn_rate,
                "base_runway_days": base_runway_days,
                "optimized_runway_days": optimized_runway_days,
                "optimization_impact": optimization_impact,
                "runway_status": self._determine_runway_status(base_runway_days),
                "forecast_accuracy": self._assess_forecast_accuracy(qbo_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate runway for {self.business_id}: {e}", exc_info=True)
            return {
                "business_id": self.business_id,
                "calculated_at": datetime.now().isoformat(),
                "error": "Could not calculate runway",
                "cash_position": 0,
                "ar_expected": 0,
                "ap_due": 0,
                "base_runway_days": 0,
                "optimized_runway_days": 0,
                "runway_status": "unknown"
            }
    
    def calculate_scenario_impact(self, scenario: Dict[str, Any], 
                                qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate runway impact of a specific scenario.
        
        Args:
            scenario: Dict describing the scenario (e.g., delay payment, accelerate collection)
            qbo_data: QBO data containing bills, invoices, and balances
            
        Returns:
            Dict containing scenario impact analysis
        """
        try:
            # Get baseline runway
            baseline = self.calculate_current_runway(qbo_data)
            
            # Apply scenario modifications
            modified_data = self._apply_scenario_modifications(qbo_data or {}, scenario)
            scenario_runway = self.calculate_current_runway(modified_data)
            
            # Calculate impact
            runway_delta = scenario_runway["base_runway_days"] - baseline["base_runway_days"]
            
            return {
                "scenario_name": scenario.get("name", "Unnamed Scenario"),
                "baseline_runway_days": baseline["base_runway_days"],
                "scenario_runway_days": scenario_runway["base_runway_days"],
                "runway_impact_days": runway_delta,
                "impact_percentage": (runway_delta / baseline["base_runway_days"] * 100) if baseline["base_runway_days"] > 0 else 0,
                "scenario_details": scenario,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate scenario impact for {self.business_id}: {e}", exc_info=True)
            return {
                "scenario_name": scenario.get("name", "Unknown"),
                "error": "Could not calculate scenario impact",
                "runway_impact_days": 0
            }
    
    def calculate_weekly_analysis(self, week_start: datetime, week_end: datetime, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate runway analysis for a specific week period.
        
        Args:
            week_start: Start of the week
            week_end: End of the week
            qbo_data: QBO data for analysis
            
        Returns:
            Dict containing week-specific runway analysis
        """
        # Use current runway calculation as the base
        week_analysis = self.calculate_current_runway(qbo_data=qbo_data)
        
        # Add week-specific formatting
        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "runway_days": float(week_analysis.get("runway_days", 0.0)),
            "runway_protected_days": float(week_analysis.get("runway_protected_days", 0.0)),
            "insights_shown": week_analysis.get("insights", []),
            "critical_issues": week_analysis.get("critical_issues_count", 0),
            "bills_analyzed": len(qbo_data.get("bills", [])),
            "invoices_analyzed": len(qbo_data.get("invoices", [])),
            "cash_flow_impact": float(week_analysis.get("cash_flow_impact", 0.0)),
            "recommendations": week_analysis.get("recommendations", []),
            # Financial position data
            "cash_position": int(week_analysis.get("cash_position", sum(balance.get("current_balance", 0) for balance in qbo_data.get("balances", [])))),
            "ar_outstanding": int(sum(invoice.get("amount", 0) for invoice in qbo_data.get("invoices", []))),
            "ap_upcoming": int(sum(bill.get("amount", 0) for bill in qbo_data.get("bills", [])))
        }
    
    async def calculate_historical_runway(self, weeks_back: int = 4, qbo_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Calculate what runway would have been for historical periods.
        Used for runway replay and trend analysis.
        """
        try:
            historical_data = []
            current_date = datetime.now()
            
            # QBO data must be provided - RunwayCalculator is now a pure calculation service
            if qbo_data is None:
                raise ValueError("qbo_data is required - RunwayCalculator is now a pure calculation service")
            
            for week_offset in range(weeks_back, 0, -1):
                week_start = current_date - timedelta(weeks=week_offset)
                week_end = week_start + timedelta(days=6)
                
                # Simulate historical state (in real implementation, this would use actual historical data)
                historical_qbo_data = self._simulate_historical_data(qbo_data, week_start, week_end)
                historical_runway = self.calculate_current_runway(historical_qbo_data)
                
                # Handle error cases gracefully
                if "error" in historical_runway:
                    logger.warning(f"Historical runway calculation failed for week {week_start}: {historical_runway.get('error')}")
                    continue
                
                historical_data.append({
                    "week_start": week_start.strftime("%Y-%m-%d"),
                    "week_end": week_end.strftime("%Y-%m-%d"),
                    "week_label": f"Week of {week_start.strftime('%b %d')}",
                    "runway_days": historical_runway["base_runway_days"],
                    "cash_position": historical_runway["cash_position"],
                    "burn_rate": historical_runway["burn_rate"]["daily_burn"] if isinstance(historical_runway["burn_rate"], dict) else historical_runway["burn_rate"],
                    "optimization_opportunities": self._identify_historical_opportunities(historical_qbo_data)
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to calculate historical runway for {self.business_id}: {e}", exc_info=True)
            return []
    
    def _calculate_cash_position(self, qbo_data: Dict[str, Any]) -> float:
        """Calculate total cash position from QBO data."""
        balances = qbo_data.get("balances", [])
        return sum(balance.get("current_balance", 0) for balance in balances)
    
    def _calculate_burn_rate(self, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate burn rate from QBO data."""
        bills = qbo_data.get("bills", [])
        
        # Calculate monthly expenses from bills
        monthly_expenses = sum(bill.get("amount", 0) for bill in bills) if bills else 0
        daily_burn = monthly_expenses / 30 if monthly_expenses > 0 else RunwayAnalysisSettings.DEFAULT_DAILY_BURN_RATE
        
        return {
            "monthly_expenses": monthly_expenses,
            "daily_burn": daily_burn,
            "calculation_method": "bills_based" if monthly_expenses > 0 else "default_estimate"
        }
    
    def _calculate_ar_position(self, qbo_data: Dict[str, Any]) -> float:
        """Calculate accounts receivable position."""
        invoices = qbo_data.get("invoices", [])
        return sum(inv.get("amount", 0) for inv in invoices if inv.get("status") != "paid")
    
    def _calculate_ap_position(self, qbo_data: Dict[str, Any]) -> float:
        """Calculate accounts payable position."""
        bills = qbo_data.get("bills", [])
        return sum(bill.get("amount", 0) for bill in bills if bill.get("status") != "paid")
    
    def _calculate_optimization_impact(self, qbo_data: Dict[str, Any], daily_burn: float) -> Dict[str, Any]:
        """Calculate potential runway improvement from optimization."""
        bills = qbo_data.get("bills", [])
        invoices = qbo_data.get("invoices", [])
        
        # AP optimization potential
        overdue_bills = [bill for bill in bills if self._is_overdue(bill)]
        ap_optimization_amount = sum(bill.get("amount", 0) for bill in overdue_bills) * RunwayAnalysisSettings.AP_OPTIMIZATION_EFFICIENCY
        ap_days_gained = ap_optimization_amount / daily_burn if daily_burn > 0 else 0
        
        # AR optimization potential
        overdue_invoices = [inv for inv in invoices if self._is_overdue(inv)]
        ar_optimization_amount = sum(inv.get("amount", 0) for inv in overdue_invoices) * RunwayAnalysisSettings.AR_COLLECTION_EFFICIENCY
        ar_days_gained = ar_optimization_amount / daily_burn if daily_burn > 0 else 0
        
        total_days_gained = ap_days_gained + ar_days_gained
        
        return {
            "ap_optimization": {
                "potential_amount": ap_optimization_amount,
                "days_gained": ap_days_gained,
                "overdue_bills_count": len(overdue_bills)
            },
            "ar_optimization": {
                "potential_amount": ar_optimization_amount,
                "days_gained": ar_days_gained,
                "overdue_invoices_count": len(overdue_invoices)
            },
            "total_optimization": {
                "potential_amount": ap_optimization_amount + ar_optimization_amount,
                "additional_days": total_days_gained
            }
        }
    
    def _determine_runway_status(self, runway_days: float) -> str:
        """Determine runway status based on days remaining."""
        if runway_days < RunwayThresholds.CRITICAL_DAYS:
            return "critical"
        elif runway_days < RunwayThresholds.WARNING_DAYS:
            return "warning"
        elif runway_days < RunwayThresholds.HEALTHY_DAYS:
            return "healthy"
        else:
            return "excellent"
    
    def _assess_forecast_accuracy(self, qbo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the accuracy of runway forecast based on data quality."""
        bills = qbo_data.get("bills", [])
        invoices = qbo_data.get("invoices", [])
        
        # Count missing critical data
        bills_missing_due_dates = sum(1 for bill in bills if not bill.get("due_date"))
        invoices_missing_due_dates = sum(1 for inv in invoices if not inv.get("due_date"))
        total_items = len(bills) + len(invoices)
        
        if total_items == 0:
            accuracy_score = 0
        else:
            missing_percentage = (bills_missing_due_dates + invoices_missing_due_dates) / total_items
            accuracy_score = max(0, 100 - (missing_percentage * 100))
        
        return {
            "accuracy_score": accuracy_score,
            "confidence_level": "high" if accuracy_score >= 90 else "medium" if accuracy_score >= 70 else "low",
            "data_quality_issues": {
                "bills_missing_due_dates": bills_missing_due_dates,
                "invoices_missing_due_dates": invoices_missing_due_dates
            }
        }
    
    def _is_overdue(self, item: Dict[str, Any]) -> bool:
        """Check if a bill or invoice is overdue."""
        due_date_str = item.get("due_date")
        if not due_date_str:
            return False
        
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            return due_date < datetime.now()
        except (ValueError, TypeError):
            return False
    
    def _apply_scenario_modifications(self, qbo_data: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Apply scenario modifications to QBO data for impact analysis."""
        # This would implement scenario-specific modifications
        # For now, return data unchanged
        return qbo_data.copy()
    
    def _simulate_historical_data(self, current_data: Dict[str, Any], week_start: datetime, week_end: datetime) -> Dict[str, Any]:
        """
        TODO: Replace with actual historical data retrieval.
        
        This is a temporary implementation that returns current data.
        In production, this should:
        1. Query historical QBO data for the specific time period
        2. Use audit logs to reconstruct past state
        3. Apply time-based filtering to transactions
        
        For MVP, we return current data as a placeholder.
        """
        # TODO: Implement actual historical data retrieval
        logger.warning(f"Using current data as historical placeholder for {week_start} - {week_end}")
        return current_data.copy()
    
    def _identify_historical_opportunities(self, historical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities for historical data."""
        opportunities = []
        
        bills = historical_data.get("bills", [])
        invoices = historical_data.get("invoices", [])
        
        # Check for overdue items
        overdue_bills = [bill for bill in bills if self._is_overdue(bill)]
        overdue_invoices = [inv for inv in invoices if self._is_overdue(inv)]
        
        if overdue_bills:
            opportunities.append({
                "type": "ap_timing",
                "description": f"Optimize timing for {len(overdue_bills)} overdue bills",
                "potential_impact": "runway_extension"
            })
        
        if overdue_invoices:
            opportunities.append({
                "type": "ar_collection",
                "description": f"Accelerate collection of {len(overdue_invoices)} overdue invoices",
                "potential_impact": "cash_acceleration"
            })
        
        return opportunities
    
    def format_for_presentation(self, weeks_data: List[Dict[str, Any]], format_type: str = "standard") -> List[Dict[str, Any]]:
        """
        Format runway analysis data for different presentation contexts.
        
        Args:
            weeks_data: Raw runway analysis data
            format_type: Presentation format ("standard", "test_drive", "digest")
            
        Returns:
            Formatted data appropriate for the specified presentation context
        """
        formatted_weeks = []
        
        for week in weeks_data:
            if format_type == "test_drive":
                # Format for proof-of-value demonstration
                formatted_week = {
                    "week_start": week.get("week_start"),
                    "week_end": week.get("week_end"),
                    "week_label": week.get("week_label"),
                    "runway_days": week.get("runway_days", 0),
                    "cash_position": week.get("cash_position", 0),
                    "runway_protected_days": len(week.get("optimization_opportunities", [])) * 2,  # Estimate impact
                    "insights_shown": week.get("optimization_opportunities", []),
                    "critical_issues": 1 if week.get("runway_days", 0) < RunwayThresholds.WARNING_DAYS else 0
                }
            else:
                # Standard format for regular analysis
                formatted_week = {
                    "week_start": week.get("week_start"),
                    "week_end": week.get("week_end"),
                    "week_label": week.get("week_label"),
                    "runway_days": week.get("runway_days", 0),
                    "cash_position": week.get("cash_position", 0),
                    "optimization_opportunities": week.get("optimization_opportunities", [])
                }
            
            formatted_weeks.append(formatted_week)
        
        return formatted_weeks


    def calculate_daily_burn_rate(self, qbo_data: Dict[str, Any]) -> float:
        """Calculate daily burn rate from provided QBO data."""
        try:
            burn_rate_data = self._calculate_burn_rate(qbo_data)
            return burn_rate_data.get('daily_burn', RunwayAnalysisSettings.DEFAULT_DAILY_BURN_RATE)
        except Exception as e:
            logger.error(f"Failed to calculate daily burn rate: {e}")
            return RunwayAnalysisSettings.DEFAULT_DAILY_BURN_RATE

  
