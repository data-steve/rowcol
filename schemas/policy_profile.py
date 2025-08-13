from pydantic import BaseModel
from typing import Optional, List, Dict

class PolicyProfileBase(BaseModel):
    firm_id: str
    thresholds: Dict
    pricing_tier: str = "basic"
    doc_volume: int = 0
    client_id: Optional[int] = None
    revenue_policy: Optional[str] = None
    cutoff_rules: Optional[List] = None
    tickmark_map: Optional[Dict] = None
    deliverable_prefs: Optional[Dict] = None

class PolicyProfileCreate(PolicyProfileBase):
    pass

class PolicyProfile(PolicyProfileBase):
    profile_id: int

    class Config:
        from_attributes = True