"""
Runway Wiring - Composition Root for MVP

This module provides the composition root for dependency injection in the MVP.
It binds domain interfaces to infrastructure implementations and creates
service instances with proper dependencies.

Architecture: runway/ → domains/ → infra/ (no back edges)
"""

from typing import Dict, Any, Optional
import logging

# Domain interfaces
from mvp.domains.ap.gateways import BillsGateway, ListBillsQuery
from mvp.domains.ar.gateways import InvoicesGateway, ListInvoicesQuery  
from mvp.domains.bank.gateways import BalancesGateway, ListBalancesQuery

# Infrastructure implementations
from mvp.infra.gateways.qbo.bills_gateway import QBOBillsGateway
from mvp.infra.gateways.qbo.invoices_gateway import QBOInvoicesGateway
from mvp.infra.gateways.qbo.balances_gateway import QBOBalancesGateway
from mvp.infra.sync.orchestrator import SyncOrchestrator
from mvp.infra.repos.ap_repo import BillsMirrorRepo
from mvp.infra.repos.ar_repo import InvoicesMirrorRepo
from mvp.infra.repos.bank_repo import BalancesMirrorRepo
from mvp.infra.services.business_realm_service import business_realm_service

# Runway services
from mvp.runway.services.runway_orchestrator import RunwayOrchestrator

logger = logging.getLogger(__name__)

# Global instances for dependency injection
_sync_orchestrator: Optional[SyncOrchestrator] = None
_bills_repo: Optional[BillsMirrorRepo] = None
_invoices_repo: Optional[InvoicesMirrorRepo] = None
_balances_repo: Optional[BalancesMirrorRepo] = None

def _get_sync_orchestrator() -> SyncOrchestrator:
    """Get or create sync orchestrator instance."""
    global _sync_orchestrator
    if _sync_orchestrator is None:
        _sync_orchestrator = SyncOrchestrator()
        logger.info("Created SyncOrchestrator instance")
    return _sync_orchestrator

def _get_bills_repo() -> BillsMirrorRepo:
    """Get or create bills repository instance."""
    global _bills_repo
    if _bills_repo is None:
        _bills_repo = BillsMirrorRepo()
        logger.info("Created BillsMirrorRepo instance")
    return _bills_repo

def _get_invoices_repo() -> InvoicesMirrorRepo:
    """Get or create invoices repository instance."""
    global _invoices_repo
    if _invoices_repo is None:
        _invoices_repo = InvoicesMirrorRepo()
        logger.info("Created InvoicesMirrorRepo instance")
    return _invoices_repo

def _get_balances_repo() -> BalancesMirrorRepo:
    """Get or create balances repository instance."""
    global _balances_repo
    if _balances_repo is None:
        _balances_repo = BalancesMirrorRepo()
        logger.info("Created BalancesMirrorRepo instance")
    return _balances_repo

def create_bills_gateway(advisor_id: str, business_id: str) -> BillsGateway:
    """
    Create bills gateway with QBO implementation.
    
    Automatically resolves realm_id from business_id using BusinessRealmService.
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        
    Returns:
        BillsGateway implementation
    """
    realm_id = business_realm_service.get_realm_id(business_id)
    sync_orchestrator = _get_sync_orchestrator()
    bills_repo = _get_bills_repo()
    
    return QBOBillsGateway(
        advisor_id=advisor_id,
        business_id=business_id,
        realm_id=realm_id,
        sync_orchestrator=sync_orchestrator,
        bills_repo=bills_repo
    )

def create_invoices_gateway(advisor_id: str, business_id: str) -> InvoicesGateway:
    """
    Create invoices gateway with QBO implementation.
    
    Automatically resolves realm_id from business_id using BusinessRealmService.
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        
    Returns:
        InvoicesGateway implementation
    """
    realm_id = business_realm_service.get_realm_id(business_id)
    sync_orchestrator = _get_sync_orchestrator()
    invoices_repo = _get_invoices_repo()
    
    return QBOInvoicesGateway(
        advisor_id=advisor_id,
        business_id=business_id,
        realm_id=realm_id,
        sync_orchestrator=sync_orchestrator,
        invoices_repo=invoices_repo
    )

