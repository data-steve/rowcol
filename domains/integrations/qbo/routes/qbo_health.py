"""
QBO Health Monitoring API Routes

Production API endpoints for monitoring QBO integration health.
Used by admin dashboards, client status pages, and monitoring systems.

Endpoints:
- GET /health/summary - Overall QBO health summary
- GET /health/business/{business_id} - Specific business health
- GET /health/dashboard - Dashboard metrics
- POST /health/check/{business_id} - Force health check
- GET /health/alerts - Active alerts
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import asyncio

from db.session import get_db
from domains.integrations.qbo.qbo_health_monitor import (
    get_qbo_health_monitor,
    QBOHealthSummary,
    QBOAlert
)
from domains.integrations.qbo.qbo_connection_manager import get_qbo_connection_manager
from runway.auth.middleware.auth import require_auth

router = APIRouter(prefix="/integrations/qbo/health", tags=["QBO Health"])


@router.get("/summary")
async def get_health_summary(db: Session = Depends(get_db)) -> QBOHealthSummary:
    """Get overall QBO health summary across all businesses."""
    monitor = get_qbo_health_monitor(db)
    return await monitor.get_health_summary()


@router.get("/business/{business_id}")
async def get_business_health(
    business_id: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed health information for a specific business."""
    monitor = get_qbo_health_monitor(db)
    health_details = await monitor.get_business_health_details(business_id)
    
    if not health_details:
        raise HTTPException(
            status_code=404, 
            detail=f"No QBO integration found for business {business_id}"
        )
    
    return health_details


