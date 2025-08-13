from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.suggestion import Suggestion as SuggestionModel
from schemas.suggestion import Suggestion
from database import get_db

router = APIRouter(prefix="/api", tags=["Suggestions"])

@router.post("/suggestions", response_model=Suggestion)
async def create_suggestion(suggestion: Suggestion, db: Session = Depends(get_db)):
    db_suggestion = SuggestionModel(**suggestion.dict())
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion

@router.get("/suggestions/{suggestion_id}", response_model=Suggestion)
async def get_suggestion(suggestion_id: int, firm_id: str, db: Session = Depends(get_db)):
    suggestion = db.query(SuggestionModel).filter(SuggestionModel.suggestion_id == suggestion_id, SuggestionModel.firm_id == firm_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return suggestion