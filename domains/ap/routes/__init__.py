"""
Consolidated router for AP domain routes.
This centralizes AP route registration.
"""
from fastapi import APIRouter
from . import vendor_canonical, ingest

# Create AP domain router
router = APIRouter(prefix="/api/ap", tags=["AP"])

# Include all AP route modules
router.include_router(vendor_canonical.router)
router.include_router(ingest.router)
