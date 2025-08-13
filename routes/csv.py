from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from services.csv_ingestion import CsvIngestionService
from schemas.document import Document
from database import get_db

router = APIRouter(prefix="/api/csv", tags=["CSV"])

@router.post("/upload", response_model=Document)
async def upload_csv(file: UploadFile = File(...), firm_id: str = Form(...), client_id: int = Form(...), db: Session = Depends(get_db)):
    service = CsvIngestionService(db)
    document = service.ingest_csv(file, firm_id, client_id)
    return document

@router.post("/validate")
async def validate_csv(file: UploadFile = File(...), firm_id: str = None, client_id: int = None, db: Session = Depends(get_db)):
    service = CsvIngestionService(db)
    result = service.validate_csv(file)
    return result
