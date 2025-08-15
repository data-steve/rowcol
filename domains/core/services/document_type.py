from sqlalchemy.orm import Session
from domains.core.models.document_type import DocumentType as DocumentTypeModel
from domains.core.schemas.document_type import DocumentType
from typing import List

class DocumentTypeService:
    def __init__(self, db: Session):
        self.db = db

    def create_document_type(self, doc_type: DocumentType) -> DocumentType:
        """Create a new document type."""
        db_doc_type = DocumentTypeModel(**doc_type.dict())
        self.db.add(db_doc_type)
        self.db.commit()
        self.db.refresh(db_doc_type)
        return db_doc_type

    def get_document_type(self, type_id: int) -> DocumentType:
        """Get a document type by ID."""
        doc_type = self.db.query(DocumentTypeModel).filter(
            DocumentTypeModel.type_id == type_id
        ).first()
        if not doc_type:
            raise ValueError("Document type not found")
        return doc_type

    def list_document_types(self) -> List[DocumentType]:
        """List all document types."""
        doc_types = self.db.query(DocumentTypeModel).all()
        return doc_types
