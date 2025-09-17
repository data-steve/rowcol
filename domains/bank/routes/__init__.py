from fastapi import APIRouter
from . import bank

router = APIRouter(prefix="/api/v1/bank", tags=["Bank"])
router.include_router(bank.router)
