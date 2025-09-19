from fastapi import APIRouter
from . import invoices, payments

router = APIRouter(tags=["AR"])
router.include_router(invoices.router)
router.include_router(payments.router)
