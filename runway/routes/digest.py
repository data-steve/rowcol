from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from runway.experiences.digest import DigestService

router = APIRouter(tags=['digest'])

@router.get('/businesses/{business_id}/digest')
async def get_business_digest(business_id: str, db: Session = Depends(get_db)):
    """Get runway digest data for a business (no email)"""
    digest_service = DigestService(db)
    
    try:
        digest_data = digest_service.calculate_runway(business_id)
        return {
            "success": True,
            "business_id": business_id,
            "digest_data": digest_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating digest: {str(e)}")

@router.post('/businesses/{business_id}/digest/send')
async def send_business_digest(business_id: str, db: Session = Depends(get_db)):
    """Generate and send digest email to business owner"""
    digest_service = DigestService(db)
    
    result = await digest_service.generate_and_send_digest(business_id)
    
    if result["success"]:
        return result
    else:
        status_code = 404 if "not found" in result.get("error", "").lower() else 500
        raise HTTPException(status_code=status_code, detail=result["error"])

@router.get('/businesses/{business_id}/digest/preview')
async def preview_digest(business_id: str, db: Session = Depends(get_db)):
    """Preview digest email HTML without sending"""
    digest_service = DigestService(db)
    
    result = digest_service.get_digest_preview(business_id)
    
    if result["success"]:
        return result
    else:
        status_code = 404 if "not found" in result.get("error", "").lower() else 500
        raise HTTPException(status_code=status_code, detail=result["error"])

@router.post('/digest/send-all')
async def send_all_digests(db: Session = Depends(get_db)):
    """Send digest emails to all businesses (admin/cron endpoint)"""
    digest_service = DigestService(db)
    
    result = await digest_service.send_digest_to_all_businesses()
    return result

@router.get('/digest/email-status')
async def get_email_provider_status():
    """Get status of email providers"""
    from runway.experiences.digest.email import EmailService
    
    email_service = EmailService()
    provider_status = email_service.get_provider_status()
    
    return {
        "providers": provider_status,
        "healthy_providers": sum(1 for status in provider_status.values() if status),
        "total_providers": len(provider_status)
    }
