"""
Preamble: Consolidated router for Close domain routes in Stage 2.
References: Stage 2 requirements.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/close", tags=["Close"])

from . import preclose, portal

router.include_router(preclose.router)
router.include_router(portal.router)
