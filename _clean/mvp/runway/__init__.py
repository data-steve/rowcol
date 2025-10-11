"""
Runway Package - Business Logic Layer

This package contains the business logic layer that orchestrates domain gateways
to provide product features. It follows the architecture pattern:
runway/ → domains/ → infra/ (no back edges)
"""

from .wiring import (
    create_bills_gateway,
    create_invoices_gateway,
    create_balances_gateway,
    create_runway_orchestrator,
    create_tray_service,
    create_console_service,
    create_digest_service,
    reset_dependencies
)

from .services.runway_orchestrator import RunwayOrchestrator
from .services.tray_service import TrayService
from .services.console_service import ConsoleService
from .services.digest_service import DigestService

__all__ = [
    # Wiring functions
    "create_bills_gateway",
    "create_invoices_gateway", 
    "create_balances_gateway",
    "create_runway_orchestrator",
    "create_tray_service",
    "create_console_service",
    "create_digest_service",
    "reset_dependencies",
    
    # Service classes
    "RunwayOrchestrator",
    "TrayService",
    "ConsoleService", 
    "DigestService"
]
