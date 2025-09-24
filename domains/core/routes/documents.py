# PARKED: Document management routes are out of scope for Oodaloo cash runway focus
# These routes depend on DocumentManagementService which was removed for Phase 1-3
# TODO: Phase 4+ - Evaluate if document management is needed for Oodaloo
# - Do business owners need document storage beyond QBO attachments?
# - Should this integrate with existing cloud storage (Google Drive, Dropbox)?
# - What's the simplest UX for document categorization?

from fastapi import APIRouter

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# All document routes parked for Phase 4+ evaluation
