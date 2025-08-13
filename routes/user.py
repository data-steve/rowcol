from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User as UserModel
from schemas.user import User
from database import get_db

router = APIRouter(prefix="/api", tags=["Users"])

@router.post("/users", response_model=User)
async def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, firm_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.user_id == user_id, UserModel.firm_id == firm_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user