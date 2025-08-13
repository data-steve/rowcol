from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class EngagementBase(BaseModel):
    firm_id: str
    client_id: int
    service_type: str = "bookkeeping"
    due_date: datetime
    task_ids: Optional[List[int]] = None
    user_input: Optional[Dict] = None
    allowance_overage: float = 0.0

class EngagementCreate(EngagementBase):
    pass

class Engagement(EngagementBase):
    engagement_id: int
    status: str
    agreed_at: Optional[datetime] = None
    health_status: str
    compliance_status: str
    e_signature: Optional[Dict] = None
    qbo_sync_status: str

    class Config:
        from_attributes = True
