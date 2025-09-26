"""
VendorService - Vendor Lifecycle and Business Logic Management

Handles vendor business logic and lifecycle operations:
- Payment method validation
- W9 status tracking  
- Payment urgency calculation
- Payment statistics updates
- Vendor normalization and matching

Enhanced service following established architecture patterns.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from domains.core.services.base_service import TenantAwareService
from domains.ap.models.vendor import Vendor, PaymentMethod
from common.exceptions import ValidationError

logger = logging.getLogger(__name__)


class VendorService(TenantAwareService):
    """
    Comprehensive service for managing vendor business logic and lifecycle.
    
    Enhanced to include modern architecture patterns:
    - Tenant isolation (ADR-003)
    - Comprehensive business logic
    """
    
    def __init__(self, db: Session, business_id: str):
        """Initialize vendor service."""
        super().__init__(db, business_id)
        logger.info(f"Initialized VendorService for business {business_id}")
    
    # ==================== SMART SYNC DATA METHODS ====================
    
    def get_active_vendors(self) -> List[Dict[str, Any]]:
        """Get all active vendors for digest/sync purposes."""
        try:
            vendors = self.db.query(Vendor).filter(
                Vendor.business_id == self.business_id,
                Vendor.is_active
            ).all()
            
            return [
                {
                    "qbo_id": vendor.qbo_vendor_id,
                    "name": vendor.name,
                    "is_active": vendor.is_active,
                    "balance": 0,  # Would need to calculate from unpaid bills
                    "payment_terms": getattr(vendor, 'payment_terms', None),
                    "contact_info": {
                        "email": vendor.email,
                        "phone": vendor.phone
                    }
                }
                for vendor in vendors
            ]
        except Exception as e:
            logger.error(f"Failed to get active vendors: {e}")
            return []

    def list_vendors(self, active_only: bool = True) -> List[Vendor]:
        """Get all vendors with optional filtering."""
        try:
            query = self.db.query(Vendor).filter(Vendor.business_id == self.business_id)
            
            if active_only:
                query = query.filter(Vendor.is_active)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error listing vendors for business {self.business_id}: {e}")
            return []
    
    # ==================== VENDOR BUSINESS LOGIC ====================
    
    def get_vendor_payment_methods(self, vendor: Vendor) -> List[str]:
        """Get list of preferred payment methods for vendor."""
        if vendor.payment_methods:
            return vendor.payment_methods
        
        # Default payment methods if none specified
        if vendor.preferred_payment_method:
            return [vendor.preferred_payment_method]
        
        # Fallback to common methods
        return [PaymentMethod.ACH, PaymentMethod.CHECK]
    
    def can_vendor_accept_payment_method(self, vendor: Vendor, method: str) -> bool:
        """Check if vendor accepts a specific payment method."""
        accepted_methods = self.get_vendor_payment_methods(vendor)
        return method in accepted_methods
    
    def vendor_needs_w9_update(self, vendor: Vendor) -> bool:
        """Check if vendor W9 needs to be updated."""
        if vendor.w9_status in ["pending", "expired"]:
            return True
        
        if vendor.w9_expiry_date and vendor.w9_expiry_date < datetime.utcnow():
            return True
        
        return False
    
    def calculate_vendor_payment_urgency(self, vendor: Vendor, bill_amount: float) -> str:
        """Calculate payment urgency based on vendor relationship."""
        if vendor.is_critical:
            return "high"
        
        # Use centralized payment rules for consistent thresholds
        from infra.config import PaymentRules
        HIGH_AMOUNT_THRESHOLD = PaymentRules.HIGH_AMOUNT_THRESHOLD
        HIGH_RELIABILITY_THRESHOLD = PaymentRules.HIGH_RELIABILITY_THRESHOLD
        
        if bill_amount >= HIGH_AMOUNT_THRESHOLD or (vendor.payment_reliability_score and vendor.payment_reliability_score >= HIGH_RELIABILITY_THRESHOLD):
            return "medium"
        
        return "normal"
    
    def update_vendor_payment_stats(self, vendor: Vendor, payment_amount: float, days_to_pay: int):
        """Update vendor payment statistics."""
        # Update YTD total
        vendor.total_paid_ytd_cents += int(payment_amount * 100)
        
        # Update average payment days (simple moving average)
        if vendor.average_payment_days:
            vendor.average_payment_days = int((vendor.average_payment_days + days_to_pay) / 2)
        else:
            vendor.average_payment_days = days_to_pay
        
        # Update reliability score based on payment timeliness
        if days_to_pay <= 30:
            reliability_boost = 5
        elif days_to_pay <= 45:
            reliability_boost = 0
        else:
            reliability_boost = -5
        
        current_score = vendor.payment_reliability_score or 50
        vendor.payment_reliability_score = max(0, min(100, current_score + reliability_boost))
        
        vendor.updated_at = datetime.utcnow()
    
    # ==================== VENDOR MANAGEMENT ====================
    
    def create_vendor(self, vendor_data: Dict[str, Any]) -> Vendor:
        """Create a new vendor with validation."""
        try:
            # Validate required fields
            if not vendor_data.get('name'):
                raise ValidationError("Vendor name is required")
            
            vendor = Vendor(
                business_id=self.business_id,
                name=vendor_data['name'],
                legal_name=vendor_data.get('legal_name'),
                tax_id=vendor_data.get('tax_id'),
                terms=vendor_data.get('terms'),
                preferred_payment_method=vendor_data.get('preferred_payment_method'),
                payment_methods=vendor_data.get('payment_methods'),
                contact_name=vendor_data.get('contact_name'),
                email=vendor_data.get('email'),
                phone=vendor_data.get('phone'),
                address_line1=vendor_data.get('address_line1'),
                address_line2=vendor_data.get('address_line2'),
                city=vendor_data.get('city'),
                state=vendor_data.get('state'),
                zip_code=vendor_data.get('zip_code'),
                country=vendor_data.get('country', 'US'),
                vendor_type=vendor_data.get('vendor_type'),
                is_1099_vendor=vendor_data.get('is_1099_vendor', False),
                is_critical=vendor_data.get('is_critical', False),
                notes=vendor_data.get('notes'),
                tags=vendor_data.get('tags'),
                is_active=True
            )
            
            # Set default payment methods if not provided
            if not vendor.payment_methods:
                vendor.payment_methods = [PaymentMethod.ACH, PaymentMethod.CHECK]
            
            self.db.add(vendor)
            self.db.flush()
            
            logger.info(f"Created vendor {vendor.vendor_id}: {vendor.name}")
            return vendor
            
        except Exception as e:
            logger.error(f"Vendor creation failed: {str(e)}")
            raise
    
    def update_vendor(self, vendor_id: int, update_data: Dict[str, Any]) -> Vendor:
        """Update vendor information."""
        try:
            vendor = self._get_vendor_or_raise(vendor_id)
            
            # Update allowed fields
            updatable_fields = [
                'name', 'legal_name', 'tax_id', 'terms', 'preferred_payment_method',
                'payment_methods', 'contact_name', 'email', 'phone',
                'address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country',
                'vendor_type', 'is_1099_vendor', 'is_critical', 'notes', 'tags', 'is_active'
            ]
            
            for field in updatable_fields:
                if field in update_data:
                    setattr(vendor, field, update_data[field])
            
            vendor.updated_at = datetime.utcnow()
            
            logger.info(f"Updated vendor {vendor_id}")
            return vendor
            
        except Exception as e:
            logger.error(f"Vendor update failed: {str(e)}")
            raise
    
    def find_vendors_by_name(self, name: str, fuzzy_match: bool = True) -> List[Vendor]:
        """Find vendors by name with optional fuzzy matching."""
        query = self._base_query(Vendor)
        
        if fuzzy_match:
            # Use ILIKE for fuzzy matching
            query = query.filter(Vendor.name.ilike(f"%{name}%"))
        else:
            # Exact match
            query = query.filter(Vendor.name == name)
        
        return query.all()
    
    def get_critical_vendors(self) -> List[Vendor]:
        """Get all critical vendors for the business."""
        return self._base_query(Vendor).filter(
            Vendor.is_critical,
            Vendor.is_active
        ).all()
    
    def get_vendors_needing_w9_update(self) -> List[Vendor]:
        """Get vendors that need W9 updates."""
        vendors = self._base_query(Vendor).filter(Vendor.is_active).all()
        return [v for v in vendors if self.vendor_needs_w9_update(v)]
    
    def get_vendor_payment_history_summary(self, vendor_id: int) -> Dict[str, Any]:
        """Get payment history summary for a vendor."""
        vendor = self._get_vendor_or_raise(vendor_id)
        
        return {
            'vendor_id': vendor.vendor_id,
            'vendor_name': vendor.name,
            'total_paid_ytd': float(vendor.total_paid_ytd_cents / 100) if vendor.total_paid_ytd_cents else 0.0,
            'average_payment_days': vendor.average_payment_days,
            'payment_reliability_score': vendor.payment_reliability_score,
            'is_critical': vendor.is_critical,
            'preferred_payment_methods': self.get_vendor_payment_methods(vendor),
            'needs_w9_update': self.vendor_needs_w9_update(vendor)
        }
    
    # ==================== UTILITY METHODS ====================
    
    def _get_vendor_or_raise(self, vendor_id: int) -> Vendor:
        """Get vendor by ID or raise ValidationError."""
        return self._get_by_id_or_raise(Vendor, vendor_id, f"Vendor {vendor_id} not found")
