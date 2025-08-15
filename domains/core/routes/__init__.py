"""
Consolidated router for all Escher API routes.
This centralizes route registration and keeps main.py clean.
"""
# This code snippet is importing the necessary modules and routers for setting up API routes using
# FastAPI framework in Python. Here's a breakdown of the imports:
from fastapi import APIRouter

from ...ap.routes import ingest
from . import (
    engagements, services, tasks, correction, suggestion, 
    policy_profile, document_type, user, firm, client, staff, 
    business_entity, engagement_entities, automation, csv, documents, review, kpi
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
# AR, Bank, and Payroll routes are now handled by their respective domains