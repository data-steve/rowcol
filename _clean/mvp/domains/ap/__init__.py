"""
AP (Bills) Domain Module for MVP

Provides rail-agnostic interfaces for bills operations.
"""

from .gateways import (
    Bill,
    ListBillsQuery,
    UpdateBillRequest,
    BillsGateway,
)

__all__ = [
    "Bill",
    "ListBillsQuery", 
    "UpdateBillRequest",
    "BillsGateway",
]
