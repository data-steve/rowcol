from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infra.database.session import get_db
from domains.core.services.document_type import DocumentTypeService

router = APIRouter()

@router.get("/{type_id}")
def get_document_type(type_id: int, db: Session = Depends(get_db)):
    service = DocumentTypeService(db)
    return service.get_document_type(type_id)