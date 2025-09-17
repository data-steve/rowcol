from pydantic import BaseModel

class EngagementEntitiesBase(BaseModel):
    engagement_id: int
    business_entity_id: int

class EngagementEntitiesCreate(EngagementEntitiesBase):
    pass

class EngagementEntities(EngagementEntitiesBase):
    id: str

    class Config:
        from_attributes = True