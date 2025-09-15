from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Balance(Base, TimestampMixin):
    __tablename__ = "balances"
    balance_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False, index=True)
    qbo_account_id = Column(String(50), nullable=False, index=True)
    current_balance = Column(Float, nullable=False)
    available_balance = Column(Float, nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    account_type = Column(String(50), nullable=False)  # checking, savings, credit
    business = relationship("Business")
