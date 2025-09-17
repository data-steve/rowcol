from fastapi import APIRouter

from . import automation, document_type, documents, sync, user

router = APIRouter()

router.include_router(automation.router, prefix="/automation", tags=["automation"])
router.include_router(document_type.router, prefix="/document_types", tags=["document_types"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(sync.router, prefix="/sync", tags=["sync"])
router.include_router(user.router, prefix="/users", tags=["users"])
