from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.data_ingestion import DataIngestionService
from services.coa_sync import COASyncService
from database import get_db

router = APIRouter(prefix="/api/ingest", tags=["Ingest"])

@router.post("/qbo")
async def sync_qbo(firm_id: str, client_id: int, full_sync: bool = False, db: Session = Depends(get_db)):
    service = DataIngestionService(db)
    result = service.sync_qbo(firm_id, client_id, full_sync)
    return result
