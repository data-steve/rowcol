"""
RowCol MVP API Routes
QBO-only Financial Control Plane for Advisors
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import logging
import os

# Import runway services
from mvp.runway.wiring import create_tray_service, create_console_service, create_digest_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RowCol MVP API",
    description="QBO-only Financial Control Plane for Advisors",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for MVP recovery"""
    return {
        "status": "healthy",
        "service": "rowcol-mvp",
        "version": "0.1.0",
        "phase": "recovery"
    }

@app.get("/api/advisor/{advisor_id}/business/{business_id}/tray")
async def get_bill_tray(advisor_id: str, business_id: str) -> Dict[str, Any]:
    """
    Get bills organized by urgency for advisor review
    
    Uses TrayService with domain gateways to provide real data.
    Realm ID is automatically resolved from business_id.
    """
    try:
        # Create tray service using wiring (realm_id resolved automatically)
        tray_service = create_tray_service(advisor_id, business_id)
        
        # Get bill tray data
        tray_data = await tray_service.get_bill_tray()
        
        return {
            "advisor_id": advisor_id,
            "business_id": business_id,
            "urgent_count": tray_data["urgent_count"],
            "upcoming_count": tray_data["upcoming_count"],
            "total_count": tray_data["total_count"],
            "total_amount": tray_data["total_amount"],
            "runway_impact": f"{tray_data['runway_impact']} days",
            "urgent_bills": tray_data["urgent_bills"],
            "upcoming_bills": tray_data["upcoming_bills"],
            "last_updated": tray_data["last_updated"],
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get bill tray for advisor {advisor_id}, business {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get bill tray: {str(e)}")

@app.get("/api/advisor/{advisor_id}/business/{business_id}/console")
async def get_console_snapshot(advisor_id: str, business_id: str) -> Dict[str, Any]:
    """
    Get complete financial snapshot for advisor dashboard
    
    Uses ConsoleService with domain gateways to provide real data.
    Realm ID is automatically resolved from business_id.
    """
    try:
        # Create console service using wiring (realm_id resolved automatically)
        console_service = create_console_service(advisor_id, business_id)
        
        # Get console snapshot data
        snapshot_data = await console_service.get_console_snapshot()
        
        return {
            "advisor_id": advisor_id,
            "business_id": business_id,
            "cash_position": snapshot_data["cash_position"],
            "bills_due_this_week": snapshot_data["bills_due_this_week"],
            "total_ap": snapshot_data["total_ap"],
            "total_ar": snapshot_data["total_ar"],
            "runway_days": snapshot_data["runway_days"],
            "payment_ready_bills": snapshot_data["payment_ready_bills"],
            "collections_ready_invoices": snapshot_data["collections_ready_invoices"],
            "last_updated": snapshot_data["last_updated"],
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get console snapshot for advisor {advisor_id}, business {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get console snapshot: {str(e)}")

@app.get("/api/advisor/{advisor_id}/business/{business_id}/digest")
async def get_weekly_digest(advisor_id: str, business_id: str) -> Dict[str, Any]:
    """
    Get weekly summary of data quality and business insights
    
    Uses DigestService with domain gateways to provide real data.
    Realm ID is automatically resolved from business_id.
    """
    try:
        # Create digest service using wiring (realm_id resolved automatically)
        digest_service = create_digest_service(advisor_id, business_id)
        
        # Get weekly digest data
        digest_data = await digest_service.get_weekly_digest()
        
        return {
            "advisor_id": advisor_id,
            "business_id": business_id,
            "cash_position": digest_data["cash_position"],
            "total_ap": digest_data["total_ap"],
            "total_ar": digest_data["total_ar"],
            "runway_days": digest_data["runway_days"],
            "data_quality_score": digest_data["data_quality_score"],
            "hygiene_flags": digest_data["hygiene_flags"],
            "recommendations": digest_data["recommendations"],
            "last_updated": digest_data["last_updated"],
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get weekly digest for advisor {advisor_id}, business {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get weekly digest: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
