from fastapi import APIRouter
from . import vendor_canonical

router = APIRouter()
router.include_router(vendor_canonical.router)
