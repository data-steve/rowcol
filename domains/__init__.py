"""
Top-level domains module that consolidates all domain routers.
This allows main.py to import a single router that includes all domains.
"""
from fastapi import APIRouter

# Import routers from each domain
from .core.routes import router as core_router
from .ap.routes import router as ap_router
from .ar.routes import router as ar_router
from .bank.routes import router as bank_router
from .payroll.routes import router as payroll_router
from .close.routes import router as close_router
from .webhooks.routes import router as webhook_router

# Create main consolidated router
router = APIRouter()

# Include all domain routers
router.include_router(core_router)
router.include_router(ap_router)
router.include_router(ar_router)
router.include_router(bank_router)
router.include_router(payroll_router)
router.include_router(close_router)
router.include_router(webhook_router)

# Import models from each domain (for global access if needed)
from .core.models import *
from .ap.models import *
from .ar.models import *
from .bank.models import *
from .payroll.models import *
# Note: Close domain has no models yet
