from fastapi import Form, Depends
from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.services.audit_log import AuditLogService
from database import get_db
from domains.integrations.qbo_auth import qbo_auth

def qualify_onboarding(email: str, weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    if not weekly_review:
        return {"dropoff": True, "reason": "No cash ritual need (20-30% expected)"}
    business = Business(name=f"{email.split('@')[0]} Agency", qbo_id=f"mock_{email.replace('@', '')}")
    db.add(business)
    db.commit()
    access, refresh = qbo_auth.exchange_tokens("mock_code", business.client_id)
    audit_service = AuditLogService(db)
    audit_service.log_event(
        business_id=business.client_id,
        action_type="onboard_qualify",
        entity_type="business",
        entity_id=str(business.client_id),
        details={"qualified": True}
    )
    return {"success": True, "business_id": business.client_id, "next": "Connect QBO"}
