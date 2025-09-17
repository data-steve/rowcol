from fastapi import UploadFile
from sqlalchemy.orm import Session
from domains.core.models.document import Document as DocumentModel
from domains.core.models.document_type import DocumentType as DocumentTypeModel
from domains.core.schemas.document import Document
from domains.core.providers import HashProvider, get_hash_provider
from db.transaction import db_transaction
from common.exceptions import ValidationError, DataIngestionError
from config.business_rules import DocumentSettings
from datetime import datetime
from typing import Optional, Dict, Any
import csv
import io
import logging

logger = logging.getLogger(__name__)

class CsvIngestionService:
    def __init__(self, db: Session, hash_provider: Optional[HashProvider] = None):
        self.db = db
        self.hash_provider = hash_provider or get_hash_provider()

    def ingest_csv(self, file: UploadFile, firm_id: str, client_id: int) -> Document:
        """Ingest CSV file with proper validation and hash calculation."""
        # Validate tenant context
        DocumentModel.ensure_tenant_context(firm_id)
        
        try:
            content = file.file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(content))
            
            doc_type = self.db.query(DocumentTypeModel).filter(
                DocumentTypeModel.name == DocumentSettings.DEFAULT_DOCUMENT_TYPE
            ).first()
            if not doc_type:
                raise ValidationError(f"DocumentType '{DocumentSettings.DEFAULT_DOCUMENT_TYPE}' not found")

            # Validate CSV structure
            errors = []
            rows = list(reader)  # Convert to list so we can access rows
            for row in rows:
                for field in doc_type.fields:
                    if doc_type.required == "y" and field not in row:
                        errors.append(f"Missing field: {field}")
            if errors:
                raise ValidationError(f"CSV validation errors: {errors}")

            # Calculate file hash using provider
            file_hash = self.hash_provider.calculate_hash(content)
            
            # Use the first row for extracted fields
            first_row = rows[0] if rows else {}
            
            # Store document with proper transaction management
            with db_transaction(self.db):
                document = DocumentModel(
                    firm_id=firm_id,
                    client_id=client_id,
                    period=DocumentSettings.get_current_period(),
                    type=DocumentSettings.DEFAULT_DOCUMENT_TYPE,
                    file_ref=file.filename,
                    hash=file_hash,
                    upload_date=datetime.now(),
                    status=DocumentSettings.DEFAULT_DOCUMENT_STATUS,
                    extracted_fields={
                        "vendor": first_row.get("Vendor"), 
                        "amount": first_row.get("Amount")
                    },
                    review_status=DocumentSettings.DEFAULT_REVIEW_STATUS
                )
                self.db.add(document)
                self.db.flush()  # Get document ID
                
                logger.info(f"CSV document ingested: {document.id}, hash: {file_hash[:8]}...")
                return document
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"CSV ingestion failed: {e}", exc_info=True)
            raise DataIngestionError("CSV ingestion failed", {"error": str(e)})

    def validate_csv(self, file: UploadFile) -> Dict[str, Any]:
        """Validate CSV file structure without storing it."""
        try:
            content = file.file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(content))
            
            doc_type = self.db.query(DocumentTypeModel).filter(
                DocumentTypeModel.name == DocumentSettings.DEFAULT_DOCUMENT_TYPE
            ).first()
            if not doc_type:
                return {"valid": False, "errors": [f"DocumentType '{DocumentSettings.DEFAULT_DOCUMENT_TYPE}' not found"]}
            
            errors = []
            row_count = 0
            for row in reader:
                row_count += 1
                for field in doc_type.fields:
                    if doc_type.required == "y" and field not in row:
                        errors.append(f"Row {row_count}: Missing required field '{field}'")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "row_count": row_count,
                "expected_fields": doc_type.fields if doc_type else []
            }
            
        except Exception as e:
            logger.error(f"CSV validation failed: {e}")
            return {"valid": False, "errors": [f"File validation error: {str(e)}"]}

