from fastapi import UploadFile
from sqlalchemy.orm import Session
from domains.core.models.document import Document as DocumentModel
from domains.core.models.document_type import DocumentType as DocumentTypeModel
from domains.core.schemas.document import Document
from datetime import datetime
import csv
import io

class CsvIngestionService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_csv(self, file: UploadFile, firm_id: str, client_id: int) -> Document:
        # Validate tenant context
        DocumentModel.ensure_tenant_context(firm_id)
        
        content = file.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        doc_type = self.db.query(DocumentTypeModel).filter(DocumentTypeModel.name == "invoice").first()
        if not doc_type:
            raise ValueError("DocumentType 'invoice' not found")

        errors = []
        rows = list(reader)  # Convert to list so we can access rows
        for row in rows:
            for field in doc_type.fields:
                if doc_type.required == "y" and field not in row:
                    errors.append(f"Missing field: {field}")
        if errors:
            raise ValueError(f"CSV validation errors: {errors}")

        # Use the first row for extracted fields
        first_row = rows[0] if rows else {}
        
        document = DocumentModel(
            firm_id=firm_id,
            client_id=client_id,
            period="2025-01",
            type="invoice",
            file_ref=file.filename,
            hash="mock_hash",
            upload_date=datetime.now(),
            status="pending",
            extracted_fields={"vendor": first_row.get("Vendor"), "amount": first_row.get("Amount")},
            review_status="pending"
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def validate_csv(self, file: UploadFile) -> dict:
        content = file.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        doc_type = self.db.query(DocumentTypeModel).filter(DocumentTypeModel.name == "invoice").first()
        errors = []
        for row in reader:
            for field in doc_type.fields:
                if doc_type.required == "y" and field not in row:
                    errors.append(f"Missing field: {field}")
        return {"errors": errors}
