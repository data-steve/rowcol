"""
Preamble: Defines Pydantic schemas for PayrollBatch and PayrollRemittance in Stage 1D of the Escher project.
Includes Base, Create, and full response schemas for API interactions.
References: Stage 1D requirements, schemas/firm.py, schemas/client.py, schemas/bank_transaction.py.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PayrollBatchBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    total_amount: float
    payroll_date: datetime
    period_start: datetime
    period_end: datetime
    description: Optional[str] = None
    status: str = "pending"

class PayrollBatchCreate(BaseModel):
    total_amount: float
    payroll_date: datetime
    period_start: datetime
    period_end: datetime
    description: Optional[str] = None

class PayrollBatch(PayrollBatchBase):
    batch_id: int

    class Config:
        from_attributes = True

class PayrollRemittanceBase(BaseModel):
    firm_id: str
    batch_id: int
    amount: float
    tax_agency: str
    remittance_date: datetime
    status: str = "pending"

class PayrollRemittanceCreate(BaseModel):
    batch_id: int
    amount: float
    tax_agency: str
    remittance_date: datetime

class PayrollRemittance(PayrollRemittanceBase):
    remittance_id: int
    transaction_id: Optional[int] = None

    class Config:
        from_attributes = True