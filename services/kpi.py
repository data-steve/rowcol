from sqlalchemy.orm import Session
from models.suggestion import Suggestion as SuggestionModel
from models.document import Document as DocumentModel
from models.task import Task as TaskModel

class KPIService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_kpis(self, firm_id: str) -> dict:
        suggestions = self.db.query(SuggestionModel).filter(SuggestionModel.firm_id == firm_id).all()
        documents = self.db.query(DocumentModel).filter(DocumentModel.firm_id == firm_id).all()
        tasks = self.db.query(TaskModel).filter(TaskModel.firm_id == firm_id).all()

        total_txns = len(suggestions)
        auto_posted = len([s for s in suggestions if s.top_k and s.top_k[0]["confidence"] >= 0.9])
        overrides = len([s for s in suggestions if s.chosen_idx is not None])
        doc_processing_time = 0
        csv_error_rate = 0
        ocr_review_time = 0
        task_completion_rate = len([t for t in tasks if t.status == "completed"]) / len(tasks) if tasks else 0

        return {
            "percent_auto_posted": (auto_posted / total_txns * 100) if total_txns else 0,
            "override_rate": (overrides / total_txns * 100) if total_txns else 0,
            "doc_processing_time": doc_processing_time,
            "csv_error_rate": csv_error_rate,
            "ocr_review_time": ocr_review_time,
            "task_completion_rate": task_completion_rate * 100
        }
