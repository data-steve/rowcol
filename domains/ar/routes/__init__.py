"""
Consolidated router for AR domain routes.
This centralizes AR route registration.
"""
from fastapi import APIRouter

# Create AR domain router
router = APIRouter(prefix="/api/ar", tags=["AR"])

# Import and include AR routes
from . import credits, invoices, collections, payments

# Include all AR route modules
router.include_router(credits.router)
router.include_router(invoices.router)
router.include_router(collections.router)
router.include_router(payments.router)
