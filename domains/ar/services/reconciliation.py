"""
Bundled AR Matching Engine for Service Contractors - V3

This file acts as the main orchestrator for the accounts receivable reconciliation process.
It coordinates the distinct steps of cash reconciliation and revenue recognition.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from enum import Enum

# Import the new dedicated services
from .cash_reconciliation import CashReconciliationService
from .types import MatchConfidence, PaymentMatch
# Disabled: RevenueRecognitionService, SharedExpenseAllocationService - not core ServicePro features


# --- Main Orchestrator Service ---

class ReconciliationService:
    """
    Orchestrates the end-to-end AR reconciliation process by calling
    specialized services for cash matching and revenue recognition.
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Instantiate the specialized services
        self.cash_reconciliation_service = CashReconciliationService(db)
        # Disabled: revenue_recognition_service, shared_expense_service - not core ServicePro features
    
    def process_bundled_ar_matching(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point that runs the full reconciliation workflow.
        """
        jobs = test_data["jobs"]
        invoices = test_data["invoices"]
        stripe_payments = test_data["stripe_payments"]
        qbo_transactions = test_data["qbo_transactions"]
        
        # Step 1: Perform cash reconciliation to match payments with invoices.
        payment_matches = self.cash_reconciliation_service.match_payments_to_invoices(stripe_payments, invoices)
        
        # Step 2 (Future): Allocate fees based on the successful matches.
        # payment_matches = self.allocate_stripe_fees(payment_matches, jobs)
        
        # Step 3: SKIP revenue recognition - not needed for ServicePro core mission
        revenue_entries = []  # Skip revenue recognition for now
        
        # Step 4: SKIP shared expenses - future feature, not core ServicePro
        shared_expenses = []  # Skip shared expenses for now
        
        # Step 5: Generate the final summary report.
        reconciliation_summary = self._generate_reconciliation_summary(payment_matches, revenue_entries, shared_expenses)
        
        return {
            "payment_matches": [self._match_to_dict(m) for m in payment_matches],
            "revenue_recognition_entries": [self._revenue_entry_to_dict(r) for r in revenue_entries],
            "shared_expense_allocations": shared_expenses,
            "reconciliation_summary": reconciliation_summary,
            "requires_human_review": self._calculate_human_review_needed(payment_matches, revenue_entries)
        }

    def _generate_reconciliation_summary(self, matches: List[PaymentMatch], 
                                      revenue_entries: List,
                                      shared_expenses: List[Dict]) -> Dict[str, Any]:
        """Generates a high-level summary of the reconciliation results."""
        total_matches = len(matches)
        high_confidence_matches = len([m for m in matches if m.confidence >= 0.90])
        requires_review = len([m for m in matches if m.requires_human_review])
        
        return {
            "matching_summary": {
                "total_payments": total_matches,
                "high_confidence_matches": high_confidence_matches,
                "requires_human_review": requires_review,
                "match_rate_percentage": (high_confidence_matches / total_matches * 100) if total_matches > 0 else 0
            },
            "revenue_recognition_summary": {
                "total_entries": len(revenue_entries),
                "requires_accrual": len([e for e in revenue_entries if e.requires_accrual]),
                "requires_deferral": len([e for e in revenue_entries if e.requires_deferral]),
                "total_variance": sum(entry.variance_amount for entry in revenue_entries)
            },
            "shared_expense_summary": {
                "total_shared_expenses": len(shared_expenses),
                "total_amount_to_allocate": sum(exp["total_amount"] for exp in shared_expenses)
            }
        }
    
    def _calculate_human_review_needed(self, matches: List[PaymentMatch], 
                                     revenue_entries: List) -> bool:
        """Determines if the overall results warrant manual review."""
        if any(match.requires_human_review for match in matches):
            return True
        if any(abs(entry.variance_amount) > 1000 for entry in revenue_entries):
            return True
        return False
    
    # --- Data Conversion Helpers for JSON serialization ---
    
    def _match_to_dict(self, match: PaymentMatch) -> Dict[str, Any]:
        """Converts PaymentMatch dataclass to a dictionary."""
        return {
            "stripe_payment_id": match.stripe_payment_id,
            "jobber_invoice_ids": match.jobber_invoice_ids,
            "job_ids": match.job_ids,
            "confidence": match.confidence,
            "match_type": match.match_type,
            "variance_amount": match.variance_amount,
            "variance_percentage": match.variance_percentage,
            "requires_human_review": match.requires_human_review,
            "suggested_action": match.suggested_action,
            "rationale": match.rationale
        }
