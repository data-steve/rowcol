"""
Runway module - Product orchestration layer for Oodaloo.

Consolidates all product-level APIs and workflows.
Follows cascading import pattern for clean main.py integration.
"""

from fastapi import APIRouter

# Import all models for SQLAlchemy registration
from .reserves import models as reserves_models
from .tray import models as tray_models

from .routes import router as runway_routes_router

# Export the consolidated runway router
router = runway_routes_router
