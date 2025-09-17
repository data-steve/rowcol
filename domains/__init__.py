"""
Top-level domains module for domain organization.
"""
from fastapi import APIRouter
from .core.routes import router as core_router
from .ap.routes import router as ap_router
from .ar.routes import router as ar_router
from .bank.routes import router as bank_router
from .vendor_normalization.routes import router as vendor_normalization_router
from .policy.routes import router as policy_router

router = APIRouter(prefix="/api/v1")

router.include_router(core_router, prefix="/core", tags=["core"])
router.include_router(ap_router, prefix="/ap", tags=["ap"])
router.include_router(ar_router, prefix="/ar", tags=["ar"])
router.include_router(bank_router, prefix="/bank", tags=["bank"])
router.include_router(vendor_normalization_router, prefix="/vendor_normalization", tags=["vendor_normalization"])
router.include_router(policy_router, prefix="/policy", tags=["policy"])