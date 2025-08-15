"""
Preamble: Defines Pydantic schemas for the Close domain in Stage 2 of the Escher project.
Includes Base, Create, and full response schemas for API interactions.
References: Stage 2 requirements, domains/core/schemas/base.py.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PreCloseCheckBase(BaseModel):
    client_id: Optional[int] = None
    period: datetime
    type: str
    status: str = "pending"
    evidence_refs: List[str] = []

class PreCloseCheckCreate(PreCloseCheckBase):
    pass

class PreCloseCheck(PreCloseCheckBase):
    check_id: int
    firm_id: str

    class Config:
        from_attributes = True

class ExceptionBase(BaseModel):
    client_id: Optional[int] = None
    period: datetime
    type: str
    description: str
    resolution: Optional[str] = None

class ExceptionCreate(ExceptionBase):
    pass

class Exception(ExceptionBase):
    exception_id: int
    firm_id: str

    class Config:
        from_attributes = True

class PBCRequestBase(BaseModel):
    client_id: Optional[int] = None
    period: datetime
    item_type: str
    owner: str
    due_date: datetime
    status: str = "pending"
    reminders: List[datetime] = []
    task_id: Optional[int] = None

class PBCRequestCreate(BaseModel):
    period: datetime
    item_type: str
    owner: str
    due_date: datetime

class PBCRequest(PBCRequestBase):
    request_id: int
    firm_id: str

    class Config:
        from_attributes = True

class CloseChecklistBase(BaseModel):
    client_id: Optional[int] = None
    period: datetime
    items: List[int] = []
    status: str = "open"

class CloseChecklistCreate(BaseModel):
    period: datetime
    items: List[int] = []

class CloseChecklist(CloseChecklistBase):
    checklist_id: int
    firm_id: str

    class Config:
        from_attributes = True

class KPIResponse(BaseModel):
    score: float
    reconciled_transactions: int
    total_transactions: int
    reconciled_batches: int
    total_batches: int
    received_pbcs: int
    total_pbcs: int
    unresolved_exceptions: int
