from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.document_type import DocumentTypeService
from schemas.document_type import DocumentType, DocumentTypeCreate
from database import get_db

router = APIRouter(prefix="/api", tags=["DocumentTypes"])

@router.post("/document_types", response_model=DocumentType)
async def create_document_type(doc_type: DocumentTypeCreate, db: Session = Depends(get_db)):
    service = DocumentTypeService(db)
    return service.create_document_type(doc_type)

@router.get("/document_types", response_model=list[DocumentType])
async def list_document_types(db: Session = Depends(get_db)):
    service = DocumentTypeService(db)
    return service.list_document_types()

@router.get("/document_types/{type_id}", response_model=DocumentType)
async def get_document_type(type_id: int, db: Session = Depends(get_db)):
    service = DocumentTypeService(db)
    try:
        return service.get_document_type(type_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))