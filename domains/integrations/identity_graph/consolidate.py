# domains/identity_graph/consolidate.py
from sqlalchemy.orm import Session

def consolidate_payout_settlement(db: Session, company_id: str, payout_identity_id: str, settlement_identity_id: str, net_cents: int, posted_at_iso: str):
    # count once at bank date
    from .services import write_ledger
    write_ledger(db, company_id, settlement_identity_id, posted_at_iso, "INFLOW", net_cents,
                 provenance={"edges":[{"from": payout_identity_id, "to": settlement_identity_id, "kind": "SETTLES"}],
                             "rule":"count_once_at_bank"})
