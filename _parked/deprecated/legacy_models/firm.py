from sqlalchemy import Column, String, JSON, Integer
import uuid
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Firm(Base, TimestampMixin):
    __tablename__ = "firms"
    firm_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    qbo_id = Column(String, nullable=True)
    pricing_tier = Column(String, default="basic")  # basic, pro, enterprise
    doc_volume = Column(Integer, default=0)
    settings = Column(JSON, default=dict)
    
    users = relationship("User", back_populates="firm")
    clients = relationship("Client", back_populates="firm")
    engagements = relationship("Engagement", back_populates="firm")
    integrations = relationship("Integration", back_populates="firm")