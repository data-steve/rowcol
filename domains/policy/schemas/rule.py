from pydantic import BaseModel
from typing import Optional, Dict

class RuleBase(BaseModel):
    business_id: str
    priority: int
    match_type: str
    pattern: str
    output: Dict
    scope: str

class RuleCreate(RuleBase):
    pass

class Rule(RuleBase):
    rule_id: int

    class Config:
        from_attributes = True