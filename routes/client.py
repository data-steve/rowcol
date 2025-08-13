from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.client import Client as ClientModel
from schemas.client import Client
from database import get_db

router = APIRouter(prefix="/api", tags=["Clients"])

@router.post("/clients", response_model=Client)
async def create_client(client: Client, db: Session = Depends(get_db)):
    db_client = ClientModel(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: int, firm_id: str, db: Session = Depends(get_db)):
    client = db.query(ClientModel).filter(ClientModel.client_id == client_id, ClientModel.firm_id == firm_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client