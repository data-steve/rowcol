from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domains.core.services.data_ingestion import DataIngestionService
from domains.webhooks.models.webhook_event import WebhookEvent
from domains.integrations.jobber.sync import JobberSyncService
from domains.integrations.plaid.sync import PlaidSyncService
from database import get_db
import stripe
import os

router = APIRouter()

class WebhookPayload(BaseModel):
    event: str
    data: dict

def verify_jobber_signature(payload: dict) -> bool:
    # TODO: Implement actual signature verification
    return True

def verify_stripe_signature(payload: dict) -> bool:
    # TODO: Implement actual signature verification
    return True

@router.post("/webhooks/jobber")
async def jobber_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    """Process Jobber webhook events (invoice.created, payment.created, etc.)."""
    if not verify_jobber_signature(payload.dict()):
        raise HTTPException(status_code=403, detail="Invalid signature")

    firm_id = payload.data.get("firm_id")
    event_key = f"jobber:{payload.data.get('id')}:{payload.data.get('created_at', '')[:10]}"
    if db.query(WebhookEvent).filter(
        WebhookEvent.firm_id == firm_id,
        WebhookEvent.id == event_key
    ).first():
        return {"status": "duplicate"}

    db.add(WebhookEvent(
        id=event_key,
        firm_id=firm_id,
        source="jobber",
        external_id=payload.data.get("id"),
        day_bucket=payload.data.get("created_at", "")[:10]
    ))

    if payload.event in ["test", "client.create"] or os.getenv("TESTING"):
        return {"status": "received"}

    service = JobberSyncService(db)
    try:
        result = await service.sync(firm_id, commit=True)
        return {"status": "success", "processed": len(result.get("invoices", {}).get("nodes", []))}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/webhooks/plaid")
async def plaid_webhook(request: Request, db: Session = Depends(get_db)):
    """Process Plaid webhook events (TRANSACTIONS_UPDATE, etc.)."""
    payload = await request.json()
    firm_id = payload.get("firm_id")  # Assume added via integration setup
    event_key = f"plaid:{payload.get('transaction_id')}:{payload.get('created', '')[:10]}"

    if db.query(WebhookEvent).filter(
        WebhookEvent.firm_id == firm_id,
        WebhookEvent.id == event_key
    ).first():
        return {"status": "duplicate"}

    db.add(WebhookEvent(
        id=event_key,
        firm_id=firm_id,
        source="plaid",
        external_id=payload.get("transaction_id"),
        day_bucket=payload.get("created", "")[:10]
    ))

    service = PlaidSyncService(db)
    try:
        result = await service.sync(firm_id, commit=True)
        return {"status": "success", "processed": len(result.get("added", []))}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/auth/jobber/callback")
async def jobber_callback(code: str):
    """Handle Jobber OAuth code exchange."""
    # TODO: Implement OAuth code exchange
    return {"status": "received", "code": code}
