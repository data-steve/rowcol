"""
Runway module - Product orchestration layer for Oodaloo.

Consolidates all product-level APIs and workflows.
Follows cascading import pattern for clean main.py integration.

Architecture: Data Orchestrators → Calculators → Experiences
- 0_data_orchestrators: Data pulling and state management
- 1_calculators: Pure business logic calculations
- 2_experiences: User-facing experience services
"""

from fastapi import APIRouter

# Import all models for SQLAlchemy registration
from .models import runway_reserve
from .models import tray_item

from .routes import router as runway_routes_router

# Export the consolidated runway router
router = runway_routes_router
