"""
Consolidated router for Tray domain routes.
"""
from fastapi import APIRouter

router = APIRouter(tags=["Tray"])
from .routes.tray import router as tray_router
router.include_router(tray_router)
