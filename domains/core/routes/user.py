from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from domains.core.services.user import UserService

router = APIRouter()

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_user(user_id)