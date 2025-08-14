from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from .base import Base, TimestampMixin

class TaskTemplate(Base, TimestampMixin):
    __tablename__ = "task_templates"
    
    template_id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False)
    service_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    estimated_hours = Column(Float, default=1.0)
    priority = Column(String(50), default="medium")
    dependencies = Column(JSON, nullable=True)  # JSON array of dependent task IDs
    micro_tasks = Column(JSON, nullable=True)  # JSON array of micro-tasks
