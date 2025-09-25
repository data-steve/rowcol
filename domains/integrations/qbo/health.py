"""
QBO Health Monitoring Service

Production monitoring system for QBO integration health across all clients.
Provides real-time status, alerts, and automated recovery actions.

Features:
- Real-time connection health dashboard
- Automated alerts for connection issues  
- Proactive token refresh scheduling
- Client-facing status pages
- Integration health metrics and SLAs
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.integration import Integration
from domains.integrations.qbo.client import QBOAPIClient

class QBOConnectionStatus(Enum):
    """QBO connection health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    DISCONNECTED = "disconnected"

logger = logging.getLogger(__name__)


@dataclass
class QBOHealthSummary:
    """Overall QBO health summary."""
    total_businesses: int
    healthy_connections: int
    degraded_connections: int
    failing_connections: int
    disconnected_connections: int
    overall_health_percentage: float
    avg_response_time_ms: Optional[float]
    last_updated: datetime


@dataclass
class QBOAlert:
    """QBO health alert."""
    business_id: str
    business_name: str
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    created_at: datetime
    resolved_at: Optional[datetime]


class QBOHealthMonitor:
    """
    Monitors QBO integration health across all clients.
    
    Responsibilities:
    - Continuous health monitoring
    - Alert generation and management
    - Health metrics and reporting
    - Automated recovery actions
    - Client status communication
    """
    
    def __init__(self, db: Session):
        self.db = db
        # TODO: Replace with QBOAuthService when health monitoring is reimplemented
        # self.connection_manager = get_qbo_connection_manager(db)
        self.active_alerts: Dict[str, List[QBOAlert]] = {}
        self.health_history: List[QBOHealthSummary] = []
        self.monitoring_active = False
        
        # Monitoring configuration
        self.health_check_interval = 300  # 5 minutes
        self.alert_thresholds = {
            "consecutive_failures_warning": 2,
            "consecutive_failures_critical": 5,
            "response_time_warning_ms": 5000,  # 5 seconds
            "response_time_critical_ms": 10000,  # 10 seconds
            "token_expiry_warning_hours": 2,
        }
        
        logger.info("QBOHealthMonitor initialized")
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.monitoring_active:
            logger.warning("Health monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting QBO health monitoring")
        
        while self.monitoring_active:
            try:
                await self._perform_health_sweep()
                await self._generate_alerts()
                await self._update_health_summary()
                await self._perform_automated_recovery()
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring_active = False
        logger.info("QBO health monitoring stopped")
    
    async def get_health_summary(self) -> QBOHealthSummary:
        """Get current health summary."""
        all_health = self.connection_manager.get_all_connection_health()
        
        total = len(all_health)
        healthy = sum(1 for h in all_health.values() if h.status == QBOConnectionStatus.HEALTHY)
        degraded = sum(1 for h in all_health.values() if h.status == QBOConnectionStatus.DEGRADED)
        failing = sum(1 for h in all_health.values() if h.status == QBOConnectionStatus.FAILING)
        disconnected = sum(1 for h in all_health.values() if h.status == QBOConnectionStatus.DISCONNECTED)
        
        # Calculate overall health percentage
        if total > 0:
            health_percentage = (healthy + (degraded * 0.5)) / total * 100
        else:
            health_percentage = 100.0
        
        # Calculate average response time
        response_times = [h.api_response_time_ms for h in all_health.values() if h.api_response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        return QBOHealthSummary(
            total_businesses=total,
            healthy_connections=healthy,
            degraded_connections=degraded,
            failing_connections=failing,
            disconnected_connections=disconnected,
            overall_health_percentage=round(health_percentage, 1),
            avg_response_time_ms=round(avg_response_time, 1) if avg_response_time else None,
            last_updated=datetime.now()
        )
    
    async def get_business_health_details(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed health information for a specific business."""
        health = self.connection_manager.get_connection_health(business_id)
        if not health:
            return None
        
        # Get business name
        business = self.db.query(Business).filter(Business.business_id == business_id).first()
        business_name = business.name if business else "Unknown"
        
        # Get active alerts
        alerts = self.active_alerts.get(business_id, [])
        
        # Get integration details
        integration = self.db.query(Integration).filter(
            Integration.business_id == business_id,
            Integration.platform == "qbo"
        ).first()
        
        return {
            "business_id": business_id,
            "business_name": business_name,
            "health": asdict(health),
            "active_alerts": [asdict(alert) for alert in alerts],
            "integration_details": {
                "realm_id": integration.realm_id if integration else None,
                "connected_at": integration.connected_at.isoformat() if integration and integration.connected_at else None,
                "status": integration.status if integration else "unknown"
            }
        }
    
    async def get_all_business_health(self) -> List[Dict[str, Any]]:
        """Get health details for all businesses."""
        all_health = self.connection_manager.get_all_connection_health()
        results = []
        
        for business_id in all_health.keys():
            details = await self.get_business_health_details(business_id)
            if details:
                results.append(details)
        
        return results
    
    async def force_health_check(self, business_id: str) -> bool:
        """Force an immediate health check for a specific business."""
        try:
            return await self.connection_manager.ensure_healthy_connection(business_id)
        except Exception as e:
            logger.error(f"Forced health check failed for business {business_id}: {e}")
            return False
    
    async def _perform_health_sweep(self):
        """Perform health checks for all businesses."""
        # Get all businesses with QBO integrations
        businesses = self.db.query(Business).join(Integration).filter(
            Integration.platform == "qbo"
        ).all()
        
        logger.debug(f"Performing health sweep for {len(businesses)} businesses")
        
        # Check health for each business
        tasks = []
        for business in businesses:
            task = self.connection_manager.ensure_healthy_connection(business.business_id)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _generate_alerts(self):
        """Generate alerts based on current health status."""
        all_health = self.connection_manager.get_all_connection_health()
        
        for business_id, health in all_health.items():
            # Get business name
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            business_name = business.name if business else "Unknown"
            
            # Check for alert conditions
            new_alerts = []
            
            # Connection failure alerts
            if health.consecutive_failures >= self.alert_thresholds["consecutive_failures_critical"]:
                new_alerts.append(QBOAlert(
                    business_id=business_id,
                    business_name=business_name,
                    alert_type="connection_failure",
                    severity="critical",
                    message=f"QBO connection failing: {health.consecutive_failures} consecutive failures",
                    created_at=datetime.now(),
                    resolved_at=None
                ))
            elif health.consecutive_failures >= self.alert_thresholds["consecutive_failures_warning"]:
                new_alerts.append(QBOAlert(
                    business_id=business_id,
                    business_name=business_name,
                    alert_type="connection_degraded",
                    severity="medium",
                    message=f"QBO connection degraded: {health.consecutive_failures} recent failures",
                    created_at=datetime.now(),
                    resolved_at=None
                ))
            
            # Response time alerts
            if health.api_response_time_ms:
                if health.api_response_time_ms >= self.alert_thresholds["response_time_critical_ms"]:
                    new_alerts.append(QBOAlert(
                        business_id=business_id,
                        business_name=business_name,
                        alert_type="slow_response",
                        severity="high",
                        message=f"QBO API very slow: {health.api_response_time_ms:.0f}ms response time",
                        created_at=datetime.now(),
                        resolved_at=None
                    ))
                elif health.api_response_time_ms >= self.alert_thresholds["response_time_warning_ms"]:
                    new_alerts.append(QBOAlert(
                        business_id=business_id,
                        business_name=business_name,
                        alert_type="slow_response",
                        severity="medium",
                        message=f"QBO API slow: {health.api_response_time_ms:.0f}ms response time",
                        created_at=datetime.now(),
                        resolved_at=None
                    ))
            
            # Token expiry alerts
            if health.token_expires_at:
                time_to_expiry = health.token_expires_at - datetime.now()
                if time_to_expiry <= timedelta(hours=self.alert_thresholds["token_expiry_warning_hours"]):
                    new_alerts.append(QBOAlert(
                        business_id=business_id,
                        business_name=business_name,
                        alert_type="token_expiring",
                        severity="medium",
                        message=f"QBO token expires in {time_to_expiry}",
                        created_at=datetime.now(),
                        resolved_at=None
                    ))
            
            # Update active alerts
            if new_alerts:
                if business_id not in self.active_alerts:
                    self.active_alerts[business_id] = []
                
                # Add new alerts (avoid duplicates)
                existing_types = {alert.alert_type for alert in self.active_alerts[business_id]}
                for alert in new_alerts:
                    if alert.alert_type not in existing_types:
                        self.active_alerts[business_id].append(alert)
                        logger.warning(f"QBO Alert: {alert.message} (Business: {business_name})")
            
            # Resolve alerts if health improved
            if business_id in self.active_alerts and health.status == QBOConnectionStatus.HEALTHY:
                for alert in self.active_alerts[business_id]:
                    if not alert.resolved_at:
                        alert.resolved_at = datetime.now()
                        logger.info(f"QBO Alert Resolved: {alert.message} (Business: {business_name})")
    
    async def _update_health_summary(self):
        """Update health summary history."""
        summary = await self.get_health_summary()
        self.health_history.append(summary)
        
        # Keep only last 24 hours of history (5-minute intervals = 288 entries)
        if len(self.health_history) > 288:
            self.health_history = self.health_history[-288:]
    
    async def _perform_automated_recovery(self):
        """Perform automated recovery actions where possible."""
        all_health = self.connection_manager.get_all_connection_health()
        
        for business_id, health in all_health.items():
            # Auto-refresh tokens that are expiring soon
            if health.token_expires_at:
                time_to_expiry = health.token_expires_at - datetime.now()
                if time_to_expiry <= timedelta(minutes=30):  # 30 minutes before expiry
                    try:
                        success = await self.connection_manager._refresh_token(business_id)
                        if success:
                            logger.info(f"Auto-refreshed token for business {business_id}")
                    except Exception as e:
                        logger.error(f"Auto token refresh failed for business {business_id}: {e}")
    
    def get_health_metrics_for_dashboard(self) -> Dict[str, Any]:
        """Get health metrics formatted for dashboard display."""
        if not self.health_history:
            return {"error": "No health data available"}
        
        latest_summary = self.health_history[-1]
        
        # Calculate trends (compare with 1 hour ago)
        hour_ago_summaries = [s for s in self.health_history if s.last_updated >= datetime.now() - timedelta(hours=1)]
        trend_data = {
            "health_percentage_trend": [],
            "response_time_trend": [],
            "timestamps": []
        }
        
        for summary in hour_ago_summaries[-12:]:  # Last 12 data points (1 hour)
            trend_data["health_percentage_trend"].append(summary.overall_health_percentage)
            trend_data["response_time_trend"].append(summary.avg_response_time_ms)
            trend_data["timestamps"].append(summary.last_updated.isoformat())
        
        # Count active alerts by severity
        alert_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alerts in self.active_alerts.values():
            for alert in alerts:
                if not alert.resolved_at:
                    alert_counts[alert.severity] += 1
        
        return {
            "summary": asdict(latest_summary),
            "trends": trend_data,
            "active_alerts": alert_counts,
            "status_distribution": {
                "healthy": latest_summary.healthy_connections,
                "degraded": latest_summary.degraded_connections,
                "failing": latest_summary.failing_connections,
                "disconnected": latest_summary.disconnected_connections
            }
        }


# Global health monitor instance
_health_monitor: Optional[QBOHealthMonitor] = None


def get_qbo_health_monitor(db: Session) -> QBOHealthMonitor:
    """Get or create the global QBO health monitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = QBOHealthMonitor(db)
    return _health_monitor


async def start_qbo_health_monitoring(db: Session):
    """Start the QBO health monitoring service."""
    monitor = get_qbo_health_monitor(db)
    await monitor.start_monitoring()


if __name__ == "__main__":
    # Test the health monitor
    from db.session import SessionLocal
    
    async def test_health_monitor():
        db = SessionLocal()
        monitor = QBOHealthMonitor(db)
        
        # Get health summary
        summary = await monitor.get_health_summary()
        print(f"Health Summary: {summary}")
        
        # Get dashboard metrics
        metrics = monitor.get_health_metrics_for_dashboard()
        print(f"Dashboard Metrics: {json.dumps(metrics, indent=2, default=str)}")
    
    asyncio.run(test_health_monitor())
