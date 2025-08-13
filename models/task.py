from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Task(Base, TimestampMixin, TenantMixin):
    __tablename__ = "tasks" 
    task_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    engagement_id = Column(Integer, ForeignKey("engagements.engagement_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.service_id"), nullable=False)
    type = Column(String, nullable=False)  # pbc_collection, ocr_review, tagging, je_approval
    status = Column(String, default="pending")
    assigned_staff_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String, default="medium")  # low, medium, high
    completion_level = Column(Float, default=0.0)
    micro_tasks = Column(JSON, nullable=True)
    blockers = Column(JSON, nullable=True)  # [{task_id, type}]
    priority_score = Column(Float, default=0.5)  # 0.0–1.0
    estimated_hours = Column(Float, default=1.0)
    automation_eligibility = Column(String, default="manual")  # manual, partial, full
    validation_errors = Column(JSON, nullable=True)  # [{error_code, description}]
    engagement = relationship("Engagement")
    service = relationship("Service")
    staff = relationship("Staff")