# domains/identity_graph/services.py
from typing import Dict, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import uuid
import json
import hashlib

def _uuid() -> str: return str(uuid.uuid4())

def sha256(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts: h.update(p.encode("utf-8"))
    return h.hexdigest()

@dataclass
class RawEvent:
    id: str; company_id: str; src: str; kind: str; external_id: str
    occurred_at: str; amount_cents: int; currency: str = "USD"
    account_ref: Optional[str] = None; counterparty: Optional[str] = None
    mcc: Optional[str] = None; parent_external_id: Optional[str] = None
    raw_json: str = "{}"

CANON = ("SETTLEMENT","PAYOUT","CHARGE","FEE","REFUND","INVOICE","PAYMENT")

def fingerprint(kind: str, provider: str, **kw) -> str:
    # mirrors spec; settle uses (account, abs(amount), date, merchant_norm)
    if kind == "SETTLEMENT":
        return sha256("SETTLEMENT", kw["account_id"], str(abs(kw["amount_cents"])),
                      kw["posted_date"], (kw.get("merchant_norm") or ""))
    if kind in ("PAYOUT","CHARGE","FEE","REFUND"):
        return sha256(kind, provider, kw["external_id"])
    if kind in ("INVOICE","PAYMENT"):
        return sha256(kind, provider, kw["external_id"])
    return sha256("UNKNOWN", provider, kw.get("external_id",""))

def upsert_identity(db: Session, company_id: str, canonical_kind: str, fp: str) -> str:
    # replace with SQLAlchemy upsert; return identity.id
    row = db.execute(
        "SELECT id FROM identity WHERE company_id=? AND fingerprint=?", (company_id, fp)
    ).fetchone()
    if row: return row[0]
    new_id = _uuid()
    db.execute(
        "INSERT INTO identity(id,company_id,fingerprint,canonical_kind) VALUES(?,?,?,?)",
        (new_id, company_id, fp, canonical_kind)
    )
    return new_id

def link_raw(db: Session, company_id: str, identity_id: str, raw_event_id: str, reason: str, conf: float = 1.0):
    db.execute(
        "INSERT INTO identity_link(id,company_id,identity_id,raw_event_id,confidence,reason) VALUES(?,?,?,?,?,?)",
        (_uuid(), company_id, identity_id, raw_event_id, conf, reason)
    )

def add_edge(db: Session, company_id: str, from_id: str, to_id: str, kind: str, weight: float = 1.0):
    db.execute(
        "INSERT INTO identity_edge(id,company_id,from_identity,to_identity,kind,weight) VALUES(?,?,?,?,?,?)",
        (_uuid(), company_id, from_id, to_id, kind, weight)
    )

def write_ledger(db: Session, company_id: str, identity_id: str, posted_at: str,
                 direction: str, amount_cents: int, provenance: Dict, currency: str = "USD"):
    db.execute(
        "INSERT INTO cash_ledger(id,company_id,identity_id,posted_at,direction,amount_cents,currency,provenance_json,confidence) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (_uuid(), company_id, identity_id, posted_at, direction, amount_cents, currency, json.dumps(provenance), 1.0)
    )
