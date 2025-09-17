"""
Model registration and table creation

Imports all models to ensure they're registered with SQLAlchemy Base.
"""
import logging
from .base import Base
from .session import engine

logger = logging.getLogger(__name__)

def create_db_and_tables():
    """Create all database tables by importing and registering models."""
    # Import all models here to ensure they are registered with Base
    from domains.core.models import user, business, balance, notification, integration, transaction, document, document_type, sync_cursor, audit_log
    from domains.ap.models import bill, vendor, payment
    from domains.ar.models import invoice, customer, credit_memo
    from domains.bank.models import bank_transaction, transfer
    from domains.policy.models import correction, policy_profile, rule, suggestion
    from runway.tray.models import tray_item
    from domains.vendor_normalization.models import vendor_canonical
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
