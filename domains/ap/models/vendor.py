"""
Vendor model for AP vendor tracking and QBO integration.

Stores vendor records with payment methods, contact info, and compliance data.
Business logic handled by VendorService.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class PaymentMethod:
    """Payment method constants."""
    ACH = "ach"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    WIRE = "wire"
    CASH = "cash"

class Vendor(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vendors"
    vendor_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    canonical_vendor_id = Column(Integer, ForeignKey('vendor_canonicals.id'), nullable=True)
    
    # QBO Integration Fields
    qbo_vendor_id = Column(String(255), nullable=True, index=True)
    qbo_sync_token = Column(String(50), nullable=True)  # QBO sync token
    qbo_last_sync = Column(DateTime, nullable=True)     # Last QBO sync timestamp
    qbo_version = Column(String(20), nullable=True)     # QBO entity version
    
    # Vendor Information
    name = Column(String(255), nullable=False)          # Vendor display name
    legal_name = Column(String(255), nullable=True)     # Legal business name
    tax_id = Column(String(50), nullable=True)          # Tax ID/EIN
    
    # Payment Terms and Methods
    terms = Column(String(100), nullable=True)          # Payment terms (e.g., Net 30)
    preferred_payment_method = Column(String(50), nullable=True) # PaymentMethod enum
    payment_methods = Column(JSON, nullable=True)       # List of accepted payment methods
    
    # Banking Information
    bank_account_number = Column(String(100), nullable=True)  # Encrypted bank account
    routing_number = Column(String(20), nullable=True)   # Bank routing number
    bank_name = Column(String(255), nullable=True)       # Bank name
    
    # Contact Information  
    contact_name = Column(String(255), nullable=True)    # Primary contact
    email = Column(String(255), nullable=True)           # Contact email
    phone = Column(String(50), nullable=True)            # Contact phone
    
    # Address Information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(50), default="US")
    
    # Compliance and Documentation
    w9_status = Column(String(50), default="pending")   # pending, received, verified, expired
    w9_received_date = Column(DateTime, nullable=True)   # When W9 was received
    w9_expiry_date = Column(DateTime, nullable=True)     # When W9 expires
    insurance_status = Column(String(50), nullable=True) # Insurance verification status
    
    # Default Categorization
    default_gl_account = Column(String(100), nullable=True)  # Default GL account
    default_expense_category = Column(String(100), nullable=True) # Default category
    
    # Vendor Relationship Management
    vendor_type = Column(String(100), nullable=True)     # Type of vendor (supplier, contractor, etc.)
    is_1099_vendor = Column(Boolean, default=False)      # Whether vendor receives 1099
    is_critical = Column(Boolean, default=False)         # Critical vendor flag
    credit_limit = Column(Integer, nullable=True)        # Credit limit in cents
    
    # Performance Tracking
    total_paid_ytd_cents = Column(Integer, default=0)    # Total paid year-to-date
    average_payment_days = Column(Integer, nullable=True) # Average days to pay
    payment_reliability_score = Column(Integer, nullable=True) # 0-100 reliability score
    
    # Deduplication and Matching
    fingerprint_hash = Column(String(255), nullable=True) # For deduplication
    match_confidence = Column(Integer, default=0)        # Matching confidence score
    
    # Additional Metadata
    notes = Column(Text, nullable=True)                  # Internal notes
    tags = Column(JSON, nullable=True)                   # User-defined tags
    is_active = Column(Boolean, default=True)            # Whether vendor is active
    
    # Relationships
    vendor_canonical = relationship("VendorCanonical")
    business = relationship("Business")
    bills = relationship("Bill", back_populates="vendor")
    payments = relationship("Payment", back_populates="vendor")
    transaction_logs = relationship("VendorTransactionLog", back_populates="vendor")
    