from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.data_ingestion import DataIngestionService
from services.ap_ingestion import APIngestionService
from services.vendor_normalization import VendorNormalizationService
from services.policy_engine import PolicyEngineService
from schemas.bill import Bill
from schemas.payment_intent import PaymentIntent
from schemas.vendor import Vendor
from schemas.vendor_statement import VendorStatement
from schemas.correction import Correction
from models.bill import Bill as BillModel
from models.vendor import Vendor as VendorModel
from models.payment_intent import PaymentIntent as PaymentIntentModel
from models.vendor_statement import VendorStatement as VendorStatementModel
from pydantic import BaseModel
from datetime import date
from database import get_db
from typing import Dict, List

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
        from services.statement_reconciliation import StatementReconciliationService
        
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