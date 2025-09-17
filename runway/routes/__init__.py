from fastapi import APIRouter
from .onboarding import router as onboarding_router
from .tray import router as tray_router

# Note: auth, businesses, and users are included directly in main.py
# This router includes runway product routes
router = APIRouter()
router.include_router(onboarding_router)
router.include_router(tray_router)
