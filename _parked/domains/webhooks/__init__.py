from fastapi import APIRouter
from .routes import router as webhook_router

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])
router.include_router(webhook_router)