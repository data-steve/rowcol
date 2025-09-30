"""
Business Routes - Core Domain Business Entity API

These routes provide basic CRUD operations for Business entities.
Business management is a core domain primitive that other layers can use.

API Design:
- All routes are under /domains/core/businesses/
- These are internal system APIs, not user-facing runway APIs
- Runway layer should orchestrate these for user workflows
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from infra.database.session import get_db
from domains.core.services.business import BusinessService
from domains.core.schemas.business import (
    BusinessCreate, 
    BusinessUpdate, 
    Business as BusinessSchema
)

router = APIRouter(prefix='/domains/core', tags=['core-business'])

@router.post('/businesses/', response_model=BusinessSchema)
def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    """Create a new business entity."""
    service = BusinessService(db)
    return service.create_business(business)

@router.get('/businesses/{business_id}', response_model=BusinessSchema)
def get_business(business_id: str, db: Session = Depends(get_db)):
    """Get business by ID."""
    service = BusinessService(db)
    business = service.get_business(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.get('/businesses/', response_model=List[BusinessSchema])
def get_all_businesses(db: Session = Depends(get_db)):
    """Get all businesses (admin function)."""
    service = BusinessService(db)
    return service.get_all_businesses()

@router.put('/businesses/{business_id}', response_model=BusinessSchema)
def update_business(
    business_id: str, 
    business_update: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    """Update business profile."""
    service = BusinessService(db)
    business = service.update_business(business_id, business_update)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.delete('/businesses/{business_id}')
def delete_business(business_id: str, db: Session = Depends(get_db)):
    """Delete business (admin function)."""
    service = BusinessService(db)
    success = service.delete_business(business_id)
    if not success:
        raise HTTPException(status_code=404, detail="Business not found")
    return {"message": "Business deleted successfully"}
