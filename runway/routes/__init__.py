"""
Consolidated runway routes - orchestrates all product-level API endpoints.

This module follows the cascading import pattern:
- Individual domain routes are imported and consolidated here
- main.py imports only from this consolidated router
- Maintains clean separation between product (runway/) and domain (domains/) APIs
"""

from fastapi import APIRouter

# Import all runway module routers
from .auth import router as auth_router
from .users import router as users_router
from .digest import router as digest_router
from .reserve_runway import router as reserves_router
from .bills import router as ap_bills_router
from .payments import router as ap_payments_router
from .vendors import router as ap_vendors_router
from .collections import router as ar_collections_router
from .invoices import router as ar_invoices_router
# KPIs route removed - QBO has built-in KPIs
from .onboarding import router as onboarding_router
from .tray import router as tray_router
from .test_drive import router as test_drive_router

# Import QBO setup routes
from .qbo_setup import router as qbo_setup_router

# Create consolidated runway router with /api/v1 prefix
router = APIRouter(prefix="/api/v1")

# Include all runway routes with standardized prefixes
router.include_router(auth_router, prefix="/auth")
router.include_router(users_router, prefix="/users")
router.include_router(digest_router, prefix="/digest")

# Runway-specific routes
router.include_router(reserves_router, prefix="/runway")
router.include_router(onboarding_router, prefix="/onboarding")
router.include_router(tray_router, prefix="/tray")
router.include_router(test_drive_router, prefix="/test-drive")

# AP routes
router.include_router(ap_bills_router, prefix="/ap")
router.include_router(ap_payments_router, prefix="/ap")
router.include_router(ap_vendors_router, prefix="/ap")

# AR routes
router.include_router(ar_collections_router, prefix="/ar")
router.include_router(ar_invoices_router, prefix="/ar")

# Analytics routes removed - QBO has built-in KPIs

# QBO setup infrastructure routes
router.include_router(qbo_setup_router, prefix="/infrastructure")
