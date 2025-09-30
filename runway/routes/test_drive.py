"""
Test Drive API Routes

Provides endpoints for proof-of-value demonstrations including:
- Runway Replay: Historical 4-week analysis
- Hygiene Score: Data quality assessment
- QBO Sandbox Test Drive: Demo with sample data
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from infra.database.session import get_db
from runway.services.2_experiences.test_drive import TestDriveService, DemoTestDriveService

router = APIRouter(prefix="/test-drive", tags=["test-drive"])

@router.get("/{business_id}/test-drive")
async def get_test_drive(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get test drive data showing historical insights.
    
    Returns a 4-week retrospective analysis of what Oodaloo would have 
    recommended based on the business's QBO data.
    """
    service = TestDriveService(db)
    return await service.get_test_drive_experience(business_id)

@router.get("/{business_id}/test-drive/enhanced")
async def get_enhanced_test_drive(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get enhanced test drive data with insights and value proposition analysis.
    
    Returns enhanced analysis with insights, value proposition, and demo metrics.
    """
    service = TestDriveService(db)
    return await service.get_enhanced_test_drive_experience(business_id)

@router.get("/{business_id}/hygiene-score")
def get_hygiene_score(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get data hygiene score showing QBO data quality issues.
    
    Demonstrates value by showing how fixing data quality improves 
    runway accuracy.
    """
    service = DemoTestDriveService(db)
    return service.generate_hygiene_score(business_id)

@router.get("/demo/{industry}")
def get_qbo_sandbox_demo(industry: str = "software_agency", db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get QBO sandbox test drive demo for a specific industry.
    
    Uses realistic sample data from QBO sandbox to demonstrate
    Oodaloo's capabilities without requiring real business data.
    """
    service = DemoTestDriveService(db)
    return service.generate_qbo_sandbox_test_drive(industry)
