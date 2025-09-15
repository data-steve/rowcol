from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from ..services.onboarding import qualify_onboarding
from database import get_db

router = APIRouter(prefix="/onboard", tags=["Onboarding"])

@router.post("/")
async def onboard(email: str = Form(...), weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    result = qualify_onboarding(email, weekly_review, db)
    if result.get("dropoff"):
        return {"msg": result["reason"]}
    return result
