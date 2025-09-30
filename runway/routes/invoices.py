"""
Runway AR Invoices API Routes

User-facing API endpoints for invoice management workflows.
Orchestrates domains/ar/ services with runway-specific business logic.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from infra.database.session import get_db
from infra.auth.auth import get_current_business_id
from domains.ar.services.invoice import InvoiceService
from domains.ar.services.collections import CollectionsService
from runway.services.1_calculators.reserve_runway import RunwayReserveService
from runway.services.utils.qbo_mapper import QBOMapper
from common.exceptions import ValidationError

router = APIRouter(tags=["AR Invoices"])

def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "invoice_service": InvoiceService(db, business_id),
        "collections_service": CollectionsService(db, business_id),
        "reserve_service": RunwayReserveService(db, business_id)
    }

@router.get("/", response_model=List[Dict[str, Any]])
async def list_invoices(
    status_filter: Optional[str] = None,
    customer_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    services: Dict = Depends(get_services)
):
    """
    List invoices with filtering and runway impact analysis.
    
    Shows invoice status, payment progress, and cash flow impact calculations.
    """
    try:
        reserve_service = services["reserve_service"]
        business_id = services["reserve_service"].business_id
        
        # Get invoice data using domain service
        invoice_service = services["invoice_service"]
        
        # Get overdue invoices using domain service
        overdue_invoices = await invoice_service.get_overdue_invoices()
        
        # Get current runway for impact calculations
        runway_calc = reserve_service.calculate_runway_with_reserves()
        daily_burn = runway_calc.get("daily_burn", 1)
        
        enhanced_invoices = []
        count = 0
        
        for invoice_data in overdue_invoices:
            # Map QBO data to standardized format
            mapped_invoice = QBOMapper.map_invoice_data(invoice_data)
            
            # Apply filters
            if status_filter:
                balance = mapped_invoice.get("balance", 0)
                if status_filter == "paid" and balance > 0:
                    continue
                elif status_filter == "unpaid" and balance <= 0:
                    continue
                elif status_filter == "overdue":
                    due_date_str = mapped_invoice.get("due_date")
                    if due_date_str:
                        try:
                            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                            if datetime.utcnow() <= due_date:
                                continue
                        except (ValueError, TypeError):
                            continue
                    else:
                        continue
            
            if customer_id and mapped_invoice.get("customer", {}).get("id") != customer_id:
                continue
            
            # Apply pagination
            if count < offset:
                count += 1
                continue
            if len(enhanced_invoices) >= limit:
                break
            
            # Calculate runway impact
            balance = mapped_invoice.get("balance", 0)
            runway_impact_days = balance / daily_burn if daily_burn > 0 else 0
            
            # Determine status
            invoice_status = "paid" if balance <= 0 else "unpaid"
            if balance > 0:
                due_date_str = mapped_invoice.get("due_date")
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                        if datetime.utcnow() > due_date:
                            invoice_status = "overdue"
                    except (ValueError, TypeError):
                        pass
            
            enhanced_invoice = {
                "invoice_id": mapped_invoice.get("qbo_id"),
                "invoice_number": mapped_invoice.get("doc_number"),
                "customer": mapped_invoice.get("customer", {"id": None, "name": "Unknown"}),
                "amount": mapped_invoice.get("amount", 0),
                "balance": balance,
                "paid_amount": mapped_invoice.get("amount", 0) - balance,
                "issue_date": mapped_invoice.get("txn_date"),
                "due_date": mapped_invoice.get("due_date"),
                "status": invoice_status,
                "runway_impact": {
                    "collection_value_days": runway_impact_days,
                    "priority": "high" if runway_impact_days > 7 else "medium" if runway_impact_days > 3 else "low"
                }
            }
            
            enhanced_invoices.append(enhanced_invoice)
            count += 1
        
        return enhanced_invoices
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list invoices: {str(e)}"
        )

@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    services: Dict = Depends(get_services)
):
    """Get detailed invoice information with payment history and collection status."""
    try:
        collections_service = services["collections_service"]
        reserve_service = services["reserve_service"]
        business_id = services["reserve_service"].business_id
        
        # Get invoice data using domain service
        invoice_service = services["invoice_service"]
        
        # Get overdue invoices using domain service
        overdue_invoices = await invoice_service.get_overdue_invoices()
        
        # Find the specific invoice
        target_invoice = next((inv for inv in overdue_invoices if inv.get("Id") == invoice_id), None)
        if not target_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found"
            )
        
        # Map QBO data to standardized format
        mapped_invoice = QBOMapper.map_invoice_data(target_invoice)
        
        # Get customer payment history
        customer_id = mapped_invoice.get("customer", {}).get("id")
        payment_history = None
        if customer_id:
            try:
                payment_history = collections_service.get_customer_payment_history(customer_id)
            except Exception:
                payment_history = None
        
        # Calculate runway impact
        balance = mapped_invoice.get("balance", 0)
        runway_calc = reserve_service.calculate_runway_with_reserves()
        daily_burn = runway_calc.get("daily_burn", 1)
        runway_impact_days = balance / daily_burn if daily_burn > 0 else 0
        
        # Check if overdue
        is_overdue = False
        days_overdue = 0
        due_date_str = mapped_invoice.get("due_date")
        if due_date_str and balance > 0:
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                if datetime.utcnow() > due_date:
                    is_overdue = True
                    days_overdue = (datetime.utcnow() - due_date).days
            except (ValueError, TypeError):
                pass
        
        return {
            "invoice_id": invoice_id,
            "invoice_number": mapped_invoice.get("doc_number"),
            "customer": {
                "id": customer_id,
                "name": mapped_invoice.get("customer", {}).get("name", "Unknown"),
                "payment_history": payment_history["summary"] if payment_history else None
            },
            "amounts": {
                "total": mapped_invoice.get("amount", 0),
                "balance": balance,
                "paid": mapped_invoice.get("amount", 0) - balance
            },
            "dates": {
                "issue_date": mapped_invoice.get("txn_date"),
                "due_date": due_date_str,
                "days_overdue": days_overdue if is_overdue else 0
            },
            "status": {
                "is_paid": balance <= 0,
                "is_overdue": is_overdue,
                "collection_priority": "high" if days_overdue > 60 else "medium" if days_overdue > 30 else "low"
            },
            "runway_impact": {
                "collection_value_days": runway_impact_days,
                "current_runway_days": runway_calc.get("runway_days", 0),
                "impact_percentage": (runway_impact_days / runway_calc.get("runway_days", 1)) * 100 if runway_calc.get("runway_days", 0) > 0 else 0
            },
            "line_items": target_invoice.get("Line", []),
            "metadata": {
                "qbo_sync_status": "synced",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice: {str(e)}"
        )

@router.post("/{invoice_id}/send-reminder")
async def send_collection_reminder(
    invoice_id: str,
    reminder_data: dict,
    services: Dict = Depends(get_services)
):
    """
    Send a collection reminder for an invoice.
    
    Orchestrates reminder sending with tracking and runway impact notifications.
    """
    try:
        collections_service = services["collections_service"]
        
        reminder_type = reminder_data.get("type", "email")
        custom_message = reminder_data.get("message")
        
        result = collections_service.send_reminder(
            invoice_id=invoice_id,
            reminder_type=reminder_type,
            custom_message=custom_message
        )
        
        return {
            "message": "Collection reminder sent successfully",
            "invoice_id": invoice_id,
            "reminder_details": result
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send reminder: {str(e)}"
        )

@router.get("/{invoice_id}/payment-options")
async def get_payment_options(
    invoice_id: str,
    services: Dict = Depends(get_services)
):
    """
    Get payment options and scenarios for an invoice.
    
    Shows different payment timing options and their runway impact.
    """
    try:
        reserve_service = services["reserve_service"]
        business_id = services["reserve_service"].business_id
        
        # Get invoice details using domain service
        invoice_service = services["invoice_service"]
        
        # Get overdue invoices using domain service
        overdue_invoices = await invoice_service.get_overdue_invoices()
        
        target_invoice = next((inv for inv in overdue_invoices if inv.get("Id") == invoice_id), None)
        if not target_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found"
            )
        
        balance = float(target_invoice.get("Balance", 0))
        if balance <= 0:
            return {
                "message": "Invoice is already paid",
                "balance": balance
            }
        
        # Get runway calculation
        runway_calc = reserve_service.calculate_runway_with_reserves()
        daily_burn = runway_calc.get("daily_burn", 1)
        current_runway = runway_calc.get("runway_days", 0)
        
        # Calculate payment scenarios
        runway_extension = balance / daily_burn if daily_burn > 0 else 0
        
        scenarios = {
            "immediate_payment": {
                "description": "Customer pays immediately",
                "runway_extension_days": runway_extension,
                "new_runway_days": current_runway + runway_extension,
                "probability": "low"
            },
            "payment_plan_30_days": {
                "description": "30-day payment plan",
                "runway_extension_days": runway_extension,
                "new_runway_days": current_runway + runway_extension,
                "probability": "medium",
                "monthly_payment": balance / 1  # Single payment in 30 days
            },
            "payment_plan_60_days": {
                "description": "60-day payment plan (2 installments)",
                "runway_extension_days": runway_extension,
                "new_runway_days": current_runway + runway_extension,
                "probability": "high",
                "monthly_payment": balance / 2
            }
        }
        
        return {
            "invoice_id": invoice_id,
            "balance": balance,
            "current_runway_days": current_runway,
            "payment_scenarios": scenarios,
            "recommendations": [
                {
                    "scenario": "payment_plan_60_days",
                    "reason": "Highest probability of collection with manageable payments",
                    "priority": "recommended"
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment options: {str(e)}"
        )

@router.get("/runway-impact/summary")
async def get_invoices_runway_impact(
    services: Dict = Depends(get_services)
):
    """
    Get summary of how all outstanding invoices impact runway.
    
    Shows total AR value and potential runway extension from collections.
    """
    try:
        reserve_service = services["reserve_service"]
        business_id = services["reserve_service"].business_id
        
        # Get current runway
        runway_calc = reserve_service.calculate_runway_with_reserves()
        current_runway = runway_calc.get("runway_days", 0)
        daily_burn = runway_calc.get("daily_burn", 1)
        
        # Get outstanding invoices using domain service
        invoice_service = services["invoice_service"]
        
        # Get overdue invoices using domain service
        overdue_invoices = await invoice_service.get_overdue_invoices()
        
        total_ar = 0
        overdue_ar = 0
        current_ar = 0
        invoice_count = 0
        overdue_count = 0
        
        today = datetime.utcnow()
        
        for invoice_data in overdue_invoices:
            balance = float(invoice_data.get("Balance", 0))
            if balance <= 0:
                continue
            
            total_ar += balance
            invoice_count += 1
            
            # Check if overdue
            mapped_invoice = QBOMapper.map_invoice_data(invoice_data)
            due_date_str = mapped_invoice.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    if today > due_date:
                        overdue_ar += balance
                        overdue_count += 1
                    else:
                        current_ar += balance
                except (ValueError, TypeError):
                    current_ar += balance
            else:
                current_ar += balance
        
        # Calculate runway impact scenarios
        total_runway_extension = total_ar / daily_burn if daily_burn > 0 else 0
        overdue_runway_extension = overdue_ar / daily_burn if daily_burn > 0 else 0
        current_runway_extension = current_ar / daily_burn if daily_burn > 0 else 0
        
        return {
            "current_runway_days": current_runway,
            "daily_burn": daily_burn,
            "ar_summary": {
                "total_outstanding": total_ar,
                "overdue_amount": overdue_ar,
                "current_amount": current_ar,
                "invoice_count": invoice_count,
                "overdue_count": overdue_count
            },
            "runway_impact": {
                "total_potential_extension": total_runway_extension,
                "overdue_potential_extension": overdue_runway_extension,
                "current_potential_extension": current_runway_extension,
                "max_possible_runway": current_runway + total_runway_extension
            },
            "collection_priorities": {
                "focus_on_overdue": {
                    "amount": overdue_ar,
                    "runway_gain": overdue_runway_extension,
                    "effort_level": "medium"
                },
                "focus_on_large_invoices": {
                    "amount": total_ar,
                    "runway_gain": total_runway_extension,
                    "effort_level": "high"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get runway impact summary: {str(e)}"
        )
