from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import uuid

class EngagementEntities(Base, TimestampMixin):
    __tablename__ = "engagement_entities"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    engagement_id = Column(Integer, ForeignKey("engagements.engagement_id"), nullable=False)
    business_entity_id = Column(Integer, ForeignKey("business_entities.id"), nullable=False)
    
    engagement = relationship("Engagement", back_populates="engagement_entities")
    business_entity = relationship("BusinessEntity", back_populates="engagement_entities")
    __table_args__ = (
        UniqueConstraint("engagement_id", "business_entity_id", name="uq_engagement_entity"),
    )