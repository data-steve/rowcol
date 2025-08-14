from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.client import ClientService
from schemas.client import Client
from database import get_db

router = APIRouter(prefix="/api", tags=["Clients"])

@router.post("/clients", response_model=Client)
async def create_client(client: Client, db: Session = Depends(get_db)):
    service = ClientService(db)
    return service.create_client(client)

@router.get("/clients", response_model=list[Client])
async def list_clients(firm_id: str, db: Session = Depends(get_db)):
    service = ClientService(db)
    return service.list_clients(firm_id)

@router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = ClientService(db)
    try:
        return service.get_client(client_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))