@router.get("/businesses")
async def get_all_business_health(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get health information for all businesses with QBO integrations."""
    monitor = get_qbo_health_monitor(db)
    return await monitor.get_all_business_health()


@router.get("/dashboard")
async def get_dashboard_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get health metrics formatted for dashboard display."""
    monitor = get_qbo_health_monitor(db)
    return monitor.get_health_metrics_for_dashboard()


@router.post("/check/{business_id}")
async def force_health_check(
    business_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Force an immediate health check for a specific business."""
    monitor = get_qbo_health_monitor(db)
    
    # Run health check in background
    async def run_health_check():
        try:
            is_healthy = await monitor.force_health_check(business_id)
            return is_healthy
        except Exception:
            return False
    
    # Start the health check
    task = asyncio.create_task(run_health_check())
    
    return {
        "message": f"Health check initiated for business {business_id}",
        "business_id": business_id,
        "check_started_at": "now"
    }


@router.get("/alerts")
async def get_active_alerts(
    severity: Optional[str] = None,
    business_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get active QBO health alerts with optional filtering."""
    monitor = get_qbo_health_monitor(db)
    
    all_alerts = []
    for bid, alerts in monitor.active_alerts.items():
        if business_id and bid != business_id:
            continue
            
        for alert in alerts:
            if alert.resolved_at:  # Skip resolved alerts
                continue
                
            if severity and alert.severity != severity:
                continue
            
            all_alerts.append({
                "business_id": alert.business_id,
                "business_name": alert.business_name,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
                "age_minutes": int((monitor.health_history[-1].last_updated - alert.created_at).total_seconds() / 60) if monitor.health_history else 0
            })
    
    # Sort by severity and creation time
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_alerts.sort(key=lambda x: (severity_order.get(x["severity"], 4), x["created_at"]))
    
    return all_alerts


@router.get("/status-page")
async def get_status_page_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get data for client-facing status page."""
    monitor = get_qbo_health_monitor(db)
    summary = await monitor.get_health_summary()
    
    # Determine overall status
    if summary.overall_health_percentage >= 95:
        overall_status = "operational"
        status_message = "All systems operational"
    elif summary.overall_health_percentage >= 85:
        overall_status = "degraded"
        status_message = "Some systems experiencing issues"
    else:
        overall_status = "outage"
        status_message = "Major service disruption"
    
    # Get recent incidents (unresolved alerts)
    recent_alerts = []
    for alerts in monitor.active_alerts.values():
        for alert in alerts:
            if not alert.resolved_at and alert.severity in ["high", "critical"]:
                recent_alerts.append({
                    "type": alert.alert_type,
                    "message": alert.message,
                    "severity": alert.severity,
                    "started_at": alert.created_at.isoformat()
                })
    
    return {
        "overall_status": overall_status,
        "status_message": status_message,
        "health_percentage": summary.overall_health_percentage,
        "total_businesses": summary.total_businesses,
        "services": {
            "qbo_integration": {
                "status": overall_status,
                "uptime_percentage": summary.overall_health_percentage,
                "response_time_ms": summary.avg_response_time_ms,
                "last_updated": summary.last_updated.isoformat()
            }
        },
        "recent_incidents": recent_alerts[:5],  # Last 5 incidents
        "last_updated": summary.last_updated.isoformat()
    }


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(db: Session = Depends(get_db)) -> str:
    """Get QBO health metrics in Prometheus format for monitoring systems."""
    monitor = get_qbo_health_monitor(db)
    summary = await monitor.get_health_summary()
    
    metrics = []
    
    # Health summary metrics
    metrics.append(f"qbo_health_percentage {summary.overall_health_percentage}")
    metrics.append(f"qbo_total_businesses {summary.total_businesses}")
    metrics.append(f"qbo_healthy_connections {summary.healthy_connections}")
    metrics.append(f"qbo_degraded_connections {summary.degraded_connections}")
    metrics.append(f"qbo_failing_connections {summary.failing_connections}")
    metrics.append(f"qbo_disconnected_connections {summary.disconnected_connections}")
    
    if summary.avg_response_time_ms:
        metrics.append(f"qbo_avg_response_time_ms {summary.avg_response_time_ms}")
    
    # Alert counts by severity
    alert_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for alerts in monitor.active_alerts.values():
        for alert in alerts:
            if not alert.resolved_at:
                alert_counts[alert.severity] += 1
    
    for severity, count in alert_counts.items():
        metrics.append(f"qbo_active_alerts{{severity=\"{severity}\"}} {count}")
    
    # Per-business health metrics
    all_health = monitor.connection_manager.get_all_connection_health()
    for business_id, health in all_health.items():
        business_label = business_id.replace("-", "_")  # Prometheus-safe label
        
        status_value = {
            "healthy": 1,
            "degraded": 0.5,
            "failing": 0.25,
            "disconnected": 0
        }.get(health.status.value, 0)
        
        metrics.append(f"qbo_business_health{{business_id=\"{business_id}\"}} {status_value}")
        metrics.append(f"qbo_business_failures{{business_id=\"{business_id}\"}} {health.consecutive_failures}")
        
        if health.api_response_time_ms:
            metrics.append(f"qbo_business_response_time_ms{{business_id=\"{business_id}\"}} {health.api_response_time_ms}")
    
    return "\n".join(metrics)


# Admin-only endpoints (require special auth)
@router.post("/admin/start-monitoring")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    # auth: dict = Depends(require_auth)  # Uncomment when auth is ready
) -> Dict[str, Any]:
    """Start QBO health monitoring (admin only)."""
    monitor = get_qbo_health_monitor(db)
    
    if monitor.monitoring_active:
        return {"message": "Monitoring already active", "status": "running"}
    
    # Start monitoring in background
    background_tasks.add_task(monitor.start_monitoring)
    
    return {
        "message": "QBO health monitoring started",
        "status": "starting",
        "check_interval_seconds": monitor.health_check_interval
    }


@router.post("/admin/stop-monitoring")
async def stop_monitoring(
    db: Session = Depends(get_db),
    # auth: dict = Depends(require_auth)  # Uncomment when auth is ready
) -> Dict[str, Any]:
    """Stop QBO health monitoring (admin only)."""
    monitor = get_qbo_health_monitor(db)
    monitor.stop_monitoring()
    
    return {
        "message": "QBO health monitoring stopped",
        "status": "stopped"
    }


@router.get("/admin/connection-details/{business_id}")
async def get_connection_details(
    business_id: str,
    db: Session = Depends(get_db),
    # auth: dict = Depends(require_auth)  # Uncomment when auth is ready
) -> Dict[str, Any]:
    """Get detailed connection information for debugging (admin only)."""
    connection_manager = get_qbo_connection_manager(db)
    
    # Get connection health
    health = connection_manager.get_connection_health(business_id)
    if not health:
        raise HTTPException(
            status_code=404,
            detail=f"No connection health data for business {business_id}"
        )
    
    # Get circuit breaker state
    circuit_breaker = connection_manager.circuit_breakers.get(business_id, {})
    
    return {
        "business_id": business_id,
        "health": {
            "status": health.status.value,
            "consecutive_failures": health.consecutive_failures,
            "last_successful_call": health.last_successful_call.isoformat() if health.last_successful_call else None,
            "last_token_refresh": health.last_token_refresh.isoformat() if health.last_token_refresh else None,
            "token_expires_at": health.token_expires_at.isoformat() if health.token_expires_at else None,
            "api_response_time_ms": health.api_response_time_ms,
            "failing_endpoints": health.failing_endpoints,
            "error_message": health.error_message
        },
        "circuit_breaker": {
            "state": circuit_breaker.get("state", "unknown"),
            "failure_count": circuit_breaker.get("failure_count", 0),
            "last_failure_time": circuit_breaker.get("last_failure_time").isoformat() if circuit_breaker.get("last_failure_time") else None,
            "next_attempt_time": circuit_breaker.get("next_attempt_time").isoformat() if circuit_breaker.get("next_attempt_time") else None
        }
    }
