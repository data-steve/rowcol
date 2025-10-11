"""
Database Session Management for MVP

Provides centralized SQLite session management.
SINGLE SOURCE OF TRUTH for database configuration.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# SINGLE SOURCE OF TRUTH for database path
# All code should import from this module, never hardcode paths
_db_path = os.getenv("SQLALCHEMY_DATABASE_URL", "/Users/stevesimpson/projects/rowcol/_clean/rowcol.db")

# Construct SQLAlchemy URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_path}" if not _db_path.startswith("sqlite") else _db_path

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Get database session for dependency injection.
    Use with FastAPI Depends() or in context managers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_database_url():
    """Get the database URL. For tests and configuration."""
    return SQLALCHEMY_DATABASE_URL


def get_database_engine():
    """Get the database engine. For tests and direct queries."""
    return engine


def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# Export commonly used items
__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'get_database_url',
    'get_database_engine',
    'test_connection',
    'SQLALCHEMY_DATABASE_URL'
]
