from fastapi import UploadFile
from sqlalchemy.orm import Session
from domains.core.models.document import Document as DocumentModel
from domains.core.schemas.document import Document
import hashlib
from datetime import datetime

class DocumentStorageService:
    def __init__(self, db: Session):
        self.db = db

    def store_document(self, file: UploadFile, firm_id: str, client_id: int) -> Document:
        content = file.file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        document = DocumentModel(
            firm_id=firm_id,
            client_id=client_id,
            period="2025-01",
            type="invoice",
            file_ref=file.filename,
            hash=file_hash,
            upload_date=datetime.utcnow(),
            status="pending",
            extracted_fields={},
            review_status="pending"
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_document(self, doc_id: int, firm_id: str) -> Document:
        """Retrieve a document by ID with firm_id filtering."""
        document = self.db.query(DocumentModel).filter(
            DocumentModel.doc_id == doc_id, 
            DocumentModel.firm_id == firm_id
        ).first()
        if not document:
            raise ValueError("Document not found")
        return document
