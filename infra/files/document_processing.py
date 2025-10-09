"""
Document Processing Infrastructure

Provides file upload, processing, validation, and storage utilities
for documents across the application.

Key Features:
- File upload and validation
- Document metadata extraction
- Hash-based deduplication
- Business isolation
- Multiple storage backends
"""

import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import UploadFile
from sqlalchemy.orm import Session

from infra.config.exceptions import ValidationError
from domains.core.models.document import Document as DocumentModel
from domains.core.schemas.document import Document
from domains.core.services.base_service import TenantAwareService


class DocumentProcessor:
    """
    Core document processing utilities.
    
    Handles file validation, metadata extraction, and basic processing
    without being tied to specific storage backends.
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.doc', '.docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_file(cls, file: UploadFile) -> None:
        """
        Validate uploaded file for size, type, and basic requirements.
        
        Args:
            file: Uploaded file to validate
            
        Raises:
            ValidationError: If file is invalid
        """
        if not file.filename:
            raise ValidationError("File must have a filename")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file type: {file_ext}. "
                f"Supported types: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
        
        # Check file size (we need to read the file to check size)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"File too large: {file_size} bytes. "
                f"Maximum size: {cls.MAX_FILE_SIZE} bytes"
            )
        
        if file_size == 0:
            raise ValidationError("File is empty")
    
    @classmethod
    def calculate_file_hash(cls, content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content for deduplication.
        
        Args:
            content: File content as bytes
            
        Returns:
            SHA-256 hash as hex string
        """
        return hashlib.sha256(content).hexdigest()
    
    @classmethod
    def extract_metadata(cls, file: UploadFile) -> Dict[str, Any]:
        """
        Extract basic metadata from uploaded file.
        
        Args:
            file: Uploaded file
            
        Returns:
            Dictionary of extracted metadata
        """
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        return {
            "filename": file.filename,
            "file_size": file_size,
            "file_extension": file_ext,
            "content_type": file.content_type,
            "upload_timestamp": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def generate_document_id(cls, business_id: str, filename: str, file_hash: str) -> str:
        """
        Generate a unique document ID for storage.
        
        Args:
            business_id: Business identifier
            filename: Original filename
            file_hash: SHA-256 hash of file content
            
        Returns:
            Unique document identifier
        """
        # Create a deterministic ID based on business, filename, and hash
        id_data = f"{business_id}:{filename}:{file_hash}"
        return hashlib.md5(id_data.encode()).hexdigest()


class DocumentStorageService(TenantAwareService):
    """
    Document storage service for business-centric architecture.
    
    This is the infrastructure layer for document storage, moved from
    domains/core/services/document_storage.py to consolidate file processing.
    """
    
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
            
        Returns:
            Document schema object
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
