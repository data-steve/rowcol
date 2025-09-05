from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from domains.core.models.base import Base, TimestampMixin, TenantMixin
import uuid

class SyncCursor(Base, TimestampMixin, TenantMixin):
    __tablename__ = "sync_cursors"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    source = Column(String, nullable=False)  # jobber, plaid
    cursor = Column(String, nullable=True)  # pagination cursor
    last_full_backfill_at = Column(DateTime, nullable=True)
