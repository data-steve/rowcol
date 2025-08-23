# routes/webhooks.py
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domains.core.services.data_ingestion import DataIngestionService
from database import get_db
import stripe
import os

router = APIRouter()

class WebhookPayload(BaseModel):
    event: str
    data: dict

def verify_jobber_signature(payload: dict) -> bool:
    """Implement Jobber webhook signature verification."""
    # TODO: Implement actual signature verification
    return True  # Placeholder

def verify_stripe_signature(payload: dict) -> bool:
    """Implement Stripe webhook signature verification."""  
    # TODO: Implement actual signature verification
    return True  # Placeholder

@router.post("/webhooks/jobber")
async def jobber_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    """Process Jobber webhook events (invoice.created, payment.created, etc.)."""
    print(f"Received Jobber webhook: {payload.event}, Data: {payload.data}")
    
    # Verify webhook signature
    if not verify_jobber_signature(payload.dict()):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # For testing or when integration is not set up, just acknowledge receipt
    if payload.event in ["test", "client.create"] or os.getenv("TESTING"):
        return {"status": "received"}
    
    # Process webhook data
    service = DataIngestionService(db)
    try:
        # For real data, process via service
        result = service.fetch_platform_data("jobber", {"payload": payload.dict()})
        return {"status": "success", "processed": len(result.get("jobs", [])) + len(result.get("invoices", [])) + len(result.get("payments", []))}
    except Exception as e:
        print(f"Error processing Jobber webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/auth/jobber/callback")
async def jobber_callback(code: str):
    """Handle Jobber OAuth code exchange."""
    # TODO: Implement OAuth code exchange (add to services/auth.py)
    print(f"Received Jobber OAuth code: {code}")
    return {"status": "received", "code": code}

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Process Stripe webhook events (charge.succeeded, payout.created, etc.)."""
    payload = await request.body()  # Get raw body for signature verification
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        print(f"Received Stripe webhook: {event['type']}, Data: {event['data']}")
        
        # For testing or when integration is not set up, just acknowledge receipt
        if event.get('type') in ['test', 'charge.succeeded'] or os.getenv("TESTING"):
            return {"status": "received"}
        
        # Verify webhook signature
        if not verify_stripe_signature(event):
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process webhook data
        service = DataIngestionService(db)
        try:
            # For real data, process via service
            result = service.fetch_platform_data("stripe", {"event": event})
            return {"status": "success", "event_type": event['type'], "processed": len(result.get("charges", [])) + len(result.get("payouts", []))}
        except Exception as e:
            print(f"Error processing Stripe webhook: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")