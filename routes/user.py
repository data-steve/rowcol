from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.user import UserService
from schemas.user import User
from database import get_db

router = APIRouter(prefix="/api", tags=["Users"])

@router.post("/users", response_model=User)
async def create_user(user: User, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(user)

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        return service.get_user(user_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))