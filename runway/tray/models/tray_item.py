from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class TrayItem(Base, TimestampMixin):
    __tablename__ = "tray_item"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firm.id"))
    type = Column(String)
    qbo_id = Column(String)
    status = Column(String, default="pending")
    priority = Column(String, default="medium")
    due_date = Column(DateTime)
    allowed_roles = Column(String, default="owner")
    firm = relationship("Firm", back_populates="tray_items")
