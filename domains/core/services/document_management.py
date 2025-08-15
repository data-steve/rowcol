from sqlalchemy.orm import Session
from domains.core.models.document import Document as DocumentModel
from domains.core.schemas.document import Document

class DocumentManagementService:
    def __init__(self, db: Session):
        self.db = db

    def categorize_document(self, doc_id: int, firm_id: str) -> Document:
        document = self.db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id, DocumentModel.firm_id == firm_id).first()
        if not document:
            raise ValueError("Document not found")
        document.extracted_fields = {"vendor": "Starbucks", "amount": 10.50, "confidence": 0.85}
        document.status = "review" if document.extracted_fields["confidence"] < 0.9 else "processed"
        self.db.commit()
        self.db.refresh(document)
        return document

    def archive_document(self, doc_id: int, firm_id: str) -> Document:
        document = self.db.query(DocumentModel).filter(DocumentModel.doc_id == doc_id, DocumentModel.firm_id == firm_id).first()
        if not document:
            raise ValueError("Document not found")
        document.status = "archived"
        self.db.commit()
        self.db.refresh(document)
        return document
