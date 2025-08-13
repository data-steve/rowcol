from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from .base import Base, TimestampMixin, TenantMixin

class Service(Base, TimestampMixin, TenantMixin):
    __tablename__ = "services"
    service_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    complexity_score = Column(Float, default=1.0)  # 1.0–5.0
    task_sequence = Column(JSON, nullable=False)  # [{step_type, micro_tasks, estimated_hours}]
    tier = Column(String, default="basic")  # basic, pro, enterprise
    automation_score = Column(Float, default=0.0)  # 0.0–1.0
    client_instructions = Column(String, nullable=True)  # Client-facing guidance