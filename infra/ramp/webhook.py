"""
Ramp Webhook Handler

Handles Ramp webhook events for A/P execution and payment processing.
Part of the multi-rail Financial Control Plane infrastructure.
"""

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domains.webhooks.models.webhook_event import WebhookEvent
from infra.ramp.sync import RampSyncService
from infra.database.session import get_db

router = APIRouter()

class WebhookPayload(BaseModel):
    event: str
    data: dict
    

@router.post("/webhooks/ramp")
async def ramp_webhook(request: Request, db: Session = Depends(get_db)):
    """Process Ramp webhook events (transaction.created, transaction.updated, etc.)."""
    payload = await request.json()
    business_id = payload.get("business_id")  # Assume added via integration setup
    event_key = f"ramp:{payload.get('id')}:{payload.get('created_at', '')[:10]}"

    if db.query(WebhookEvent).filter(
        WebhookEvent.business_id == business_id,
        WebhookEvent.id == event_key
    ).first():
        return {"status": "duplicate"}

    db.add(WebhookEvent(
        id=event_key,
        business_id=business_id,
        source="ramp",
        external_id=payload.get("id"),
        day_bucket=payload.get("created_at", "")[:10]
    ))

    service = RampSyncService(db)
    try:
        result = await service.sync(business_id, commit=True)
        return {"status": "success", "processed": len(result.get("added", []))}
    except Exception as e:
        return {"status": "error", "message": str(e)}
