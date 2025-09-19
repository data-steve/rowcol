"""
Preamble: Defines FastAPI routes for pre-close checks and exceptions in the Close domain, Stage 2.
References: Stage 2 requirements, domains/close/schemas/preclose.py, domains/close/services/preclose.py.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.close.services.preclose import PreCloseService, PBCTrackerService
from domains.close.schemas.preclose import PreCloseCheck, Exception, PBCRequest, PBCRequestCreate, CloseChecklist, CloseChecklistCreate, KPIResponse
from domains.close.models.preclose import Exception as ExceptionModel, CloseChecklist as CloseChecklistModel
from database import get_db
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/checks", tags=["Close"])

@router.post("", response_model=List[PreCloseCheck])
async def run_checks(
    period: datetime,
    firm_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        service = PreCloseService(db)
        return service.run_checks(firm_id, client_id, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/exceptions/{exception_id}", response_model=Exception)
async def get_exception(
    exception_id: int,
    firm_id: str,
    db: Session = Depends(get_db)
):
    try:
        service = PreCloseService(db)
        exception = service.db.query(ExceptionModel).filter(
            ExceptionModel.exception_id == exception_id,
            ExceptionModel.firm_id == firm_id
        ).first()
        if not exception:
            raise ValueError("Exception not found")
        return exception
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/exceptions/{exception_id}", response_model=Exception)
async def resolve_exception(
    exception_id: int,
    resolution: str,
    firm_id: str,
    db: Session = Depends(get_db)
):
    try:
        service = PreCloseService(db)
        return service.resolve_exception(firm_id, exception_id, resolution)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pbc", response_model=List[PBCRequest])
async def list_pbc_requests(
    firm_id: str,
    client_id: Optional[int] = None,
    period: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    try:
        service = PBCTrackerService(db)
        query = service.db.query(PBCRequestModel).filter(PBCRequestModel.firm_id == firm_id)
        if client_id:
            query = query.filter(PBCRequestModel.client_id == client_id)
        if period:
            query = query.filter(PBCRequestModel.period == period)
        return query.all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pbc", response_model=PBCRequest)
async def create_pbc_request(
    pbc: PBCRequestCreate,
    firm_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        service = PBCTrackerService(db)
        return service.create_pbc_request(pbc, firm_id, client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/pbc/{request_id}", response_model=PBCRequest)
async def update_pbc_status(
    request_id: int,
    status: str,
    firm_id: str,
    db: Session = Depends(get_db)
):
    try:
        service = PBCTrackerService(db)
        return service.update_pbc_status(firm_id, request_id, status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/checklist", response_model=List[CloseChecklist])
async def list_checklists(
    firm_id: str,
    client_id: Optional[int] = None,
    period: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(CloseChecklistModel).filter(CloseChecklistModel.firm_id == firm_id)
        if client_id:
            query = query.filter(CloseChecklistModel.client_id == client_id)
        if period:
            query = query.filter(CloseChecklistModel.period == period)
        return query.all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/checklist", response_model=CloseChecklist)
async def create_checklist(
    checklist: CloseChecklistCreate,
    firm_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        db_checklist = CloseChecklistModel(
            firm_id=firm_id,
            client_id=client_id,
            period=checklist.period,
            items=checklist.items,
            status="open"
        )
        db.add(db_checklist)
        db.commit()
        db.refresh(db_checklist)
        return db_checklist
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    firm_id: str,
    client_id: Optional[int] = None,
    period: datetime = datetime.utcnow(),
    db: Session = Depends(get_db)
):
    try:
        service = PBCTrackerService(db)
        return service.compute_readiness_score(firm_id, client_id, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
