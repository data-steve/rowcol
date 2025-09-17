from sqlalchemy import Column, String, ForeignKey
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class WebhookEvent(Base, TimestampMixin, TenantMixin):
    __tablename__ = "webhook_events"
    id = Column(String, primary_key=True)  # source:external_id:day_bucket
    business_id = Column(String(36), ForeignKey("firms.business_id"), nullable=False)
    source = Column(String, nullable=False)  # jobber, plaid
    external_id = Column(String, nullable=True)
    day_bucket = Column(String, nullable=False)  # YYYY-MM-DD
