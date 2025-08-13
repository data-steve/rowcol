from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.business_entity import BusinessEntity as BusinessEntityModel
from schemas.business_entity import BusinessEntity
from database import get_db

router = APIRouter(prefix="/api", tags=["BusinessEntities"])

@router.post("/business_entities", response_model=BusinessEntity)
async def create_business_entity(entity: BusinessEntity, db: Session = Depends(get_db)):
    db_entity = BusinessEntityModel(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.get("/business_entities/{entity_id}", response_model=BusinessEntity)
async def get_business_entity(entity_id: int, firm_id: str, db: Session = Depends(get_db)):
    entity = db.query(BusinessEntityModel).filter(BusinessEntityModel.entity_id == entity_id, BusinessEntityModel.firm_id == firm_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Business entity not found")
    return entity