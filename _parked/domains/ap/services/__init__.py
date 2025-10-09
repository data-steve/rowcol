"""
A/P Execution Services - Parked for Future Ramp Implementation

These services contain execution methods that were moved from
domains/ap/services/bill.py to maintain QBO-honest architecture.

QBO is only a ledger rail - it cannot execute payments.
These services will be implemented by Ramp when payment execution is enabled.
"""

from .bill_payment_service import BillPaymentService

__all__ = [
    'BillPaymentService',
]
