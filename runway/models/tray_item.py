from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class TrayItem(Base, TimestampMixin):
    __tablename__ = "tray_item"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    type = Column(String(50))
    qbo_id = Column(String(50))
    status = Column(String(50), default="pending")
    priority = Column(String(50), default="medium")
    due_date = Column(DateTime)
    allowed_roles = Column(String(50), default="owner")
    business = relationship("Business", back_populates="tray_items")
