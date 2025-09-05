"""
Consolidated router for Tray domain routes.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/tray", tags=["Tray"])
from .routes.tray import router as tray_router
router.include_router(tray_router)
