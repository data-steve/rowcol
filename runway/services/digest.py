from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.models.business import Business
from domains.ap.models.bill import Bill
from domains.ar.models.invoice import Invoice
from domains.integrations.qbo_integration import QBOIntegration
from datetime import datetime, timedelta
from typing import Dict

def calculate_runway(db: Session, business_id: int) -> Dict[str, float]:
    business = db.query(Business).filter(Business.client_id == business_id).first()
    if not business:
        raise ValueError("Business not found")
    qbo = QBOIntegration(business)
    balances = db.query(Balance).filter(
        Balance.business_id == business_id,
        Balance.snapshot_date >= datetime.utcnow() - timedelta(days=1)
    ).all()
    overdue_invoices = qbo.get_invoices(db, aging_days=30)
    upcoming_bills = qbo.get_bills(db, due_days=14)
    cash = sum(b.available_balance for b in balances)
    ar_total = sum(i["amount"] for i in overdue_invoices)
    ap_total = sum(b["amount"] for b in upcoming_bills)
    burn_rate = 10000.0  # Placeholder: Phase 3 historical calc
    runway_days = (cash + ar_total - ap_total) / (burn_rate / 30) if burn_rate else 0
    return {
        "runway_days": runway_days,
        "cash": cash,
        "ar_overdue": ar_total,
        "ap_due_soon": ap_total
    }
