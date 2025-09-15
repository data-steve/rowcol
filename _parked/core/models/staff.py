from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Staff(Base, TimestampMixin, TenantMixin):
    __tablename__ = "staff"
    staff_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    role = Column(String, nullable=False)  # bookkeeper, manager
    training_level = Column(String, default="junior")  # junior, senior
    user = relationship("User", back_populates="staff")