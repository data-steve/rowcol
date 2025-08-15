"""
Consolidated router for Bank domain routes.
This centralizes Bank route registration.
"""
from fastapi import APIRouter

# Create Bank domain router
router = APIRouter(prefix="/api/bank", tags=["Bank"])

# Import and include bank routes
from . import bank

# Include all bank route modules
router.include_router(bank.router)
