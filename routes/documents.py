from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from services.document_storage import DocumentStorageService
from services.document_management import DocumentManagementService
from services.document_review import DocumentReviewService
from schemas.document import Document
from database import get_db
from typing import Dict

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=Document)
async def upload_document(file: UploadFile = File(...), firm_id: str = None, client_id: int = None, db: Session = Depends(get_db)):
    service = DocumentStorageService(db)
    document = service.store_document(file, firm_id, client_id)
    return document

@router.get("/{doc_id}", response_model=Document)
async def get_document(doc_id: int, firm_id: str, db: Session = Depends(get_db)):
    from models.document import Document as DocumentModel
    document = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id, DocumentModel.firm_id == firm_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document.from_orm(document)

@router.patch("/{doc_id}", response_model=Document)
async def update_document(doc_id: int, firm_id: str, data: Dict, db: Session = Depends(get_db)):
    service = DocumentManagementService(db)
    document = service.categorize_document(doc_id, firm_id)
    return document
