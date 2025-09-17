from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.services.engagement_entities import EngagementEntitiesService
from domains.core.schemas.engagement_entities import EngagementEntities
from database import get_db

router = APIRouter(prefix="/api", tags=["EngagementEntities"])

@router.post("/engagement_entities", response_model=EngagementEntities)
async def create_engagement_entity(engagement_entity: EngagementEntities, db: Session = Depends(get_db)):
    service = EngagementEntitiesService(db)
    return service.create_engagement_entities(engagement_entity)

@router.get("/engagement_entities/{id}", response_model=EngagementEntities)
async def get_engagement_entity(id: str, firm_id: str, db: Session = Depends(get_db)):
    service = EngagementEntitiesService(db)
    try:
        return service.get_engagement_entities(int(id), firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))