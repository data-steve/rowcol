from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domains.webhooks.models.webhook_event import WebhookEvent
from domains.integrations.plaid.sync import PlaidSyncService
from db.session import get_db

router = APIRouter()

class WebhookPayload(BaseModel):
    event: str
    data: dict
    
    

@router.post("/webhooks/plaid")
async def plaid_webhook(request: Request, db: Session = Depends(get_db)):
    """Process Plaid webhook events (TRANSACTIONS_UPDATE, etc.)."""
    payload = await request.json()
    business_id = payload.get("business_id")  # Assume added via integration setup
    event_key = f"plaid:{payload.get('transaction_id')}:{payload.get('created', '')[:10]}"

    if db.query(WebhookEvent).filter(
        WebhookEvent.business_id == business_id,
        WebhookEvent.id == event_key
    ).first():
        return {"status": "duplicate"}

    db.add(WebhookEvent(
        id=event_key,
        business_id=business_id,
        source="plaid",
        external_id=payload.get("transaction_id"),
        day_bucket=payload.get("created", "")[:10]
    ))

    service = PlaidSyncService(db)
    try:
        result = await service.sync(business_id, commit=True)
        return {"status": "success", "processed": len(result.get("added", []))}
    except Exception as e:
        return {"status": "error", "message": str(e)}

