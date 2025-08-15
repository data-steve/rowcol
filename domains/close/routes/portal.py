"""
Preamble: Defines FastAPI routes for client portal in the Close domain, Stage 2.
References: Stage 2 requirements, domains/close/schemas/preclose.py, domains/close/services/preclose.py.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from domains.close.services.preclose import ClientPortalService
from domains.close.schemas.preclose import PBCRequest
from database import get_db
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/portal", tags=["Portal"])

@router.post("/login", response_model=dict)
async def login(
    email: str,
    password: str,
    firm_id: str,
    db: Session = Depends(get_db)
):
    try:
        service = ClientPortalService(db)
        return service.login(firm_id, email, password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/pbc/upload", response_model=PBCRequest)
async def upload_pbc(
    request_id: int,
    firm_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        service = ClientPortalService(db)
        return service.upload_pbc(firm_id, request_id, file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status", response_model=dict)
async def get_status(
    firm_id: str,
    client_id: Optional[int] = None,
    period: datetime = datetime.utcnow(),
    db: Session = Depends(get_db)
):
    try:
        service = ClientPortalService(db)
        return service.get_status(firm_id, client_id, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
