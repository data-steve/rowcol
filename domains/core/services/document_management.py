from sqlalchemy.orm import Session
from domains.core.models.document import Document as DocumentModel
from domains.core.schemas.document import Document

class DocumentManagementService:
    def __init__(self, db: Session):
        self.db = db

    def categorize_document(self, doc_id: int, firm_id: str, 
                           extracted_fields: dict = None) -> Document:
        """Categorize document with extracted fields from OCR/ML processing."""
        document = self.db.query(DocumentModel).filter(
            DocumentModel.doc_id == doc_id, 
            DocumentModel.firm_id == firm_id
        ).first()
        if not document:
            raise ValueError("Document not found")
        
        # Use provided extracted fields or mock data for development
        if extracted_fields:
            document.extracted_fields = extracted_fields
        else:
            # Mock data for development - replace with actual OCR/ML service
            document.extracted_fields = {
                "vendor": "Mock Vendor",
                "amount": 0.0,
                "confidence": 0.5,
                "date": None,
                "description": "Placeholder extraction"
            }
        
        # Set status based on confidence threshold
        confidence = document.extracted_fields.get("confidence", 0.0)
        document.status = "review" if confidence < 0.9 else "processed"
        
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
