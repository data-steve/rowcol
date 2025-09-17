from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class User(Base, TimestampMixin, TenantMixin):
    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True, index=True)  # Changed to String for UUID-like IDs
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    role = Column(String, nullable=False)  # owner, admin, staff
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # Added for authentication
    permissions = Column(JSON, nullable=True)
    training_level = Column(String, default="junior")  # junior, senior, manager
    is_active = Column(Boolean, default=True)  # Added for soft delete
    business = relationship("Business", back_populates="users")
    # staff = relationship("Staff", back_populates="user")  # Parked for Phase 0