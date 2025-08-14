"""
Preamble: Defines Pydantic schemas for Transfer in Stage 1C of the Escher project.
Includes Base, Create, and full response schemas for API interactions.
References: Stage 1C requirements, schemas/bank_transaction.py.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransferBase(BaseModel):
    firm_id: str
    source_transaction_id: int
    destination_transaction_id: int
    amount: float
    date: datetime
    description: Optional[str] = None

class TransferCreate(BaseModel):
    source_transaction_id: int
    destination_transaction_id: int
    amount: float
    date: datetime
    description: Optional[str] = None

class Transfer(TransferBase):
    transfer_id: int

    class Config:
        from_attributes = True