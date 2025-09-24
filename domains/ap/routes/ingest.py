from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from domains.ap.services.ap_ingestion import IngestionService
from domains.ap.services.payment import PaymentService
from domains.ap.services.statement_reconciliation import StatementReconciliationService
from datetime import date

router = APIRouter()

@router.post("/")
def ingest_bill(file_path: str, business_id: int, db: Session = Depends(get_db)):
    service = IngestionService(db, str(business_id))
    return service.ingest_document(file_path, business_id)

@router.post("/payments")
def schedule_payment(payment_data: dict, business_id: str, db: Session = Depends(get_db)):
    service = PaymentService(db, business_id)
    return service.schedule_payment(
        business_id=business_id,
        bill_ids=payment_data["bill_ids"],
        funding_account=payment_data["funding_account"]
    )

@router.post("/statements/reconcile")
def reconcile_statement(reconcile_data: dict, business_id: str, db: Session = Depends(get_db)):
    service = StatementReconciliationService(db, business_id)
    return service.reconcile_statement(
        business_id=business_id,
        vendor_id=reconcile_data["vendor_id"],
        statement_file=reconcile_data["file_ref"],
        statement_date=date.fromisoformat(reconcile_data["period"]) if isinstance(reconcile_data["period"], str) else reconcile_data["period"]
    )
