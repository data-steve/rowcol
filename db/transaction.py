"""Database transaction management utilities."""

from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

@contextmanager
def db_transaction(db: Session) -> Generator[Session, None, None]:
    """
    Context manager for database transactions.
    
    Ensures that all operations within the context are committed together
    or all are rolled back if any operation fails.
    
    Usage:
        with db_transaction(db):
            business = Business(**business_data)
            db.add(business)
            db.flush()  # Get ID without committing
            
            user = User(business_id=business.business_id, **user_data)
            db.add(user)
            # Both saved together or both fail
    
    Args:
        db: SQLAlchemy database session
        
    Yields:
        db: The same database session
        
    Raises:
        Any exception that occurs during the transaction
    """
    try:
        yield db
        db.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}", exc_info=True)
        raise

@contextmanager
def db_savepoint(db: Session, savepoint_name: str = None) -> Generator[Session, None, None]:
    """
    Context manager for database savepoints (nested transactions).
    
    Useful for operations that might fail but shouldn't rollback the entire transaction.
    
    Usage:
        with db_transaction(db):
            # Main transaction
            business = Business(**business_data)
            db.add(business)
            
            try:
                with db_savepoint(db, "optional_user"):
                    # This might fail, but won't affect business creation
                    user = User(**user_data)
                    db.add(user)
            except UserCreationError:
                # Business still gets created, just without user
                logger.warning("User creation failed, continuing without user")
    
    Args:
        db: SQLAlchemy database session
        savepoint_name: Optional name for the savepoint
        
    Yields:
        db: The same database session
    """
    savepoint = db.begin_nested()
    try:
        yield db
        savepoint.commit()
        logger.debug(f"Savepoint {savepoint_name or 'unnamed'} committed successfully")
    except Exception as e:
        savepoint.rollback()
        logger.warning(f"Savepoint {savepoint_name or 'unnamed'} rolled back: {e}")
        raise
