"""
AR domain routes for credit memos.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from domains.ar.schemas.credit_memo import CreditMemoCreate, CreditMemo
from domains.ap.services.adjustment import AdjustmentService

router = APIRouter()

@router.post("/credits", response_model=CreditMemo)
def create_credit_memo(
    credit_memo: CreditMemoCreate,
    firm_id: str,
    client_id: str,
    db: Session = Depends(get_db)
):
    service = AdjustmentService(db)
    return service.create_credit_memo(firm_id, credit_memo.invoice_id, credit_memo.amount, credit_memo.reason)
