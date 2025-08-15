"""
Consolidated router for Payroll domain routes.
This centralizes Payroll route registration.
"""
from fastapi import APIRouter

# Create Payroll domain router
router = APIRouter(prefix="/api/payroll", tags=["Payroll"])

# Import and include payroll routes
from . import payroll

# Include all payroll route modules
router.include_router(payroll.router)
