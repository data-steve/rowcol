from sqlalchemy import Column, Integer, String, JSON
from domains.core.models.base import Base, TimestampMixin

class DocumentType(Base, TimestampMixin):
    __tablename__ = "document_types"
    type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # invoice, statement, receipt, payroll
    fields = Column(JSON, nullable=False)  # List of field names
    required = Column(String, default="n")  # y, n
    validation_rules = Column(JSON, nullable=True)