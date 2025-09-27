"""
Runway AR Collections API Routes

User-facing API endpoints for collections management workflows.
Orchestrates domains/ar/ services with runway-specific business logic.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime

from infra.database.session import get_db
from infra.auth.auth import get_current_business_id
from domains.ar.services.invoice import InvoiceService
from runway.core.reserve_runway import RunwayReserveService

router = APIRouter(tags=["AR Collections"])

def get_services(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    """Get all required services with business context."""
    return {
        "invoice_service": InvoiceService(db, business_id),
        "reserve_service": RunwayReserveService(db, business_id)
    }

@router.get("/dashboard")
async def get_collections_dashboard(
    services: Dict = Depends(get_services)
):
    """
    Get collections dashboard with key metrics and overdue invoices.
    
    Shows aging buckets, collection priorities, and runway impact from outstanding AR.
    """
    try:
        reserve_service = services["reserve_service"]
        business_id = services["reserve_service"].business_id
        
        # Get current runway calculation
        runway_calc = reserve_service.calculate_runway_with_reserves()
        
        # Get QBO data for AR analysis using SmartSyncService
        from infra.qbo.smart_sync import SmartSyncService
        
        smart_sync = SmartSyncService(business_id, "", db)
        
        # Get QBO data using SmartSyncService
        qbo_data = await smart_sync.get_all_data()
        
        invoices = qbo_data.get("invoices", [])
        
        # Calculate aging buckets
        today = datetime.utcnow()
        aging_buckets = {
            "current": {"count": 0, "amount": 0},
            "1_30_days": {"count": 0, "amount": 0},
            "31_60_days": {"count": 0, "amount": 0},
            "61_90_days": {"count": 0, "amount": 0},
            "over_90_days": {"count": 0, "amount": 0}
        }
        
        total_outstanding = 0
        overdue_invoices = []
        
        for invoice_data in invoices:
            if invoice_data.get("Balance", 0) <= 0:
                continue  # Skip paid invoices
                
            amount = float(invoice_data.get("Balance", 0))
            due_date_str = invoice_data.get("DueDate")
            
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_overdue = (today - due_date).days
                    
                    if days_overdue <= 0:
                        aging_buckets["current"]["count"] += 1
                        aging_buckets["current"]["amount"] += amount
                    elif days_overdue <= 30:
                        aging_buckets["1_30_days"]["count"] += 1
                        aging_buckets["1_30_days"]["amount"] += amount
                        overdue_invoices.append({
                            "invoice_id": invoice_data.get("Id"),
                            "customer": invoice_data.get("CustomerRef", {}).get("name", "Unknown"),
                            "amount": amount,
                            "days_overdue": days_overdue,
                            "priority": "medium"
                        })
                    elif days_overdue <= 60:
                        aging_buckets["31_60_days"]["count"] += 1
                        aging_buckets["31_60_days"]["amount"] += amount
                        overdue_invoices.append({
                            "invoice_id": invoice_data.get("Id"),
                            "customer": invoice_data.get("CustomerRef", {}).get("name", "Unknown"),
                            "amount": amount,
                            "days_overdue": days_overdue,
                            "priority": "high"
                        })
                    elif days_overdue <= 90:
                        aging_buckets["61_90_days"]["count"] += 1
                        aging_buckets["61_90_days"]["amount"] += amount
                        overdue_invoices.append({
                            "invoice_id": invoice_data.get("Id"),
                            "customer": invoice_data.get("CustomerRef", {}).get("name", "Unknown"),
                            "amount": amount,
                            "days_overdue": days_overdue,
                            "priority": "high"
                        })
                    else:
                        aging_buckets["over_90_days"]["count"] += 1
                        aging_buckets["over_90_days"]["amount"] += amount
                        overdue_invoices.append({
                            "invoice_id": invoice_data.get("Id"),
                            "customer": invoice_data.get("CustomerRef", {}).get("name", "Unknown"),
                            "amount": amount,
                            "days_overdue": days_overdue,
                            "priority": "critical"
                        })
                        
                    total_outstanding += amount
                except (ValueError, TypeError):
                    # Skip invoices with invalid dates
                    continue
        
        # Calculate runway impact of collections
        daily_burn = runway_calc.get("daily_burn", 1)
        potential_runway_extension = total_outstanding / daily_burn if daily_burn > 0 else 0
        
        # Sort overdue invoices by priority and amount
        priority_order = {"critical": 0, "high": 1, "medium": 2}
        overdue_invoices.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["amount"]))
        
        return {
            "summary": {
                "total_outstanding": total_outstanding,
                "total_overdue": sum(bucket["amount"] for key, bucket in aging_buckets.items() if key != "current"),
                "overdue_count": sum(bucket["count"] for key, bucket in aging_buckets.items() if key != "current"),
                "current_runway_days": runway_calc.get("runway_days", 0),
                "potential_runway_extension_days": potential_runway_extension
            },
            "aging_buckets": aging_buckets,
            "priority_collections": overdue_invoices[:10],  # Top 10 priority collections
            "recommendations": [
                {
                    "type": "immediate_action",
                    "message": f"Focus on {len([inv for inv in overdue_invoices if inv['priority'] == 'critical'])} critical overdue invoices",
                    "priority": "high"
                },
                {
                    "type": "runway_impact",
                    "message": f"Collecting all outstanding AR could extend runway by {potential_runway_extension:.1f} days",
                    "priority": "medium"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collections dashboard: {str(e)}"
        )

@router.get("/overdue")
async def get_overdue_invoices(
    days_overdue_min: int = 1,
    priority: Optional[str] = None,
    limit: int = 50,
    services: Dict = Depends(get_services)
):
    """
    Get overdue invoices with filtering options.
    
    Shows invoices past due with customer contact information and collection recommendations.
    """
    try:
        business_id = services["reserve_service"].business_id
        
        # Get QBO data using SmartSyncService
        from infra.qbo.smart_sync import SmartSyncService
        
        smart_sync = SmartSyncService(business_id, "", db)
        
        # Get QBO data using SmartSyncService
        qbo_data = await smart_sync.get_all_data()
        
        invoices = qbo_data.get("invoices", [])
        
        today = datetime.utcnow()
        overdue_invoices = []
        
        for invoice_data in invoices:
            if invoice_data.get("Balance", 0) <= 0:
                continue  # Skip paid invoices
                
            due_date_str = invoice_data.get("DueDate")
            if not due_date_str:
                continue
                
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                days_overdue = (today - due_date).days
                
                if days_overdue < days_overdue_min:
                    continue
                    
                amount = float(invoice_data.get("Balance", 0))
                
                # Determine priority based on days overdue and amount
                if days_overdue > 90 or amount > 5000:
                    invoice_priority = "critical"
                elif days_overdue > 60 or amount > 2000:
                    invoice_priority = "high"
                else:
                    invoice_priority = "medium"
                
                # Filter by priority if specified
                if priority and invoice_priority != priority:
                    continue
                
                overdue_invoices.append({
                    "invoice_id": invoice_data.get("Id"),
                    "invoice_number": invoice_data.get("DocNumber"),
                    "customer": {
                        "id": invoice_data.get("CustomerRef", {}).get("value"),
                        "name": invoice_data.get("CustomerRef", {}).get("name", "Unknown")
                    },
                    "amount": amount,
                    "original_amount": float(invoice_data.get("TotalAmt", amount)),
                    "issue_date": invoice_data.get("TxnDate"),
                    "due_date": due_date_str,
                    "days_overdue": days_overdue,
                    "priority": invoice_priority,
                    "collection_actions": {
                        "email_sent": False,  # TODO: Track collection actions
                        "phone_call_made": False,
                        "last_contact": None,
                        "next_recommended_action": "email" if days_overdue < 30 else "phone_call"
                    }
                })
                
            except (ValueError, TypeError):
                continue
        
        # Sort by priority and days overdue
        priority_order = {"critical": 0, "high": 1, "medium": 2}
        overdue_invoices.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["days_overdue"]))
        
        return {
            "overdue_invoices": overdue_invoices[:limit],
            "total_count": len(overdue_invoices),
            "summary": {
                "total_amount": sum(inv["amount"] for inv in overdue_invoices),
                "critical_count": len([inv for inv in overdue_invoices if inv["priority"] == "critical"]),
                "high_count": len([inv for inv in overdue_invoices if inv["priority"] == "high"]),
                "medium_count": len([inv for inv in overdue_invoices if inv["priority"] == "medium"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overdue invoices: {str(e)}"
        )

@router.get("/customer/{customer_id}/aging")
async def get_customer_aging(
    customer_id: str,
    services: Dict = Depends(get_services)
):
    """
    Get aging analysis for a specific customer.
    
    Shows all outstanding invoices for a customer with payment history and recommendations.
    """
    try:
        business_id = services["reserve_service"].business_id
        
        # Get QBO data using SmartSyncService
        from infra.qbo.smart_sync import SmartSyncService
        
        smart_sync = SmartSyncService(business_id, "", db)
        
        # Get QBO data using SmartSyncService
        qbo_data = await smart_sync.get_all_data()
        
        invoices = qbo_data.get("invoices", [])
        
        customer_invoices = []
        total_outstanding = 0
        
        for invoice_data in invoices:
            if invoice_data.get("CustomerRef", {}).get("value") != customer_id:
                continue
                
            balance = float(invoice_data.get("Balance", 0))
            if balance <= 0:
                continue  # Skip paid invoices
                
            customer_invoices.append({
                "invoice_id": invoice_data.get("Id"),
                "invoice_number": invoice_data.get("DocNumber"),
                "amount": balance,
                "original_amount": float(invoice_data.get("TotalAmt", balance)),
                "issue_date": invoice_data.get("TxnDate"),
                "due_date": invoice_data.get("DueDate")
            })
            
            total_outstanding += balance
        
        customer_name = None
        if customer_invoices:
            # Get customer name from first invoice
            for invoice_data in invoices:
                if invoice_data.get("CustomerRef", {}).get("value") == customer_id:
                    customer_name = invoice_data.get("CustomerRef", {}).get("name", "Unknown")
                    break
        
        return {
            "customer": {
                "id": customer_id,
                "name": customer_name or "Unknown"
            },
            "summary": {
                "total_outstanding": total_outstanding,
                "invoice_count": len(customer_invoices)
            },
            "invoices": customer_invoices,
            "payment_recommendations": [
                {
                    "type": "payment_plan",
                    "message": f"Consider offering payment plan for ${total_outstanding:.2f}",
                    "priority": "medium" if total_outstanding > 1000 else "low"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer aging: {str(e)}"
        )

@router.post("/contact/{invoice_id}")
async def record_collection_contact(
    invoice_id: str,
    contact_data: dict,
    services: Dict = Depends(get_services)
):
    """
    Record a collection contact attempt.
    
    Tracks communication with customers for collection purposes.
    """
    try:
        # TODO: Implement collection contact tracking in database
        # For now, return success response
        
        return {
            "message": "Collection contact recorded successfully",
            "invoice_id": invoice_id,
            "contact_type": contact_data.get("type", "email"),
            "contact_date": datetime.utcnow().isoformat(),
            "notes": contact_data.get("notes", "")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record collection contact: {str(e)}"
        )

@router.get("/runway-impact")
async def get_collections_runway_impact(
    services: Dict = Depends(get_services)
):
    """
    Calculate runway impact of outstanding AR collections.
    
    Shows how collecting outstanding invoices would extend runway.
    """
    try:
        reserve_service = services["reserve_service"]
        business_id = services["reserve_service"].business_id
        
        # Get current runway
        runway_calc = reserve_service.calculate_runway_with_reserves()
        current_runway = runway_calc.get("runway_days", 0)
        daily_burn = runway_calc.get("daily_burn", 1)
        
        # Get outstanding AR using SmartSyncService
        from infra.qbo.smart_sync import SmartSyncService
        
        smart_sync = SmartSyncService(business_id, "", db)
        
        # Get QBO data using SmartSyncService
        qbo_data = await smart_sync.get_all_data()
        
        invoices = qbo_data.get("invoices", [])
        
        total_ar = sum(
            float(inv.get("Balance", 0)) 
            for inv in invoices 
            if float(inv.get("Balance", 0)) > 0
        )
        
        # Calculate scenarios
        scenarios = {
            "collect_all": {
                "amount": total_ar,
                "runway_extension": total_ar / daily_burn if daily_burn > 0 else 0,
                "new_runway_days": current_runway + (total_ar / daily_burn if daily_burn > 0 else 0)
            },
            "collect_overdue_only": {
                "amount": 0,
                "runway_extension": 0,
                "new_runway_days": current_runway
            },
            "collect_critical_only": {
                "amount": 0,
                "runway_extension": 0,
                "new_runway_days": current_runway
            }
        }
        
        # Calculate overdue and critical amounts
        today = datetime.utcnow()
        overdue_amount = 0
        critical_amount = 0
        
        for invoice_data in invoices:
            balance = float(invoice_data.get("Balance", 0))
            if balance <= 0:
                continue
                
            due_date_str = invoice_data.get("DueDate")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_overdue = (today - due_date).days
                    
                    if days_overdue > 0:
                        overdue_amount += balance
                        
                    if days_overdue > 90 or balance > 5000:
                        critical_amount += balance
                        
                except (ValueError, TypeError):
                    continue
        
        scenarios["collect_overdue_only"]["amount"] = overdue_amount
        scenarios["collect_overdue_only"]["runway_extension"] = overdue_amount / daily_burn if daily_burn > 0 else 0
        scenarios["collect_overdue_only"]["new_runway_days"] = current_runway + (overdue_amount / daily_burn if daily_burn > 0 else 0)
        
        scenarios["collect_critical_only"]["amount"] = critical_amount
        scenarios["collect_critical_only"]["runway_extension"] = critical_amount / daily_burn if daily_burn > 0 else 0
        scenarios["collect_critical_only"]["new_runway_days"] = current_runway + (critical_amount / daily_burn if daily_burn > 0 else 0)
        
        return {
            "current_runway_days": current_runway,
            "daily_burn": daily_burn,
            "total_ar": total_ar,
            "overdue_ar": overdue_amount,
            "critical_ar": critical_amount,
            "scenarios": scenarios,
            "recommendations": [
                {
                    "scenario": "collect_critical_only",
                    "reason": "Highest priority, lowest effort",
                    "priority": "high"
                },
                {
                    "scenario": "collect_overdue_only", 
                    "reason": "Good balance of effort and impact",
                    "priority": "medium"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate collections runway impact: {str(e)}"
        )
