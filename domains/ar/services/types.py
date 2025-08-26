"""
Shared types and enums for AR reconciliation services.
"""
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class MatchConfidence(Enum):
    HIGH = 0.95
    MEDIUM = 0.75
    LOW = 0.50
    MANUAL_REVIEW = 0.25


class RevenueRecognitionMethod(Enum):
    CASH_BASIS = "cash"
    ACCRUAL_BASIS = "accrual"
    PERCENTAGE_COMPLETION = "percentage_completion"
    MILESTONE = "milestone"


@dataclass
class PaymentMatch:
    stripe_payment_id: str
    jobber_invoice_ids: List[str]
    job_ids: List[str]
    confidence: float
    match_type: str
    variance_amount: float
    variance_percentage: float
    requires_human_review: bool
    suggested_action: str
    allocated_fees: Dict[str, float]
    rationale: Dict[str, Any]


@dataclass
class RevenueRecognitionEntry:
    job_id: str
    period: str  # YYYY-MM
    work_performed_amount: float
    cash_received_amount: float
    variance_amount: float
    recognition_method: str
    journal_entries: List[Dict[str, Any]]
    requires_accrual: bool
    requires_deferral: bool
