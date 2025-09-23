"""
Runway Analytics KPIs API Routes

User-facing API endpoints for KPI analysis and business intelligence.
Orchestrates domains/core/ KPI services with runway-specific analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from db.session import get_db
from runway.auth.middleware.auth import get_current_business_id
from domains.core.services.kpi import KPIService
from domains.integrations.smart_sync import SmartSyncService
from runway.reserves.services.runway_reserve_service import RunwayReserveService

router = APIRouter(tags=["Analytics KPIs"])

def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "kpi_service": KPIService(db),
        "smart_sync": SmartSyncService(db, business_id),
        "reserve_service": RunwayReserveService(db, business_id)
    }

@router.get("/dashboard")
async def get_kpi_dashboard(
    services: Dict = Depends(get_services)
):
    """
    Get comprehensive KPI dashboard for business analytics.
    
    Combines operational KPIs with runway-specific metrics and cash flow analysis.
    """
    try:
        kpi_service = services["kpi_service"]
        smart_sync = services["smart_sync"]
        reserve_service = services["reserve_service"]
        business_id = services["smart_sync"].business_id
        
        # Get core operational KPIs (using business_id)
        core_kpis = kpi_service.calculate_kpis(business_id)
        
        # Get runway-specific metrics
        runway_calc = reserve_service.calculate_runway_with_reserves()
        
        # Get QBO sync and data quality metrics
        qbo_data = smart_sync.get_qbo_data_for_digest()
        
        # Calculate additional runway KPIs
        bills_data = qbo_data.get("bills", [])
        invoices_data = qbo_data.get("invoices", [])
        
        # AP KPIs
        total_bills = len(bills_data)
        overdue_bills = len([b for b in bills_data if _is_bill_overdue(b)])
        
        # AR KPIs  
        total_invoices = len(invoices_data)
        overdue_invoices = len([i for i in invoices_data if _is_invoice_overdue(i)])
        total_ar = sum(float(inv.get("Balance", 0)) for inv in invoices_data if float(inv.get("Balance", 0)) > 0)
        
        # Cash flow KPIs
        current_runway = runway_calc.get("runway_days", 0)
        daily_burn = runway_calc.get("daily_burn", 0)
        runway_trend = _calculate_runway_trend(runway_calc)  # TODO: Implement trend calculation
        
        return {
            "operational_kpis": {
                **core_kpis,
                "data_quality_score": _calculate_data_quality_score(qbo_data),
                "sync_health_score": _calculate_sync_health_score(smart_sync)
            },
            "cash_flow_kpis": {
                "current_runway_days": current_runway,
                "daily_burn_rate": daily_burn,
                "runway_trend_7d": runway_trend,
                "cash_flow_health": "healthy" if current_runway > 90 else "warning" if current_runway > 30 else "critical"
            },
            "ap_kpis": {
                "total_bills": total_bills,
                "overdue_bills": overdue_bills,
                "overdue_percentage": (overdue_bills / total_bills * 100) if total_bills > 0 else 0,
                "avg_payment_cycle": _calculate_avg_payment_cycle(bills_data)
            },
            "ar_kpis": {
                "total_invoices": total_invoices,
                "overdue_invoices": overdue_invoices,
                "overdue_percentage": (overdue_invoices / total_invoices * 100) if total_invoices > 0 else 0,
                "total_ar_outstanding": total_ar,
                "avg_collection_cycle": _calculate_avg_collection_cycle(invoices_data)
            },
            "efficiency_kpis": {
                "automation_rate": core_kpis.get("percent_auto_posted", 0),
                "manual_override_rate": core_kpis.get("override_rate", 0),
                "task_completion_rate": core_kpis.get("task_completion_rate", 0),
                "processing_efficiency": 100 - core_kpis.get("override_rate", 0)  # Inverse of override rate
            },
            "generated_at": datetime.utcnow().isoformat(),
            "period": "current"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KPI dashboard: {str(e)}"
        )

@router.get("/operational")
async def get_operational_kpis(
    services: Dict = Depends(get_services)
):
    """
    Get operational KPIs focused on process efficiency and automation.
    
    Shows transaction processing, automation rates, and manual intervention metrics.
    """
    try:
        kpi_service = services["kpi_service"]
        smart_sync = services["smart_sync"]
        business_id = services["smart_sync"].business_id
        
        # Get core KPIs
        core_kpis = kpi_service.calculate_kpis(business_id)
        
        # Get QBO data for additional calculations
        qbo_data = smart_sync.get_qbo_data_for_digest()
        
        return {
            "automation_metrics": {
                "auto_posting_rate": core_kpis.get("percent_auto_posted", 0),
                "manual_override_rate": core_kpis.get("override_rate", 0),
                "confidence_threshold": 90,  # Standard threshold for auto-posting
                "high_confidence_transactions": core_kpis.get("percent_auto_posted", 0)
            },
            "processing_metrics": {
                "document_processing_time_avg": core_kpis.get("doc_processing_time", 0),
                "ocr_review_time_avg": core_kpis.get("ocr_review_time", 0),
                "csv_error_rate": core_kpis.get("csv_error_rate", 0),
                "data_quality_score": _calculate_data_quality_score(qbo_data)
            },
            "workflow_metrics": {
                "task_completion_rate": core_kpis.get("task_completion_rate", 0),
                "workflow_efficiency": 100 - core_kpis.get("override_rate", 0),
                "exception_handling_rate": core_kpis.get("override_rate", 0)
            },
            "recommendations": _generate_operational_recommendations(core_kpis),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get operational KPIs: {str(e)}"
        )

@router.get("/cash-flow")
async def get_cash_flow_kpis(
    services: Dict = Depends(get_services)
):
    """
    Get cash flow KPIs focused on runway management and financial health.
    
    Shows runway calculations, burn rates, and cash flow projections.
    """
    try:
        smart_sync = services["smart_sync"]
        reserve_service = services["reserve_service"]
        
        # Get comprehensive runway calculation
        runway_calc = reserve_service.calculate_runway_with_reserves(include_projections=True)
        
        # Get QBO data for cash flow analysis
        qbo_data = smart_sync.get_qbo_data_for_digest()
        
        # Calculate cash flow velocity metrics
        bills_data = qbo_data.get("bills", [])
        invoices_data = qbo_data.get("invoices", [])
        
        pending_ap = sum(float(b.get("TotalAmt", 0)) for b in bills_data if float(b.get("Balance", 0)) > 0)
        pending_ar = sum(float(i.get("Balance", 0)) for i in invoices_data if float(i.get("Balance", 0)) > 0)
        
        return {
            "runway_metrics": {
                "current_runway_days": runway_calc.get("runway_days", 0),
                "runway_with_reserves": runway_calc.get("runway_with_reserves", 0),
                "daily_burn_rate": runway_calc.get("daily_burn", 0),
                "monthly_burn_rate": runway_calc.get("daily_burn", 0) * 30,
                "runway_trend": _calculate_runway_trend(runway_calc)
            },
            "cash_position": {
                "available_cash": runway_calc.get("available_cash", 0),
                "reserved_cash": runway_calc.get("total_reserves", 0),
                "total_cash": runway_calc.get("total_cash", 0),
                "cash_utilization": runway_calc.get("cash_utilization_percent", 0)
            },
            "payables_metrics": {
                "pending_ap": pending_ap,
                "ap_runway_impact": pending_ap / runway_calc.get("daily_burn", 1) if runway_calc.get("daily_burn", 0) > 0 else 0,
                "overdue_ap": sum(float(b.get("TotalAmt", 0)) for b in bills_data if _is_bill_overdue(b))
            },
            "receivables_metrics": {
                "pending_ar": pending_ar,
                "ar_runway_potential": pending_ar / runway_calc.get("daily_burn", 1) if runway_calc.get("daily_burn", 0) > 0 else 0,
                "overdue_ar": sum(float(i.get("Balance", 0)) for i in invoices_data if _is_invoice_overdue(i))
            },
            "health_indicators": {
                "cash_flow_health": _assess_cash_flow_health(runway_calc),
                "burn_rate_stability": "stable",  # TODO: Calculate from historical data
                "collection_efficiency": _calculate_collection_efficiency(invoices_data)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cash flow KPIs: {str(e)}"
        )

@router.get("/trends")
async def get_kpi_trends(
    days: int = 30,
    services: Dict = Depends(get_services)
):
    """
    Get KPI trends over specified time period.
    
    Shows historical performance and trend analysis for key metrics.
    """
    try:
        # TODO: Implement historical KPI tracking
        # For now, return mock trend data structure
        
        return {
            "period": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "trends": {
                "runway_trend": {
                    "current": 90,
                    "trend": "stable",
                    "change_percent": 2.5,
                    "historical_data": []  # TODO: Populate with actual data
                },
                "automation_trend": {
                    "current": 85,
                    "trend": "improving",
                    "change_percent": 5.2,
                    "historical_data": []
                },
                "cash_flow_trend": {
                    "current": "healthy",
                    "trend": "stable",
                    "change_percent": 1.1,
                    "historical_data": []
                }
            },
            "insights": [
                {
                    "type": "improvement",
                    "message": "Automation rate has improved by 5.2% over the last 30 days",
                    "priority": "positive"
                },
                {
                    "type": "stability",
                    "message": "Runway has remained stable with minor fluctuations",
                    "priority": "neutral"
                }
            ],
            "note": "Historical trend tracking will be implemented in future release",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KPI trends: {str(e)}"
        )

# Helper functions
def _is_bill_overdue(bill_data: Dict) -> bool:
    """Check if a bill is overdue."""
    due_date_str = bill_data.get("DueDate")
    if not due_date_str:
        return False
    
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return datetime.utcnow() > due_date and float(bill_data.get("Balance", 0)) > 0
    except:
        return False

def _is_invoice_overdue(invoice_data: Dict) -> bool:
    """Check if an invoice is overdue."""
    due_date_str = invoice_data.get("DueDate")
    if not due_date_str:
        return False
    
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return datetime.utcnow() > due_date and float(invoice_data.get("Balance", 0)) > 0
    except:
        return False

def _calculate_data_quality_score(qbo_data: Dict) -> float:
    """Calculate overall data quality score."""
    # TODO: Implement comprehensive data quality scoring
    return 85.0  # Mock score

def _calculate_sync_health_score(smart_sync: SmartSyncService) -> float:
    """Calculate QBO sync health score."""
    # TODO: Implement sync health scoring based on sync frequency and success rates
    return 92.0  # Mock score

def _calculate_runway_trend(runway_calc: Dict) -> str:
    """Calculate runway trend direction."""
    # TODO: Implement historical runway comparison
    return "stable"  # Mock trend

def _calculate_avg_payment_cycle(bills_data: List[Dict]) -> float:
    """Calculate average payment cycle in days."""
    # TODO: Implement based on actual payment dates
    return 25.5  # Mock average

def _calculate_avg_collection_cycle(invoices_data: List[Dict]) -> float:
    """Calculate average collection cycle in days."""
    # TODO: Implement based on actual collection dates
    return 32.1  # Mock average

def _generate_operational_recommendations(core_kpis: Dict) -> List[Dict]:
    """Generate recommendations based on operational KPIs."""
    recommendations = []
    
    auto_rate = core_kpis.get("percent_auto_posted", 0)
    if auto_rate < 80:
        recommendations.append({
            "type": "improvement",
            "message": f"Auto-posting rate is {auto_rate:.1f}%. Consider reviewing categorization rules to improve automation.",
            "priority": "medium"
        })
    
    override_rate = core_kpis.get("override_rate", 0)
    if override_rate > 20:
        recommendations.append({
            "type": "attention",
            "message": f"Manual override rate is {override_rate:.1f}%. Review common override patterns to improve automation.",
            "priority": "high"
        })
    
    return recommendations

def _assess_cash_flow_health(runway_calc: Dict) -> str:
    """Assess overall cash flow health."""
    runway_days = runway_calc.get("runway_days", 0)
    
    if runway_days > 90:
        return "healthy"
    elif runway_days > 30:
        return "warning"
    else:
        return "critical"

def _calculate_collection_efficiency(invoices_data: List[Dict]) -> float:
    """Calculate collection efficiency percentage."""
    # TODO: Implement based on actual collection performance
    return 78.5  # Mock efficiency score