def create_balances_gateway(advisor_id: str, business_id: str) -> BalancesGateway:
    """
    Create balances gateway with QBO implementation.
    
    Automatically resolves realm_id from business_id using BusinessRealmService.
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        
    Returns:
        BalancesGateway implementation
    """
    realm_id = business_realm_service.get_realm_id(business_id)
    sync_orchestrator = _get_sync_orchestrator()
    balances_repo = _get_balances_repo()
    
    return QBOBalancesGateway(
        advisor_id=advisor_id,
        business_id=business_id,
        realm_id=realm_id,
        sync_orchestrator=sync_orchestrator,
        balances_repo=balances_repo
    )

def create_runway_orchestrator(advisor_id: str, business_id: str, realm_id: str) -> RunwayOrchestrator:
    """
    Create runway orchestrator with all gateways.
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        realm_id: QBO realm identifier
        
    Returns:
        RunwayOrchestrator instance
    """
    bills_gateway = create_bills_gateway(advisor_id, business_id, realm_id)
    invoices_gateway = create_invoices_gateway(advisor_id, business_id, realm_id)
    balances_gateway = create_balances_gateway(advisor_id, business_id, realm_id)
    
    return RunwayOrchestrator(
        bills_gateway=bills_gateway,
        invoices_gateway=invoices_gateway,
        balances_gateway=balances_gateway
    )

def create_tray_service(advisor_id: str, business_id: str) -> 'TrayService':
    """
    Create tray service for hygiene and data quality management.
    
    Uses domain gateways with filtering methods instead of data orchestrators:
    - BillsGateway.list_incomplete() for bills with missing data
    - InvoicesGateway.list_incomplete() for invoices with missing data
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        realm_id: QBO realm identifier
        
    Returns:
        TrayService instance
    """
    bills_gateway = create_bills_gateway(advisor_id, business_id)
    invoices_gateway = create_invoices_gateway(advisor_id, business_id)
    
    # Import here to avoid circular dependencies
    from mvp.runway.services.tray_service import TrayService
    
    return TrayService(
        advisor_id=advisor_id,
        business_id=business_id,
        realm_id=business_realm_service.get_realm_id(business_id),
        bills_gateway=bills_gateway,
        invoices_gateway=invoices_gateway
    )

def create_console_service(advisor_id: str, business_id: str) -> 'ConsoleService':
    """
    Create console service for insights and recommendations.
    
    Uses domain gateways with filtering methods instead of data orchestrators:
    - BillsGateway.list_payment_ready() for bills ready for payment scheduling
    - InvoicesGateway.list_collections_ready() for invoices needing collections attention
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        realm_id: QBO realm identifier
        
    Returns:
        ConsoleService instance
    """
    bills_gateway = create_bills_gateway(advisor_id, business_id)
    invoices_gateway = create_invoices_gateway(advisor_id, business_id)
    balances_gateway = create_balances_gateway(advisor_id, business_id)
    
    # Import here to avoid circular dependencies
    from mvp.runway.services.console_service import ConsoleService
    
    return ConsoleService(
        advisor_id=advisor_id,
        business_id=business_id,
        realm_id=business_realm_service.get_realm_id(business_id),
        bills_gateway=bills_gateway,
        invoices_gateway=invoices_gateway,
        balances_gateway=balances_gateway
    )

def create_digest_service(advisor_id: str, business_id: str) -> 'DigestService':
    """
    Create digest service for weekly summaries and insights.
    
    Consumes Tray + Console outputs instead of pulling raw data:
    - Uses TrayService for incomplete data metrics
    - Uses ConsoleService for decision-ready data metrics
    - No direct QBO calls (follows solutioning design)
    
    Args:
        advisor_id: Advisor identifier (primary key)
        business_id: Business identifier (foreign key)
        realm_id: QBO realm identifier
        
    Returns:
        DigestService instance
    """
    tray_service = create_tray_service(advisor_id, business_id)
    console_service = create_console_service(advisor_id, business_id)
    
    # Import here to avoid circular dependencies
    from mvp.runway.services.digest_service import DigestService
    
    return DigestService(
        advisor_id=advisor_id,
        business_id=business_id,
        realm_id=business_realm_service.get_realm_id(business_id),
        tray_service=tray_service,
        console_service=console_service
    )

def reset_dependencies():
    """Reset all global dependencies (useful for testing)."""
    global _sync_orchestrator, _bills_repo, _invoices_repo, _balances_repo
    _sync_orchestrator = None
    _bills_repo = None
    _invoices_repo = None
    _balances_repo = None
    logger.info("Reset all dependency instances")
