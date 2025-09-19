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
    # Import domains and runway to register all models via their __init__.py files
    import domains  # This will import all domain models
    import runway   # This will import all runway models
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")