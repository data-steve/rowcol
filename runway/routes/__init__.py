"""
Consolidated runway routes - orchestrates all product-level API endpoints.

This module follows the cascading import pattern:
- Individual domain routes are imported and consolidated here
- main.py imports only from this consolidated router
- Maintains clean separation between product (runway/) and domain (domains/) APIs
"""

from fastapi import APIRouter

# Import all runway module routers
from ..auth.routes.auth import router as auth_router
from ..auth.routes.users import router as users_router
from ..digest.routes.digest import router as digest_router
from ..reserves.routes.reserves import router as reserves_router
from ..ap.routes.bills import router as ap_bills_router
from ..ap.routes.payments import router as ap_payments_router
from ..ap.routes.vendors import router as ap_vendors_router
from ..ar.routes.collections import router as ar_collections_router
from ..ar.routes.invoices import router as ar_invoices_router
from ..analytics.routes.kpis import router as analytics_kpis_router
from ..onboarding.routes.onboarding import router as onboarding_router
from ..tray.routes.tray import router as tray_router

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

# AP routes
router.include_router(ap_bills_router, prefix="/ap")
router.include_router(ap_payments_router, prefix="/ap")
router.include_router(ap_vendors_router, prefix="/ap")

# AR routes
router.include_router(ar_collections_router, prefix="/ar")
router.include_router(ar_invoices_router, prefix="/ar")

# Analytics routes
router.include_router(analytics_kpis_router, prefix="/analytics")
