# domains/policy/services/factory.py
from sqlalchemy.orm import Session
from typing import Optional
from domains.policy.services.policy_engine import PolicyEngineService
from domains.policy.services.verticals.servicepro_engine import ServiceProPolicyEngine
from domains.policy.models.policy_profile import PolicyProfile as PolicyProfileModel

def get_policy_engine(firm_id: str, db: Session) -> PolicyEngineService:
    prof = (db.query(PolicyProfileModel)
            .filter(PolicyProfileModel.firm_id == firm_id)
            .order_by(PolicyProfileModel.updated_at.desc())
            .first())
    v = (getattr(prof, "vertical", "") or "").strip().lower()
    if v in {"servicepro", "service_pro", "contractor", "trades"}:
        return ServiceProPolicyEngine(db, firm_id=firm_id)
    # default/base
    return PolicyEngineService(db, firm_id=firm_id)
