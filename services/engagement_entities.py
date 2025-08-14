from sqlalchemy.orm import Session
from models.engagement_entities import EngagementEntities as EngagementEntitiesModel
from schemas.engagement_entities import EngagementEntities
from typing import List

class EngagementEntitiesService:
    def __init__(self, db: Session):
        self.db = db

    def create_engagement_entities(self, entities: EngagementEntities) -> EngagementEntities:
        """Create new engagement entities."""
        db_entities = EngagementEntitiesModel(**entities.dict())
        self.db.add(db_entities)
        self.db.commit()
        self.db.refresh(db_entities)
        return db_entities

    def get_engagement_entities(self, id: int, firm_id: str) -> EngagementEntities:
        """Get engagement entities by ID with firm_id filtering."""
        entities = self.db.query(EngagementEntitiesModel).filter(
            EngagementEntitiesModel.id == id,
            EngagementEntitiesModel.firm_id == firm_id
        ).first()
        if not entities:
            raise ValueError("Engagement entities not found")
        return entities

    def list_engagement_entities(self, firm_id: str) -> List[EngagementEntities]:
        """List all engagement entities for a firm."""
        entities = self.db.query(EngagementEntitiesModel).filter(
            EngagementEntitiesModel.firm_id == firm_id
        ).all()
        return entities
