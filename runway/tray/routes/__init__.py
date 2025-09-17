from fastapi import APIRouter
from . import tray

router = APIRouter()
router.include_router(tray.router)