from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.engagement_entities import EngagementEntities as EngagementEntitiesModel
from schemas.engagement_entities import EngagementEntities
from database import get_db

router = APIRouter(prefix="/api", tags=["EngagementEntities"])

@router.post("/engagement_entities", response_model=EngagementEntities)
async def create_engagement_entity(engagement_entity: EngagementEntities, db: Session = Depends(get_db)):
    db_engagement_entity = EngagementEntitiesModel(**engagement_entity.dict())
    db.add(db_engagement_entity)
    db.commit()
    db.refresh(db_engagement_entity)
    return db_engagement_entity

@router.get("/engagement_entities/{id}", response_model=EngagementEntities)
async def get_engagement_entity(id: str, db: Session = Depends(get_db)):
    engagement_entity = db.query(EngagementEntitiesModel).filter(EngagementEntitiesModel.id == id).first()
    if not engagement_entity:
        raise HTTPException(status_code=404, detail="Engagement entity not found")
    return engagement_entity