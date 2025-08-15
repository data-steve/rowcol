from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class TaskBase(BaseModel):
    firm_id: str
    engagement_id: int
    client_id: int
    service_id: int
    type: str
    status: str
    assigned_staff_id: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: str
    completion_level: float
    micro_tasks: Optional[List[str]] = None
    blockers: Optional[List[Dict]] = None
    priority_score: float
    estimated_hours: float
    automation_eligibility: str
    validation_errors: Optional[List[Dict]] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    task_id: int

    class Config:
        from_attributes = True

class TaskAssignment(BaseModel):
    task_id: int
    assigned_staff_id: int