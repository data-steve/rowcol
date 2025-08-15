from pydantic import BaseModel
from typing import Optional, List, Dict

class ServiceBase(BaseModel):
    firm_id: str
    name: str
    description: Optional[str] = None
    service_type: str = "bookkeeping"
    price: float
    complexity_score: float = 1.0
    task_sequence: List[Dict]
    tier: str = "basic"
    automation_score: float = 0.0
    client_instructions: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    service_id: int

    class Config:
        from_attributes = True

class ServicePreview(BaseModel):
    service_id: int
    name: str
    task_sequence: List[Dict]
    compliance_requirements: List[Dict]

    class Config:
        from_attributes = True