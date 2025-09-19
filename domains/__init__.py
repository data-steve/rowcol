"""
Top-level domains module for domain organization.
Imports all models to ensure SQLAlchemy registration.
"""
from fastapi import APIRouter

# Import all models for SQLAlchemy registration
from .core import models as core_models
from .ap import models as ap_models
from .ar import models as ar_models
from .bank import models as bank_models

# Import all routes
from .core.routes import router as core_router
from .ap.routes import router as ap_router
from .ar.routes import router as ar_router
from .bank.routes import router as bank_router
from .vendor_normalization.routes import router as vendor_normalization_router
from .policy.routes import router as policy_router

router = APIRouter()

router.include_router(core_router, prefix="/api/core", tags=["core"])
router.include_router(ap_router, tags=["ap"])  # AP has its own /api/ingest/ap prefix
router.include_router(ar_router, prefix="/api/ar", tags=["ar"])
router.include_router(bank_router, prefix="/bank", tags=["bank"])
router.include_router(vendor_normalization_router, prefix="/vendor_normalization", tags=["vendor_normalization"])
router.include_router(policy_router, prefix="/policy", tags=["policy"])