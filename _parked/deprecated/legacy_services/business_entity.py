from sqlalchemy.orm import Session
from domains.core.models.business_entity import BusinessEntity as BusinessEntityModel
from domains.core.schemas.business_entity import BusinessEntity
from typing import List

class BusinessEntityService:
    def __init__(self, db: Session):
        self.db = db

    def create_business_entity(self, entity: BusinessEntity) -> BusinessEntity:
        """Create a new business entity."""
        db_entity = BusinessEntityModel(**entity.dict())
        self.db.add(db_entity)
        self.db.commit()
        self.db.refresh(db_entity)
        return db_entity

    def get_business_entity(self, entity_id: int, firm_id: str) -> BusinessEntity:
        """Get a business entity by ID with firm_id filtering."""
        entity = self.db.query(BusinessEntityModel).filter(
            BusinessEntityModel.entity_id == entity_id,
            BusinessEntityModel.firm_id == firm_id
        ).first()
        if not entity:
            raise ValueError("Business entity not found")
        return entity

    def list_business_entities(self, firm_id: str) -> List[BusinessEntity]:
        """List all business entities for a firm."""
        entities = self.db.query(BusinessEntityModel).filter(
            BusinessEntityModel.firm_id == firm_id
        ).all()
        return entities
