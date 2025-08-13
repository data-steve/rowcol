from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Rule(Base, TimestampMixin, TenantMixin):
    __tablename__ = "rules"
    rule_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    priority = Column(Integer, nullable=False)
    match_type = Column(String, nullable=False)  # exact, regex, contains, amount, transfer
    pattern = Column(String, nullable=False)
    output = Column(JSON, nullable=False)  # {account, class, memo, confidence}
    scope = Column(String, default="global")  # global, client
    
    client = relationship("Client")