from sqlalchemy.orm import Session
from models.document import Document as DocumentModel
from schemas.document import Document
from typing import List

class DocumentReviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_review_queue(self, firm_id: str, batch_by: str = "type") -> List[Document]:
        query = self.db.query(DocumentModel).filter(DocumentModel.firm_id == firm_id, DocumentModel.status == "review")
        if batch_by == "type":
            query = query.order_by(DocumentModel.type)
        elif batch_by == "client":
            query = query.order_by(DocumentModel.client_id)
        documents = query.all()
        return documents

    def review_document(self, doc_id: int, firm_id: str, review_data: dict) -> Document:
        document = self.db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id, DocumentModel.firm_id == firm_id).first()
        if not document:
            raise ValueError("Document not found")
        document.extracted_fields.update(review_data)
        document.review_status = "confirmed"
        document.status = "processed"
        self.db.commit()
        self.db.refresh(document)
        return document
