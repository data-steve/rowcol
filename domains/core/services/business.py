"""
Business Service - Core Domain Business Entity Management

This service handles CRUD operations for Business entities.
Business entities represent the tenant/customer in our multi-tenant system.

Business Context:
- Each business represents a service agency customer
- Business entities are the root tenant for all other data
- Business management is a core domain primitive, not a runway feature

Key Responsibilities:
- Business creation, retrieval, update operations
- Business validation and data integrity
- Integration with user management for business ownership
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from domains.core.models.business import Business
from domains.core.schemas.business import BusinessCreate, BusinessUpdate
import uuid
import logging

logger = logging.getLogger(__name__)

class BusinessService:
    """Service for managing Business entities."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_business(self, business_data: BusinessCreate) -> Business:
        """Create a new business."""
        # Generate UUID for new business
        business_id = str(uuid.uuid4())
        
        # Create business entity
        db_business = Business(
            business_id=business_id,
            **business_data.dict()
        )
        
        self.db.add(db_business)
        self.db.commit()
        self.db.refresh(db_business)
        
        logger.info(f"Created new business: {business_id}")
        return db_business
    
    def get_business(self, business_id: str) -> Optional[Business]:
        """Get business by ID."""
        return self.db.query(Business).filter(
            Business.business_id == business_id
        ).first()
    
    def get_all_businesses(self) -> List[Business]:
        """Get all businesses (admin function)."""
        return self.db.query(Business).all()
    
    def update_business(self, business_id: str, business_update: BusinessUpdate) -> Optional[Business]:
        """Update business profile."""
        business = self.get_business(business_id)
        if not business:
            return None
        
        # Update only provided fields
        for field, value in business_update.dict(exclude_unset=True).items():
            setattr(business, field, value)
        
        self.db.commit()
        self.db.refresh(business)
        
        logger.info(f"Updated business: {business_id}")
        return business
    
    def delete_business(self, business_id: str) -> bool:
        """Delete business (admin function)."""
        business = self.get_business(business_id)
        if not business:
            return False
        
        self.db.delete(business)
        self.db.commit()
        
        logger.info(f"Deleted business: {business_id}")
        return True
    
    def business_exists(self, business_id: str) -> bool:
        """Check if business exists."""
        return self.db.query(Business).filter(
            Business.business_id == business_id
        ).first() is not None
