from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from domains.core.services.data_ingestion import DataIngestionService
from domains.ap.services.ingestion import APIngestionService
from domains.ap.services.vendor_normalization import VendorNormalizationService
from domains.policy.services.policy_engine import PolicyEngineService
from domains.ap.schemas.bill import Bill
from domains.ap.schemas.payment_intent import PaymentIntent
from domains.ap.schemas.vendor import Vendor
from domains.ap.schemas.vendor_statement import VendorStatement
from domains.policy.schemas.correction import Correction
from domains.ap.models.bill import Bill as BillModel
from domains.ap.models.vendor import Vendor as VendorModel
from domains.ap.models.payment_intent import PaymentIntent as PaymentIntentModel
from domains.ap.models.vendor_statement import VendorStatement as VendorStatementModel
from pydantic import BaseModel
from datetime import date
from database import get_db
from typing import Dict, List
import os

from domains.core.models.integration import Integration

# Minimal allowlist for external writes (extend via config later)
ALLOWED_TENANTS = set()

class DocumentIngestRequest(BaseModel):
    file_path: str

class PaymentRequest(BaseModel):
    bill_ids: List[int]
    funding_account: str

class StatementReconcileRequest(BaseModel):
    vendor_id: int
    file_ref: str
    period: date

router = APIRouter(prefix="/api/ingest", tags=["Ingest"])

@router.post("/qbo")
async def sync_qbo(firm_id: str, client_id: int, full_sync: bool = False, db: Session = Depends(get_db)):
    service = DataIngestionService(db)
    result = service.sync_qbo(firm_id, client_id, full_sync)
    return result

@router.post("/ap/bills", response_model=Dict)
async def sync_ap_bills(firm_id: str, client_id: int = None, full_sync: bool = False, db: Session = Depends(get_db)):
    """Sync bills from QBO."""
    service = APIngestionService(db)
    try:
        return service.sync_bills(firm_id, client_id, full_sync)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ap/bills/upload", response_model=Bill)
