from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.engagement import EngagementService
from schemas.engagement import Engagement, EngagementCreate
from database import get_db

router = APIRouter(prefix="/api", tags=["Engagements"])

@router.get("/engagements", response_model=list[Engagement])
async def list_engagements(firm_id: str = None, db: Session = Depends(get_db)):
    service = EngagementService(db)
    return service.list_engagements(firm_id)

@router.post("/engagements", response_model=Engagement)
async def create_engagement(engagement: EngagementCreate, db: Session = Depends(get_db)):
    service = EngagementService(db)
    return service.create_engagement(engagement)

@router.get("/engagements/{engagement_id}", response_model=Engagement)
async def get_engagement(engagement_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = EngagementService(db)
    try:
        return service.get_engagement(engagement_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/engagements/{engagement_id}/sign", response_model=Engagement)
async def sign_engagement(engagement_id: int, firm_id: str, signature_data: dict, db: Session = Depends(get_db)):
    service = EngagementService(db)
    try:
        return service.sign_engagement(engagement_id, firm_id, signature_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/engagements/{engagement_id}/qbo-sync", response_model=Engagement)
async def qbo_sync(engagement_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = EngagementService(db)
    try:
        return service.sync_qbo(engagement_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))