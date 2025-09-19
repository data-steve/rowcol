from __future__ import annotations
from sqlalchemy import Column, Text, Integer, Float
try:
    # Prefer your shared Base if present
    from domains.core.models.base import Base
except Exception:
    # Fallback Base to allow imports in isolation
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

class RawEvent(Base):
    __tablename__ = "raw_event"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    src = Column(Text, nullable=False)           # 'PLAID','STRIPE','JOBBERPAY','SQUARE','JOBBER'
    kind = Column(Text, nullable=False)          # 'BANK_TXN','PAYOUT','BAL_TXN','OPS_PAYMENT','OPS_INVOICE'
    external_id = Column(Text, nullable=False)
    occurred_at = Column(Text, nullable=False)   # ISO8601
    amount_cents = Column(Integer, nullable=False)
    currency = Column(Text, default="USD")
    account_ref = Column(Text)
    counterparty = Column(Text)
    mcc = Column(Text)
    parent_external_id = Column(Text)
    raw_json = Column(Text, nullable=False)

class Identity(Base):
    __tablename__ = "identity"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    fingerprint = Column(Text, nullable=False)
    canonical_kind = Column(Text, nullable=False)  # 'SETTLEMENT','PAYOUT','CHARGE','FEE','REFUND','INVOICE','PAYMENT'

class IdentityLink(Base):
    __tablename__ = "identity_link"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    identity_id = Column(Text, nullable=False)
    raw_event_id = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)

class IdentityEdge(Base):
    __tablename__ = "identity_edge"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    from_identity = Column(Text, nullable=False)
    to_identity = Column(Text, nullable=False)
    kind = Column(Text, nullable=False)   # 'SETTLES','COMPOSED_OF','APPLIES_TO'
    weight = Column(Float, default=1.0)

class CashLedger(Base):
    __tablename__ = "cash_ledger"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    identity_id = Column(Text, nullable=False)
    posted_at = Column(Text, nullable=False)      # ISO8601
    direction = Column(Text, nullable=False)      # 'INFLOW'|'OUTFLOW'
    amount_cents = Column(Integer, nullable=False)
    currency = Column(Text, default="USD")
    cdm_key = Column(Text)                        # filled by policy adapter
    policy = Column(Text)                         # 'MUST_PAY'|'CAN_DELAY'|'DISCRETIONARY'
    confidence = Column(Float, nullable=False, default=1.0)
    provenance_json = Column(Text, nullable=False)

class RuleVersion(Base):
    __tablename__ = "rule_version"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    created_at = Column(Text)                     # set in service layer

class CdmRule(Base):
    __tablename__ = "cdm_rule"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    version_id = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)          # 'VENDOR','MCC','REGEX','ACCOUNT','SOURCE_KIND'
    predicate_json = Column(Text, nullable=False) # JSON string
    outcome_cdm_key = Column(Text, nullable=False)
    outcome_policy = Column(Text)                 # optional
    priority = Column(Integer, nullable=False, default=100)
    active = Column(Integer, nullable=False, default=1)  # 1=true

class ExceptionRow(Base):
    __tablename__ = "exception"
    id = Column(Text, primary_key=True)
    company_id = Column(Text, nullable=False, index=True)
    kind = Column(Text, nullable=False)           # 'AR_AMBIG','UNMAPPED','TIMING','NO_MATCH','GHOST_AR'
    status = Column(Text, nullable=False, default="open")
    context_json = Column(Text, nullable=False)
    created_at = Column(Text)
    resolved_at = Column(Text)