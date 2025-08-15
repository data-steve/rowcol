from pydantic import BaseModel
from typing import Optional, Dict, List

class DocumentTypeBase(BaseModel):
    name: str
    fields: List[str]
    required: str
    validation_rules: Optional[Dict] = None

class DocumentTypeCreate(DocumentTypeBase):
    pass

class DocumentType(DocumentTypeBase):
    type_id: int

    class Config:
        from_attributes = True