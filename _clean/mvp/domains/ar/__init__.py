"""
AR (Invoices) Domain Module for MVP

Provides rail-agnostic interfaces for invoices operations.
"""

from .gateways import (
    Invoice,
    ListInvoicesQuery,
    UpdateInvoiceRequest,
    InvoicesGateway,
)

__all__ = [
    "Invoice",
    "ListInvoicesQuery",
    "UpdateInvoiceRequest", 
    "InvoicesGateway",
]
