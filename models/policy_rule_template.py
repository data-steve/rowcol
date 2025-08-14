from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from .base import Base, TimestampMixin

class PolicyRuleTemplate(Base, TimestampMixin):
    __tablename__ = "policy_rule_templates"
    
    rule_id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(100), nullable=False)
    service_type = Column(String(100), nullable=False)
    conditions = Column(JSON, nullable=False)  # JSON object defining when rule applies
    actions = Column(JSON, nullable=False)     # JSON array of actions to take
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
