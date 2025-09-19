from sqlalchemy import Column, Integer, String, Boolean
from domains.core.models.base import Base, TimestampMixin

class COATemplate(Base, TimestampMixin):
    __tablename__ = "coa_templates"
    
    template_id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    parent_account = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
