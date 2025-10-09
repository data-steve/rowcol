"""
A/R Execution Services - Parked for Future Stripe Implementation

These services contain execution methods that were moved from
domains/ar/services/invoice.py to maintain QBO-honest architecture.

QBO is only a ledger rail - it cannot create invoices.
These services will be implemented by Stripe when invoice creation is enabled.
"""

from .invoice_management_service import InvoiceManagementService

__all__ = [
    'InvoiceManagementService',
]
