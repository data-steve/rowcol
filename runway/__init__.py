from fastapi import APIRouter
from .routes import router as base_runway_router
from .tray.routes import router as tray_router

router = APIRouter(prefix="/runway")
router.include_router(base_runway_router)
router.include_router(tray_router)
