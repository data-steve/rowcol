from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.document import Document as DocumentModel
from schemas.document import Document
from database import get_db

router = APIRouter(prefix="/api", tags=["Documents"])

@router.post("/documents", response_model=Document)
async def create_document(document: Document, db: Session = Depends(get_db)):
    db_document = DocumentModel(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/documents/{doc_id}", response_model=Document)
async def get_document(doc_id: int, firm_id: str, db: Session = Depends(get_db)):
    document = db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id, DocumentModel.firm_id == firm_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document