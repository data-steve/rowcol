from sqlalchemy.orm import Session
from domains.core.models.suggestion import Suggestion as SuggestionModel
from domains.core.schemas.suggestion import Suggestion
from typing import List

class SuggestionService:
    def __init__(self, db: Session):
        self.db = db

    def create_suggestion(self, suggestion: Suggestion) -> SuggestionModel:
        """Create a new suggestion."""
        db_suggestion = SuggestionModel(**suggestion.dict())
        self.db.add(db_suggestion)
        self.db.commit()
        self.db.refresh(db_suggestion)
        return db_suggestion

    def get_suggestion(self, suggestion_id: int) -> SuggestionModel:
        """Get a suggestion by ID."""
        suggestion = self.db.query(SuggestionModel).filter(SuggestionModel.suggestion_id == suggestion_id).first()
        if not suggestion:
            raise ValueError("Suggestion not found")
        return suggestion

    def list_suggestions(self) -> List[SuggestionModel]:
        """List all suggestions."""
        suggestions = self.db.query(SuggestionModel).all()
        return suggestions
