from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from runway.onboarding.services.onboarding import OnboardingService
from typing import Dict, Any

router = APIRouter()

@router.post("/")
def qualify(business_data: dict, user_data: dict, db: Session = Depends(get_db)):
    service = OnboardingService(db)
    return service.qualify_onboarding(business_data, user_data)

@router.get("/{business_id}/status")
def get_onboarding_status(business_id: str, db: Session = Depends(get_db)):
    """Get comprehensive onboarding status including runway replay if available."""
    service = OnboardingService(db)
    return service.get_onboarding_status(business_id)

@router.get("/{business_id}/runway-replay")
def get_runway_replay(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get the runway replay data generated during QBO connection.
    
    Returns historical analysis showing what Oodaloo would have recommended
    over the past 4 weeks based on the business's QBO data.
    """
    service = OnboardingService(db)
    
    # Check if business has QBO integration with runway replay data
    from domains.core.models.integration import Integration
    integration = db.query(Integration).filter(
        Integration.business_id == business_id,
        Integration.platform == "qbo",
        Integration.status == "connected"
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=404, 
            detail="QBO integration not found or not connected"
        )
    
    if not integration.runway_replay_data:
        # Generate runway replay if it doesn't exist (for existing connections)
        replay_data = service.generate_runway_replay(business_id)
        integration.runway_replay_data = replay_data
        db.commit()
        return replay_data
    
    return integration.runway_replay_data

@router.get("/{business_id}/hygiene-score")
def get_hygiene_score(business_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get the hygiene score generated during QBO connection.
    
    Returns data quality analysis showing issues that affect runway accuracy
    and the potential runway impact of fixing them.
    """
    service = OnboardingService(db)
    
    # Check if business has QBO integration with runway replay data (which includes hygiene score)
    from domains.core.models.integration import Integration
    integration = db.query(Integration).filter(
        Integration.business_id == business_id,
        Integration.platform == "qbo",
        Integration.status == "connected"
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=404, 
            detail="QBO integration not found or not connected"
        )
    
    # Check if hygiene score exists in runway replay data
    if integration.runway_replay_data and "hygiene_score" in integration.runway_replay_data:
        return integration.runway_replay_data["hygiene_score"]
    
    # Generate hygiene score if it doesn't exist
    hygiene_score = service.generate_initial_hygiene_score(business_id)
    
    # Store it in the integration data
    if not integration.runway_replay_data:
        integration.runway_replay_data = {}
    integration.runway_replay_data["hygiene_score"] = hygiene_score
    db.commit()
    
    return hygiene_score

@router.post("/{business_id}/qbo/connect")
def start_qbo_connection(business_id: str, user_id: str, db: Session = Depends(get_db)):
    """Initiate QBO OAuth flow."""
    service = OnboardingService(db)
    return service.start_qbo_connection(business_id, user_id)

@router.post("/qbo/callback")
def complete_qbo_connection(state: str, code: str, realmId: str, db: Session = Depends(get_db)):
    """Complete QBO OAuth flow and generate runway replay."""
    service = OnboardingService(db)
    result = service.complete_qbo_connection(state, code, realmId)
    
    # Include runway replay data in response
    if result.get("status") == "connected":
        business_id = result.get("business_id")
        if business_id:
            try:
                replay_data = service.generate_runway_replay(business_id)
                result["runway_replay"] = replay_data
            except Exception as e:
                # Don't fail the connection if replay generation fails
                result["runway_replay_error"] = str(e)
    
    return result
