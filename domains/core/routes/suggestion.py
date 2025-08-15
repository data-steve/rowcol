from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.services.suggestion import SuggestionService
from domains.core.schemas.suggestion import Suggestion
from database import get_db

router = APIRouter(prefix="/api", tags=["Suggestions"])

@router.post("/suggestions", response_model=Suggestion)
async def create_suggestion(suggestion: Suggestion, db: Session = Depends(get_db)):
    service = SuggestionService(db)
    return service.create_suggestion(suggestion)

@router.get("/suggestions/{suggestion_id}", response_model=Suggestion)
async def get_suggestion(suggestion_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = SuggestionService(db)
    try:
        return service.get_suggestion(suggestion_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))