from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class DocumentBase(BaseModel):
    business_id: str
    period: str
    type: str
    file_ref: str
    hash: str
    upload_date: datetime
    status: str
    extracted_fields: Optional[Dict] = None
    review_status: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    doc_id: int

    class Config:
        from_attributes = True