"""
Runway AP Vendors API Routes

User-facing API endpoints for vendor management and normalization.
Orchestrates domains/ap/ vendor services with runway-specific analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from infra.database.session import get_db
from infra.auth.auth import get_current_business_id
from domains.ap.services.vendor import VendorService
# SmartSyncService is now handled by domain services
from domains.ap.schemas.vendor import VendorResponse, VendorCreate, VendorUpdate
from common.exceptions import ValidationError

router = APIRouter(tags=["AP Vendors"])

def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "vendor_service": VendorService(db, business_id)
    }

@router.get("/", response_model=List[VendorResponse])
async def list_vendors(
    active_only: bool = True,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    services: Dict = Depends(get_services)
):
    """
    List vendors with search and filtering capabilities.
    
    Includes payment statistics, reliability scores, and runway impact analysis.
    """
    try:
        vendor_service = services["vendor_service"]
        
        if search:
            vendors = vendor_service.find_vendors_by_name(search, fuzzy_match=True)
        else:
            vendors = vendor_service.list_vendors(active_only=active_only)
        
        enhanced_vendors = []
        for vendor in vendors:
            if active_only and not vendor.is_active:
                continue
                
            # Get payment history summary
            payment_summary = vendor_service.get_vendor_payment_history_summary(vendor.vendor_id)
            
            vendor_dict = {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "legal_name": vendor.legal_name,
                "contact_info": {
                    "email": vendor.email,
                    "phone": vendor.phone,
                    "contact_name": vendor.contact_name
                },
                "payment_info": {
                    "preferred_methods": vendor_service.get_vendor_payment_methods(vendor),
                    "terms": vendor.terms,
                    "reliability_score": vendor.payment_reliability_score,
                    "total_paid_ytd": payment_summary.get("total_paid_ytd", 0),
                    "average_payment_days": payment_summary.get("average_payment_days")
                },
                "compliance": {
                    "is_1099_vendor": vendor.is_1099_vendor,
                    "needs_w9_update": vendor_service.vendor_needs_w9_update(vendor),
                    "w9_status": vendor.w9_status
                },
                "status": {
                    "is_active": vendor.is_active,
                    "is_critical": vendor.is_critical
                },
                "created_at": vendor.created_at.isoformat(),
                "updated_at": vendor.updated_at.isoformat()
            }
            
            enhanced_vendors.append(vendor_dict)
        
        return enhanced_vendors
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list vendors: {str(e)}"
        )

@router.post("/", response_model=VendorResponse)
async def create_vendor(
    vendor_data: VendorCreate,
    services: Dict = Depends(get_services)
):
    """
    Create a new vendor with automatic normalization and QBO sync.
    """
    try:
        vendor_service = services["vendor_service"]
        
        # Create the vendor
        vendor = vendor_service.create_vendor(vendor_data.dict())
        
        # Record activity for smart sync
        sync_timing.record_user_activity("vendor_created")
        
        # Get enhanced vendor data
        vendor_service.get_vendor_payment_history_summary(vendor.vendor_id)
        
        return {
            "vendor_id": vendor.vendor_id,
            "name": vendor.name,
            "legal_name": vendor.legal_name,
            "contact_info": {
                "email": vendor.email,
                "phone": vendor.phone,
                "contact_name": vendor.contact_name
            },
            "payment_info": {
                "preferred_methods": vendor_service.get_vendor_payment_methods(vendor),
                "terms": vendor.terms,
                "reliability_score": vendor.payment_reliability_score
            },
            "compliance": {
                "is_1099_vendor": vendor.is_1099_vendor,
                "needs_w9_update": vendor_service.vendor_needs_w9_update(vendor),
                "w9_status": vendor.w9_status
            },
            "status": {
                "is_active": vendor.is_active,
                "is_critical": vendor.is_critical
            },
            "created_at": vendor.created_at.isoformat(),
            "updated_at": vendor.updated_at.isoformat()
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vendor: {str(e)}"
        )

@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: int,
    services: Dict = Depends(get_services)
):
    """Get detailed vendor information with payment history and compliance status."""
    try:
        vendor_service = services["vendor_service"]
        
        vendor = vendor_service._get_vendor_or_raise(vendor_id)
        payment_summary = vendor_service.get_vendor_payment_history_summary(vendor_id)
        
        return {
            "vendor_id": vendor.vendor_id,
            "name": vendor.name,
            "legal_name": vendor.legal_name,
            "tax_id": vendor.tax_id,
            "contact_info": {
                "email": vendor.email,
                "phone": vendor.phone,
                "contact_name": vendor.contact_name
            },
            "address": {
                "address_line1": vendor.address_line1,
                "address_line2": vendor.address_line2,
                "city": vendor.city,
                "state": vendor.state,
                "zip_code": vendor.zip_code,
                "country": vendor.country
            },
            "payment_info": {
                "preferred_methods": vendor_service.get_vendor_payment_methods(vendor),
                "terms": vendor.terms,
                "reliability_score": vendor.payment_reliability_score,
                "total_paid_ytd": payment_summary.get("total_paid_ytd", 0),
                "average_payment_days": payment_summary.get("average_payment_days")
            },
            "compliance": {
                "is_1099_vendor": vendor.is_1099_vendor,
                "needs_w9_update": vendor_service.vendor_needs_w9_update(vendor),
                "w9_status": vendor.w9_status,
                "w9_expiry_date": vendor.w9_expiry_date.isoformat() if vendor.w9_expiry_date else None
            },
            "status": {
                "is_active": vendor.is_active,
                "is_critical": vendor.is_critical,
                "vendor_type": vendor.vendor_type
            },
            "metadata": {
                "notes": vendor.notes,
                "tags": vendor.tags,
                "qbo_vendor_id": vendor.qbo_vendor_id
            },
            "created_at": vendor.created_at.isoformat(),
            "updated_at": vendor.updated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vendor: {str(e)}"
        )

@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: int,
    vendor_data: VendorUpdate,
    services: Dict = Depends(get_services)
):
    """Update vendor information with automatic QBO sync."""
    try:
        vendor_service = services["vendor_service"]
        
        # Update the vendor
        vendor = vendor_service.update_vendor(vendor_id, vendor_data.dict(exclude_unset=True))
        
        # Record activity for smart sync
        sync_timing.record_user_activity("vendor_updated")
        
        # Get updated summary
        vendor_service.get_vendor_payment_history_summary(vendor_id)
        
        return {
            "vendor_id": vendor.vendor_id,
            "name": vendor.name,
            "legal_name": vendor.legal_name,
            "contact_info": {
                "email": vendor.email,
                "phone": vendor.phone,
                "contact_name": vendor.contact_name
            },
            "payment_info": {
                "preferred_methods": vendor_service.get_vendor_payment_methods(vendor),
                "terms": vendor.terms,
                "reliability_score": vendor.payment_reliability_score
            },
            "compliance": {
                "is_1099_vendor": vendor.is_1099_vendor,
                "needs_w9_update": vendor_service.vendor_needs_w9_update(vendor),
                "w9_status": vendor.w9_status
            },
            "status": {
                "is_active": vendor.is_active,
                "is_critical": vendor.is_critical
            },
            "created_at": vendor.created_at.isoformat(),
            "updated_at": vendor.updated_at.isoformat()
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update vendor: {str(e)}"
        )

@router.get("/critical", response_model=List[VendorResponse])
async def get_critical_vendors(
    services: Dict = Depends(get_services)
):
    """Get all critical vendors that require priority attention."""
    try:
        vendor_service = services["vendor_service"]
        
        critical_vendors = vendor_service.get_critical_vendors()
        
        enhanced_vendors = []
        for vendor in critical_vendors:
            payment_summary = vendor_service.get_vendor_payment_history_summary(vendor.vendor_id)
            
            vendor_dict = {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "payment_info": {
                    "preferred_methods": vendor_service.get_vendor_payment_methods(vendor),
                    "reliability_score": vendor.payment_reliability_score,
                    "total_paid_ytd": payment_summary.get("total_paid_ytd", 0)
                },
                "compliance": {
                    "needs_w9_update": vendor_service.vendor_needs_w9_update(vendor)
                },
                "criticality_reason": "Critical vendor requiring priority attention"
            }
            
            enhanced_vendors.append(vendor_dict)
        
        return enhanced_vendors
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get critical vendors: {str(e)}"
        )

@router.get("/compliance/w9-updates", response_model=List[VendorResponse])
async def get_vendors_needing_w9_updates(
    services: Dict = Depends(get_services)
):
    """Get vendors that need W9 updates for compliance."""
    try:
        vendor_service = services["vendor_service"]
        
        vendors_needing_w9 = vendor_service.get_vendors_needing_w9_update()
        
        enhanced_vendors = []
        for vendor in vendors_needing_w9:
            vendor_dict = {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "compliance": {
                    "w9_status": vendor.w9_status,
                    "w9_expiry_date": vendor.w9_expiry_date.isoformat() if vendor.w9_expiry_date else None,
                    "needs_w9_update": True,
                    "is_1099_vendor": vendor.is_1099_vendor
                },
                "contact_info": {
                    "email": vendor.email,
                    "contact_name": vendor.contact_name
                }
            }
            
            enhanced_vendors.append(vendor_dict)
        
        return enhanced_vendors
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get vendors needing W9 updates: {str(e)}"
        )

@router.post("/{vendor_id}/payment-methods/validate")
async def validate_payment_method(
    vendor_id: int,
    payment_method: str,
    services: Dict = Depends(get_services)
):
    """Validate if a vendor accepts a specific payment method."""
    try:
        vendor_service = services["vendor_service"]
        
        vendor = vendor_service._get_vendor_or_raise(vendor_id)
        
        can_accept = vendor_service.can_vendor_accept_payment_method(vendor, payment_method)
        preferred_methods = vendor_service.get_vendor_payment_methods(vendor)
        
        return {
            "vendor_id": vendor_id,
            "payment_method": payment_method,
            "can_accept": can_accept,
            "preferred_methods": preferred_methods,
            "recommendation": {
                "use_method": payment_method if can_accept else preferred_methods[0] if preferred_methods else "check",
                "reason": "Accepted method" if can_accept else "Method not supported by vendor"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate payment method: {str(e)}"
        )
