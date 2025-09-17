from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.services.document_review import DocumentReviewService
from domains.core.schemas.document import Document
from database import get_db
from typing import List, Dict

router = APIRouter(prefix="/api/review", tags=["Review"])

@router.get("/documents", response_model=List[Document])
async def get_review_queue(firm_id: str, batch_by: str = "type", db: Session = Depends(get_db)):
    service = DocumentReviewService(db)
    documents = service.get_review_queue(firm_id, batch_by)
    return documents

@router.post("/documents", response_model=Document)
async def review_document(doc_id: int, firm_id: str, review_data: Dict, db: Session = Depends(get_db)):
    service = DocumentReviewService(db)
    document = service.review_document(doc_id, firm_id, review_data)
    return document
