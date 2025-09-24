from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Notification(Base, TimestampMixin):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    recipient_role = Column(String(50), default="owner")
    event_type = Column(String(50))
    content = Column(JSON)
    sent_at = Column(DateTime, nullable=True)
    business = relationship("Business", back_populates="notifications")
    user = relationship("User")
