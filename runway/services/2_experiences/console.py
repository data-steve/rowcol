"""
Decision Console Experience Service

Provides a "single pane of glass" experience for making context-laden financial
decisions with prioritization. Uses the DecisionConsoleDataOrchestrator for
data management and state handling.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from runway.services.0_data_orchestrators.decision_console_data_orchestrator import DecisionConsoleDataOrchestrator
from runway.services.1_calculators.runway_calculator import RunwayCalculator
from runway.services.1_calculators.impact_calculator import ImpactCalculator
from runway.services.1_calculators.insight_calculator import InsightCalculator
from common.exceptions import BusinessNotFoundError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DecisionConsoleService:
    """Service for Decision Console experience."""
    
    def __init__(self, db: Session, business_id: str):
        self.db = db
        self.business_id = business_id
        
        # Initialize data orchestrator
        self.data_orchestrator = DecisionConsoleDataOrchestrator(db)
        
        # Initialize calculators for decision analysis
        self.runway_calculator = RunwayCalculator(db, business_id)
        self.impact_calculator = ImpactCalculator(db, business_id, validate_business=False)
        self.insight_calculator = InsightCalculator(db, business_id, validate_business=False)
    
    async def get_console_data(self, business_id: str) -> Dict[str, Any]:
        """
        Get all data needed for the Decision Console experience.
        
        Args:
            business_id: The business to get data for
            
        Returns:
            Dictionary containing bills, invoices, balances, and decision queue
        """
        try:
            # Get console data from orchestrator
            console_data = await self.data_orchestrator.get_console_data(business_id)
            
            # Add runway context for decision-making
            runway_context = self.runway_calculator.calculate_current_runway(console_data)
            console_data["runway_context"] = runway_context
            
            logger.info(f"Retrieved console data for business {business_id}")
            return console_data
            
        except Exception as e:
            logger.error(f"Error getting console data for business {business_id}: {e}")
            raise
    
    async def add_decision(self, business_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a decision to the decision queue.
        
        Args:
            business_id: The business the decision is for
            decision: The decision data to store
            
        Returns:
            Updated console data with the new decision added
        """
        try:
            # Add decision using orchestrator
            updated_data = await self.data_orchestrator.add_decision(business_id, decision)
            
            logger.info(f"Added decision for business {business_id}")
            return updated_data
            
        except Exception as e:
            logger.error(f"Error adding decision for business {business_id}: {e}")
            raise
    
    async def finalize_decisions(self, business_id: str) -> Dict[str, Any]:
        """
        Process all decisions in the queue and clear it.
        
        Args:
            business_id: The business to process decisions for
            
        Returns:
            Results of processing the decisions
        """
        try:
            # Finalize decisions using orchestrator
            results = await self.data_orchestrator.finalize_decisions(business_id)
            
            logger.info(f"Finalized decisions for business {business_id}: {results['decisions_processed']} processed")
            return results
            
        except Exception as e:
            logger.error(f"Error finalizing decisions for business {business_id}: {e}")
            raise
    
    async def get_decision_queue(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get the current decision queue for a business.
        
        Args:
            business_id: The business to get the queue for
            
        Returns:
            List of pending decisions
        """
        try:
            console_data = await self.data_orchestrator.get_console_data(business_id)
            return console_data.get("decision_queue", [])
            
        except Exception as e:
            logger.error(f"Error getting decision queue for business {business_id}: {e}")
            return []
    
    async def clear_decision_queue(self, business_id: str) -> Dict[str, Any]:
        """
        Clear the decision queue for a business.
        
        Args:
            business_id: The business to clear the queue for
            
        Returns:
            Confirmation of queue clearing
        """
        try:
            # Clear queue by finalizing with no decisions
            results = await self.data_orchestrator.finalize_decisions(business_id)
            
            logger.info(f"Cleared decision queue for business {business_id}")
            return {
                "status": "success",
                "message": "Decision queue cleared",
                "business_id": business_id
            }
            
        except Exception as e:
            logger.error(f"Error clearing decision queue for business {business_id}: {e}")
            raise
    
    async def analyze_decision_impact(self, business_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of a decision using the new calculators.
        
        Args:
            business_id: The business the decision is for
            decision: The decision to analyze
            
        Returns:
            Analysis results including impact and insights
        """
        try:
            # Get current runway context
            console_data = await self.get_console_data(business_id)
            runway_context = console_data.get("runway_context", {})
            
            # Calculate decision impact
            impact_analysis = self.impact_calculator.calculate_decision_impact(decision, runway_context)
            
            # Generate insights about the decision
            insights = self.insight_calculator.generate_insights({
                "decision": decision,
                "runway_context": runway_context,
                "impact_analysis": impact_analysis
            })
            
            # Generate recommendations
            recommendations = self.insight_calculator.generate_recommendations(insights)
            
            return {
                "decision": decision,
                "impact_analysis": impact_analysis,
                "insights": insights,
                "recommendations": recommendations,
                "runway_context": runway_context
            }
            
        except Exception as e:
            logger.error(f"Error analyzing decision impact for business {business_id}: {e}")
            raise