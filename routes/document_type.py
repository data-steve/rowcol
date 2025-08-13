from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.document_type import DocumentType as DocumentTypeModel
from schemas.document_type import DocumentType, DocumentTypeCreate
from database import get_db

router = APIRouter(prefix="/api", tags=["DocumentTypes"])

@router.post("/document_types", response_model=DocumentType)
async def create_document_type(doc_type: DocumentTypeCreate, db: Session = Depends(get_db)):
    db_doc_type = DocumentTypeModel(**doc_type.dict())
    db.add(db_doc_type)
    db.commit()
    db.refresh(db_doc_type)
    return db_doc_type

@router.get("/document_types", response_model=list[DocumentType])
async def list_document_types(db: Session = Depends(get_db)):
    doc_types = db.query(DocumentTypeModel).all()
    return doc_types

@router.get("/document_types/{type_id}", response_model=DocumentType)
async def get_document_type(type_id: int, db: Session = Depends(get_db)):
    doc_type = db.query(DocumentTypeModel).filter(DocumentTypeModel.type_id == type_id).first()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return doc_type