"""
Core Domain Routes

This module exports all core domain routes including:
- Business entity management
- User management  
- Document management
- Audit logging
- Sync operations
"""

from fastapi import APIRouter
from .business import router as business_router
from .user import router as user_router
from .documents import router as documents_router
from .document_type import router as document_type_router
# from .sync import router as sync_router  # Moved to infra/api/routes/


router = APIRouter()
router.include_router(business_router)
router.include_router(user_router)
router.include_router(documents_router)
router.include_router(document_type_router)
# router.include_router(sync_router)  # Moved to infra/api/routes/
