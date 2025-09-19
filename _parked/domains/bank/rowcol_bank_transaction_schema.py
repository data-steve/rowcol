"""
Preamble: Defines Pydantic schemas for BankTransaction in Stage 1C of the Escher project.
Includes Base, Create, and full response schemas for API interactions.
References: Stage 1C requirements, schemas/firm.py, schemas/client.py.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BankTransactionBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    external_id: Optional[str] = None
    amount: float
    date: datetime
    description: str
    account_id: Optional[str] = None
    source: str
    status: str = "pending"

class BankTransactionCreate(BaseModel):
    amount: float
    date: datetime
    description: str
    account_id: Optional[str] = None
    source: str

class BankTransactionCategorize(BaseModel):
    transaction_id: int
    description: Optional[str] = None
    amount: Optional[float] = None

class BankTransaction(BankTransactionBase):
    transaction_id: int
    confidence: float
    rule_id: Optional[int] = None
    suggestion_id: Optional[int] = None

    class Config:
        from_attributes = True