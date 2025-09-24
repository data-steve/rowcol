from sqlalchemy import Column, Integer, String, Text
from domains.core.models.base import Base, TimestampMixin

class VendorCategory(Base, TimestampMixin):
    __tablename__ = "vendor_categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    default_gl_account = Column(String(100), nullable=True)
    risk_level = Column(String(50), default="low")
