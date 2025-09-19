from fastapi import APIRouter
from . import bank_transaction

router = APIRouter(prefix="/api/v1/bank", tags=["Bank"])
router.include_router(bank_transaction.router)
