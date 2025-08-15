from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from domains.core.services.document_storage import DocumentStorageService
from domains.core.services.document_management import DocumentManagementService
from domains.core.services.document_review import DocumentReviewService
from domains.core.schemas.document import Document
from database import get_db
from typing import Dict

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=Document)
async def upload_document(file: UploadFile = File(...), firm_id: str = Form(...), client_id: int = Form(...), db: Session = Depends(get_db)):
    service = DocumentStorageService(db)
    document = service.store_document(file, firm_id, client_id)
    return document

@router.get("/{doc_id}", response_model=Document)
async def get_document(doc_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = DocumentStorageService(db)
    try:
        document = service.get_document(doc_id, firm_id)
        return document
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{doc_id}", response_model=Document)
async def update_document(doc_id: int, firm_id: str, data: Dict, db: Session = Depends(get_db)):
    service = DocumentManagementService(db)
    document = service.categorize_document(doc_id, firm_id)
    return document
