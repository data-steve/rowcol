from fastapi import Form, Depends
from sqlalchemy.orm import Session
from domains.core.models import Firm, User, AuditLog
from database import get_db
from domains.integrations.qbo_auth import qbo_auth

def qualify_onboarding(email: str, weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    if not weekly_review:
        return {"dropoff": True, "reason": "No cash ritual need (20-30% expected)"}
    firm = Firm(name=f"{email.split('@')[0]} Agency", qbo_tenant_id=f"mock_{email.replace('@', '')}")
    db.add(firm)
    db.commit()
    user = User(firm_id=firm.id, email=email, role="owner")
    db.add(user)
    db.commit()
    access, refresh = qbo_auth.exchange_tokens("mock_code", firm.id)
    user.qbo_access_token = access
    user.qbo_refresh_token = refresh
    db.commit()
    audit = AuditLog(
        firm_id=firm.id, user_id=user.id, action_type="onboard_qualify",
        entity_type="firm", entity_id=str(firm.id), details={"qualified": True}
    )
    db.add(audit)
    db.commit()
    return {"success": True, "firm_id": firm.id, "next": "Connect QBO"}
