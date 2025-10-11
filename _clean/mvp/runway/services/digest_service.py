"""
Digest Service - Weekly Summaries and Insights

This service provides digest functionality for advisors to receive
weekly summaries of data quality and business insights. It consumes
Tray and Console service outputs instead of pulling raw data.
"""

from typing import Dict, Any, List, Optional, Protocol
import logging

logger = logging.getLogger(__name__)

class DigestService:
    """Service for digest functionality."""
    
    def __init__(self, advisor_id: str, business_id: str, realm_id: str, 
                 tray_service, console_service):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.realm_id = realm_id
        self.tray_service = tray_service
        self.console_service = console_service
        
        logger.info(f"Initialized DigestService for advisor {advisor_id}, business {business_id}")
    
    async def get_weekly_digest(self) -> Dict[str, Any]:
        """Get weekly summary of data quality and business insights."""
        # Consume Tray and Console service outputs instead of pulling raw data
        hygiene_summary = await self.tray_service.get_hygiene_summary()
        financial_overview = await self.console_service.get_financial_overview()
        
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "cash_position": financial_overview["cash_position"],
            "total_ap": financial_overview["total_ap"],
            "total_ar": financial_overview["total_ar"],
            "runway_days": financial_overview["runway_days"],
            "data_quality_score": self._calculate_data_quality_score(hygiene_summary),
            "hygiene_flags": self._generate_hygiene_flags(hygiene_summary),
            "recommendations": self._generate_recommendations(hygiene_summary, financial_overview),
            "last_updated": hygiene_summary["last_updated"]
        }
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio health summary across all businesses."""
        digest = await self.get_weekly_digest()
        
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "cash_position": digest["cash_position"],
            "total_ap": digest["total_ap"],
            "total_ar": digest["total_ar"],
            "runway_days": digest["runway_days"],
            "data_quality_score": digest["data_quality_score"],
            "critical_issues": len([flag for flag in digest["hygiene_flags"] if "critical" in flag.lower()]),
            "recommendations": digest["recommendations"],
            "overall_health": self._calculate_overall_health(digest),
            "last_updated": digest["last_updated"]
        }
    
    def _calculate_data_quality_score(self, hygiene_summary: Dict[str, Any]) -> int:
        """Calculate data quality score based on hygiene issues."""
        total_bills = hygiene_summary.get("total_bills", 0)
        urgent_issues = hygiene_summary.get("urgent_issues", 0)
        
        if total_bills == 0:
            return 100
        
        # Score based on percentage of bills without urgent issues
        score = int((total_bills - urgent_issues) / total_bills * 100)
        return max(0, min(100, score))
    
    def _generate_hygiene_flags(self, hygiene_summary: Dict[str, Any]) -> List[str]:
        """Generate hygiene flags based on summary data."""
        flags = []
        
        if hygiene_summary.get("urgent_issues", 0) > 0:
            flags.append("Critical: Bills with missing vendor information")
        
        if hygiene_summary.get("upcoming_issues", 0) > 5:
            flags.append("Warning: High number of bills needing attention")
        
        if hygiene_summary.get("runway_impact", 0) > 30:
            flags.append("Critical: Hygiene issues significantly impact runway")
        
        return flags
    
    def _generate_recommendations(self, hygiene_summary: Dict[str, Any], financial_overview: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on hygiene and financial data."""
        recommendations = []
        
        if hygiene_summary.get("urgent_issues", 0) > 0:
            recommendations.append("Fix urgent hygiene issues to improve data quality")
        
        if financial_overview.get("runway_days", 0) < 30:
            recommendations.append("Focus on collections to improve cash position")
        
        if financial_overview.get("bills_due_this_week", 0) > 10:
            recommendations.append("Schedule payment review for upcoming bills")
        
        return recommendations
    
    def _calculate_overall_health(self, digest: Dict[str, Any]) -> str:
        """Calculate overall portfolio health."""
        data_quality_score = digest.get("data_quality_score", 0)
        runway_days = digest.get("runway_days", 0)
        critical_issues = len([flag for flag in digest.get("hygiene_flags", []) if "critical" in flag.lower()])
        
        if data_quality_score < 70 or runway_days < 30 or critical_issues > 0:
            return "needs_attention"
        elif data_quality_score < 85 or runway_days < 90:
            return "monitor"
        else:
            return "healthy"