async def upload_bill(request: DocumentIngestRequest, firm_id: str, client_id: int = None, db: Session = Depends(get_db)):
    """Ingest a bill via OCR/CSV."""
    service = APIngestionService(db)
    try:
        return service.ingest_document(request.file_path, firm_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Safe Jobber/Stripe ingest endpoints (dry-run by default) ---

def _external_writes_enabled() -> bool:
    return os.getenv("EXTERNAL_WRITE_ENABLED", "false").lower() == "true"


def _allowed_tenant(firm_id: str, client_id: int) -> bool:
    return (firm_id, client_id) in ALLOWED_TENANTS


@router.post("/jobber", response_model=Dict)
async def ingest_jobber(
    firm_id: str,
    client_id: int,
    mode: str = "mock",  # "mock" | "live"
    commit: bool = False,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    """Safely ingest Jobber data. Dry-run by default; returns preview without writes.

    - mode=mock (default): returns generated preview data, no external calls
    - mode=live and commit=true requires EXTERNAL_WRITE_ENABLED=true and an Integration(platform="jobber")
    """
    service = DataIngestionService(db)

    # Always use preview unless explicitly allowed
    if mode != "live" or not commit or not _external_writes_enabled() or os.getenv("TESTING"):
        integration = db.query(Integration).filter_by(platform="jobber").first()
        # Generate safe mock preview
        if integration is None:
            class _I:
                pass
            integration = _I()
            integration.firm_id = firm_id
            integration.client_id = client_id
            integration.integration_id = "mock"
        preview = service._generate_simple_jobber_mock_data(integration)
        return {"status": "preview", "platform": "jobber", "result": preview}

    # Live path (guarded)
    if not _allowed_tenant(firm_id, client_id):
        raise HTTPException(status_code=403, detail="Tenant not allowlisted for external writes")
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")
    try:
        result = service.fetch_platform_data("jobber", credentials={})
        return {"status": "success", "platform": "jobber", "result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stripe", response_model=Dict)
async def ingest_stripe(
    firm_id: str,
    client_id: int,
    mode: str = "mock",  # "mock" | "live"
    commit: bool = False,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    """Safely ingest Stripe data. Dry-run by default; returns preview without writes.

    - Validates that only test keys are used; refuses live keys unless gated
    - mode=mock: returns generated preview data, no external calls
    - mode=live and commit=true requires EXTERNAL_WRITE_ENABLED=true and test-mode keys
    """
    service = DataIngestionService(db)

    # If not explicitly allowed, return safe preview
    if mode != "live" or not commit or not _external_writes_enabled() or os.getenv("TESTING"):
        integration = db.query(Integration).filter_by(platform="stripe").first()
        # Provide safe empty preview (no external call); shape matches service output
        return {"status": "preview", "platform": "stripe", "result": {"charges": [], "payouts": []}}

    # Live path with additional safety: enforce test key
    if not _allowed_tenant(firm_id, client_id):
        raise HTTPException(status_code=403, detail="Tenant not allowlisted for external writes")
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")
    integration = db.query(Integration).filter_by(platform="stripe").first()
    if not integration or not integration.access_token or not integration.access_token.startswith("sk_test_"):
        raise HTTPException(status_code=400, detail="Stripe test key required for live ingest")

    try:
        result = service.fetch_platform_data("stripe", credentials={})
        return {"status": "success", "platform": "stripe", "result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ap/bills/{id}", response_model=Bill)
async def get_bill(id: int, firm_id: str, db: Session = Depends(get_db)):
    """Get bill details."""
    bill = db.query(BillModel).filter(BillModel.bill_id == id, BillModel.firm_id == firm_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.patch("/ap/bills/{id}", response_model=Bill)
async def update_bill(id: int, firm_id: str, gl_account: str, db: Session = Depends(get_db)):
    """Update bill (e.g., GL account)."""
    bill = db.query(BillModel).filter(BillModel.bill_id == id, BillModel.firm_id == firm_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill.gl_account = gl_account
    bill.status = "review" if bill.confidence < 0.9 else "pending"
    db.commit()
    db.refresh(bill)
    return bill

@router.post("/ap/bills/categorize", response_model=Bill)
async def categorize_bill(bill_id: int, firm_id: str, client_id: int = None, db: Session = Depends(get_db)):
    """Categorize a bill."""
    bill = db.query(BillModel).filter(BillModel.bill_id == bill_id, BillModel.firm_id == firm_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Use existing vendor normalization service for categorization
    vendor_service = VendorNormalizationService(db)
    vendor = vendor_service.normalize_vendor(bill.extracted_fields.get("vendor_name", ""), firm_id, client_id)
    
    # Simple categorization logic
    if "food" in bill.extracted_fields.get("vendor_name", "").lower():
        bill.gl_account = "6000-Expenses"
        bill.confidence = 0.9
    else:
        bill.gl_account = "5000-Other Expenses"
        bill.confidence = 0.7
    
    bill.status = "review" if bill.confidence < 0.9 else "pending"
    db.commit()
    db.refresh(bill)
    return bill

@router.post("/ap/payments", response_model=PaymentIntent)
async def schedule_payment(request: PaymentRequest, firm_id: str, client_id: int = None, db: Session = Depends(get_db)):
    """Schedule a payment."""
    try:
        # Create payment intent
        payment_intent = PaymentIntentModel(
            firm_id=firm_id,
            client_id=client_id,
            bill_ids=request.bill_ids,  # Direct assignment for JSON field
            funding_account=request.funding_account,
            total_amount=0.0,  # Calculate from bills
            status="pending"
        )
        db.add(payment_intent)
        db.commit()
        db.refresh(payment_intent)
        return payment_intent
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ap/statements/reconcile", response_model=VendorStatement)
async def reconcile_statement(request: StatementReconcileRequest, firm_id: str, client_id: int = None, db: Session = Depends(get_db)):
    """Reconcile a vendor statement."""
    try:
        from domains.ap.services.statement_reconciliation import StatementReconciliationService
        
        # Pydantic already converted period to date object
        service = StatementReconciliationService(db)
        statement = service.reconcile_statement(firm_id, request.vendor_id, request.file_ref, request.period, client_id)
        return statement
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ap/vendors/{id}", response_model=Vendor)
async def get_vendor(id: int, firm_id: str, db: Session = Depends(get_db)):
    """Get vendor details."""
    vendor = db.query(VendorModel).filter(VendorModel.vendor_id == id, VendorModel.firm_id == firm_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.patch("/ap/vendors/{id}", response_model=Vendor)
async def update_vendor(id: int, firm_id: str, w9_status: str = None, terms: str = None, db: Session = Depends(get_db)):
    """Update vendor details."""
    vendor = db.query(VendorModel).filter(VendorModel.vendor_id == id, VendorModel.firm_id == firm_id).first()
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor not found")
    if w9_status:
        vendor.w9_status = w9_status
    if terms:
        vendor.terms = terms
    db.commit()
    db.refresh(vendor)
    return vendor

@router.post("/ap/document", response_model=Bill)
async def ingest_document(request: DocumentIngestRequest, firm_id: str, client_id: int = None, db: Session = Depends(get_db)):
    """Ingest a document (mock OCR for now)."""
    service = APIngestionService(db)
    try:
        return service.ingest_document(request.file_path, firm_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))