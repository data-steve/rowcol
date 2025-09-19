from fastapi import APIRouter
from .ingest import router as ingest_router

router = APIRouter(prefix="/api/ingest/ap", tags=["AP"])
router.include_router(ingest_router)
