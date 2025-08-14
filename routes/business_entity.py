from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.business_entity import BusinessEntityService
from schemas.business_entity import BusinessEntity
from database import get_db

router = APIRouter(prefix="/api", tags=["BusinessEntities"])

@router.post("/business_entities", response_model=BusinessEntity)
async def create_business_entity(entity: BusinessEntity, db: Session = Depends(get_db)):
    service = BusinessEntityService(db)
    return service.create_business_entity(entity)

@router.get("/business_entities/{entity_id}", response_model=BusinessEntity)
async def get_business_entity(entity_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = BusinessEntityService(db)
    try:
        return service.get_business_entity(entity_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))