from fastapi import UploadFile
from sqlalchemy.orm import Session
from domains.core.models.document import Document as DocumentModel
from domains.core.schemas.document import Document
from domains.core.services.base_service import TenantAwareService
from common.exceptions import ValidationError
import hashlib
from datetime import datetime
from typing import Optional

class DocumentStorageService(TenantAwareService):
    """Document storage service for business-centric architecture."""
    
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)

    def store_document(
        self, 
        file: UploadFile, 
        document_type: str,
        period: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Document:
        """
        Store a document with proper business isolation.
        
        Args:
            file: Uploaded file
            document_type: Type of document (bill, invoice, receipt, etc.)
            period: Accounting period (defaults to current month)
            metadata: Additional document metadata
        """
        if not file.filename:
            raise ValidationError("File must have a filename")
            
        content = file.file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Default to current month if no period specified
        if not period:
            period = datetime.utcnow().strftime("%Y-%m")
            
        document = DocumentModel(
            business_id=self.business_id,  # Use business_id instead of firm/client
            period=period,
            type=document_type,
            file_ref=file.filename,
            hash=file_hash,
            upload_date=datetime.utcnow(),
            status="pending",
            extracted_fields=metadata or {},
            review_status="pending"
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_document(self, doc_id: int) -> Document:
        """Retrieve a document by ID with business isolation."""
        document = self._base_query(DocumentModel).filter(
            DocumentModel.doc_id == doc_id
        ).first()
        if not document:
            raise ValidationError(f"Document {doc_id} not found")
        return document
