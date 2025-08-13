from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.engagement import Engagement as EngagementModel
from schemas.engagement import Engagement, EngagementCreate
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Engagements"])

@router.get("/engagements", response_model=list[Engagement])
async def list_engagements(firm_id: str = None, db: Session = Depends(get_db)):
    query = db.query(EngagementModel)
    if firm_id:
        query = query.filter(EngagementModel.firm_id == firm_id)
    engagements = query.all()
    return engagements

@router.post("/engagements", response_model=Engagement)
async def create_engagement(engagement: EngagementCreate, db: Session = Depends(get_db)):
    db_engagement = EngagementModel(**engagement.dict())
    db.add(db_engagement)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.get("/engagements/{engagement_id}", response_model=Engagement)
async def get_engagement(engagement_id: int, firm_id: str, db: Session = Depends(get_db)):
    engagement = db.query(EngagementModel).filter(EngagementModel.engagement_id == engagement_id, EngagementModel.firm_id == firm_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement

@router.post("/engagements/{engagement_id}/sign", response_model=Engagement)
async def sign_engagement(engagement_id: int, firm_id: str, signature_data: dict, db: Session = Depends(get_db)):
    engagement = db.query(EngagementModel).filter(
        EngagementModel.engagement_id == engagement_id,
        EngagementModel.firm_id == firm_id
    ).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    engagement.e_signature = {"signer_id": signature_data.get("signer_id"), "timestamp": datetime.utcnow().isoformat(), "signature_data": signature_data.get("signature_data")}
    engagement.agreed_at = datetime.utcnow()
    db.commit()
    db.refresh(engagement)
    return engagement

@router.post("/engagements/{engagement_id}/qbo-sync", response_model=Engagement)
async def qbo_sync(engagement_id: int, firm_id: str, db: Session = Depends(get_db)):
    engagement = db.query(EngagementModel).filter(EngagementModel.engagement_id == engagement_id, EngagementModel.firm_id == firm_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    engagement.qbo_sync_status = "syncing"
    db.commit()
    db.refresh(engagement)
    # Placeholder for QBO sync logic (to be implemented in Phase 1)
    engagement.qbo_sync_status = "success"
    db.commit()
    db.refresh(engagement)
    return engagement