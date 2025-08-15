from sqlalchemy import Column, Integer, String, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class User(Base, TimestampMixin, TenantMixin):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    role = Column(String, nullable=False)  # admin, staff, client
    email = Column(String, unique=True, nullable=False, index=True)
    permissions = Column(JSON, nullable=True)
    training_level = Column(String, default="junior")  # junior, senior, manager
    firm = relationship("Firm", back_populates="users")
    staff = relationship("Staff", back_populates="user")