from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from domains.ap.services.ingest import IngestionService

router = APIRouter()

@router.post("/")
def ingest_bill(file_path: str, business_id: int, db: Session = Depends(get_db)):
    service = IngestionService(db)
    return service.ingest_document(file_path, business_id)
