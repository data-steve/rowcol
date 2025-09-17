from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.session import get_db
from domains.core.services.document_management import DocumentManagementService
from domains.core.services.document_review import DocumentReviewService
from domains.core.schemas.document import Document
from typing import Dict

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=Document)
async def upload_document(file: UploadFile = File(...), firm_id: str = Form(...), client_id: int = Form(...), db: Session = Depends(get_db)):
    service = DocumentManagementService(db)
    document = service.store_document(file, firm_id, client_id)
    return document

@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    service = DocumentManagementService(db)
    return service.get_document(document_id)

@router.patch("/{doc_id}", response_model=Document)
async def update_document(doc_id: int, firm_id: str, data: Dict, db: Session = Depends(get_db)):
    service = DocumentManagementService(db)
    document = service.categorize_document(doc_id, firm_id)
    return document
