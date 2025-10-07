"""
Stripe Webhook Handler

Handles Stripe webhook events for payment processing and A/R insights.
Part of the multi-rail Financial Control Plane infrastructure.
"""

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domains.webhooks.models.webhook_event import WebhookEvent
from infra.stripe.sync import StripeSyncService
from infra.database.session import get_db

router = APIRouter()

class WebhookPayload(BaseModel):
    event: str
    data: dict
    

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Process Stripe webhook events (payment_intent.succeeded, charge.succeeded, etc.)."""
    payload = await request.json()
    business_id = payload.get("business_id")  # Assume added via integration setup
    event_key = f"stripe:{payload.get('id')}:{payload.get('created', '')[:10]}"

    if db.query(WebhookEvent).filter(
        WebhookEvent.business_id == business_id,
        WebhookEvent.id == event_key
    ).first():
        return {"status": "duplicate"}

    db.add(WebhookEvent(
        id=event_key,
        business_id=business_id,
        source="stripe",
        external_id=payload.get("id"),
        day_bucket=payload.get("created", "")[:10]
    ))

    service = StripeSyncService(db)
    try:
        result = await service.sync(business_id, commit=True)
        return {"status": "success", "processed": len(result.get("added", []))}
    except Exception as e:
        return {"status": "error", "message": str(e)}
