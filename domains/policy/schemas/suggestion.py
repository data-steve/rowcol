from pydantic import BaseModel
from typing import Optional, List, Dict

class SuggestionBase(BaseModel):
    business_id: str
    txn_id: str
    top_k: List[Dict[str, str | float]]
    chosen_idx: Optional[int] = None

class SuggestionCreate(SuggestionBase):
    pass

class Suggestion(SuggestionBase):
    suggestion_id: Optional[int] = None

    class Config:
        from_attributes = True