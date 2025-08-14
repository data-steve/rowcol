"""
Consolidated router for all Escher API routes.
This centralizes route registration and keeps main.py clean.
"""
from fastapi import APIRouter
from . import (
    engagements, services, tasks, correction, suggestion, 
    policy_profile, document_type, user, firm, client, staff, 
    business_entity, engagement_entities, automation, ingest, 
    csv, documents, review, kpi, ar, bank,   
)

# Create main router
router = APIRouter()

# Include all route modules
router.include_router(engagements.router)
router.include_router(services.router)
router.include_router(tasks.router)
router.include_router(correction.router)
router.include_router(suggestion.router)
router.include_router(policy_profile.router)
router.include_router(document_type.router)
router.include_router(user.router)
router.include_router(firm.router)
router.include_router(client.router)
router.include_router(staff.router)
router.include_router(business_entity.router)
router.include_router(engagement_entities.router)
router.include_router(automation.router)
router.include_router(ingest.router)
router.include_router(csv.router)
router.include_router(documents.router)
router.include_router(review.router)
router.include_router(kpi.router)
router.include_router(ar.router)
router.include_router(bank.router)
