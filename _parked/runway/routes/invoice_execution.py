"""
Invoice Execution Routes - Parked for Future Stripe Implementation

These routes contain invoice creation and sending endpoints
that were moved from domains/ar/routes/invoices.py to maintain QBO-honest architecture.

QBO is only a ledger rail - it cannot create invoices.
These routes will be implemented by Stripe when invoice creation is enabled.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from infra.database.session import get_db
from infra.auth.auth import get_current_business_id, get_current_user
from _parked.domains.ar.services.invoice_management_service import InvoiceManagementService

router = APIRouter(prefix="/invoices", tags=["A/R Invoice Execution - Parked"])

def get_execution_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get execution services - will be implemented by Stripe."""
    return {
        "invoice_management_service": InvoiceManagementService(db, business_id)
    }

@router.post("/create")
async def create_invoice(
    invoice_data: dict,
    services: Dict = Depends(get_execution_services),
    current_user: dict = Depends(get_current_user)
):
    """
    Create invoice - PARKED for Stripe implementation.
    
    This endpoint was moved from domains/ar/routes/invoices.py to maintain
    QBO-honest architecture. Will be implemented by Stripe.
    """
    try:
        invoice_management_service = services["invoice_management_service"]
        
        # Future Stripe implementation
        result = await invoice_management_service.create_invoice(
            customer_id=invoice_data["customer_id"],
            items=invoice_data["lines"]
        )
        
        return {
            "message": "Invoice creation - will be implemented by Stripe",
            "invoice_data": invoice_data,
            "status": "parked",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invoice creation error: {str(e)}"
        )

@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: str,
    services: Dict = Depends(get_execution_services),
    current_user: dict = Depends(get_current_user)
):
    """
    Send invoice - PARKED for Stripe implementation.
    
    This endpoint was moved from domains/ar/routes/invoices.py to maintain
    QBO-honest architecture. Will be implemented by Stripe.
    """
    try:
        invoice_management_service = services["invoice_management_service"]
        
        # Future Stripe implementation
        result = await invoice_management_service.send_invoice(invoice_id)
        
        return {
            "message": "Invoice sending - will be implemented by Stripe",
            "invoice_id": invoice_id,
            "status": "parked",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invoice sending error: {str(e)}"
        )
