from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship 
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class BusinessEntity(Base, TimestampMixin, TenantMixin):
    __tablename__ = "business_entities"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    name = Column(String, nullable=False)
    ein = Column(String(9), nullable=True)
    tax_classification = Column(String, nullable=False)  # individual, partnership, s_corp, c_corp, nonprofit
    state = Column(String(2), nullable=True)
    business = relationship("Business")
    engagement_entities = relationship("EngagementEntities", back_populates="business_entity")