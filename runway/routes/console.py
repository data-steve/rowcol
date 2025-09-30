"""
Decision Console API Routes

Provides endpoints for the Decision Console experience including:
- Console data retrieval
- Decision management
- Decision impact analysis
- Decision queue operations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from infra.database.session import get_db
from infra.auth.auth import get_current_business_id
from runway.services.2_experiences.console import DecisionConsoleService

router = APIRouter(prefix="/console", tags=["decision-console"])

def get_console_service(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
) -> DecisionConsoleService:
    """Get console service with business context."""
    return DecisionConsoleService(db, business_id)

@router.get("/data")
async def get_console_data(
    console_service: DecisionConsoleService = Depends(get_console_service)
) -> Dict[str, Any]:
    """
    Get all data needed for the Decision Console experience.
    
    Returns:
        Dictionary containing bills, invoices, balances, and decision queue
    """
    try:
        return await console_service.get_console_data(console_service.business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting console data: {str(e)}")

@router.post("/decisions")
async def add_decision(
    decision: Dict[str, Any],
    console_service: DecisionConsoleService = Depends(get_console_service)
) -> Dict[str, Any]:
    """
    Add a decision to the decision queue.
    
    Args:
        decision: The decision data to store
        
    Returns:
        Updated console data with the new decision added
    """
    try:
        return await console_service.add_decision(console_service.business_id, decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding decision: {str(e)}")

@router.post("/decisions/finalize")
async def finalize_decisions(
    console_service: DecisionConsoleService = Depends(get_console_service)
) -> Dict[str, Any]:
    """
    Process all decisions in the queue and clear it.
    
    Returns:
        Results of processing the decisions
    """
    try:
        return await console_service.finalize_decisions(console_service.business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finalizing decisions: {str(e)}")

@router.get("/decisions/queue")
async def get_decision_queue(
    console_service: DecisionConsoleService = Depends(get_console_service)
) -> List[Dict[str, Any]]:
    """
    Get the current decision queue for a business.
    
    Returns:
        List of pending decisions
    """
    try:
        return await console_service.get_decision_queue(console_service.business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting decision queue: {str(e)}")

@router.delete("/decisions/queue")
async def clear_decision_queue(
    console_service: DecisionConsoleService = Depends(get_console_service)
) -> Dict[str, Any]:
    """
    Clear the decision queue for a business.
    
    Returns:
        Confirmation of queue clearing
    """
    try:
        return await console_service.clear_decision_queue(console_service.business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing decision queue: {str(e)}")

@router.post("/decisions/analyze")
async def analyze_decision_impact(
    decision: Dict[str, Any],
    console_service: DecisionConsoleService = Depends(get_console_service)
) -> Dict[str, Any]:
    """
    Analyze the impact of a decision using the new calculators.
    
    Args:
        decision: The decision to analyze
        
    Returns:
        Analysis results including impact and insights
    """
    try:
        return await console_service.analyze_decision_impact(console_service.business_id, decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing decision impact: {str(e)}")
