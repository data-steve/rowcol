"""
QBO Setup API Routes

Handles QBO connection setup endpoints as infrastructure,
separate from the onboarding user experience.

These routes handle the technical setup process of connecting to QBO,
including OAuth flow, connection manager establishment, and health verification.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from db.session import get_db
from runway.infrastructure.qbo_setup.qbo_setup_service import QBOSetupService

router = APIRouter(prefix="/qbo-setup", tags=["qbo-setup"])

@router.post("/{business_id}/connect")
def start_qbo_connection(business_id: str, user_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Initiate QBO OAuth flow for first-time connection setup.
    
    This endpoint starts the QBO connection process by initiating the OAuth flow.
    The user will be redirected to QBO to authorize the connection.
    """
    service = QBOSetupService(db)
    return service.start_qbo_connection(business_id, user_id)

@router.post("/callback")
async def complete_qbo_connection(state: str, code: str, realm_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Complete QBO OAuth flow and establish full connection infrastructure.
    
    This endpoint completes the QBO connection process by:
    1. Exchanging the authorization code for access tokens
    2. Establishing the QBO connection manager
    3. Generating test drive data
    4. Verifying connection health
    
    Returns comprehensive setup results including test drive data.
    """
    service = QBOSetupService(db)
    return await service.complete_qbo_connection(state, code, realm_id)

@router.get("/{business_id}/status")
def get_qbo_connection_status(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive QBO connection status including connection manager health.
    
    Returns detailed status information including:
    - Basic connection status
    - Connection manager health
    - Token status
    - Infrastructure status
    """
    service = QBOSetupService(db)
    return service.get_qbo_connection_status(business_id)

@router.get("/{business_id}/health")
def verify_connection_health(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Verify QBO connection health and test API connectivity.
    
    This endpoint performs a comprehensive health check including:
    - Connection manager status
    - API connectivity test
    - Token validity check
    """
    service = QBOSetupService(db)
    return service.verify_connection_health(business_id)

@router.delete("/{business_id}/disconnect")
def disconnect_qbo(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Disconnect QBO integration and clean up connection manager.
    
    This endpoint:
    1. Disconnects the QBO integration
    2. Cleans up the connection manager
    3. Removes stored tokens and credentials
    """
    service = QBOSetupService(db)
    return service.disconnect_qbo(business_id)
