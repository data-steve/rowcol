from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from domains.core.models.business import Business
from domains.core.schemas.business import BusinessCreate, BusinessUpdate, Business as BusinessSchema

router = APIRouter(prefix='/runway', tags=['businesses'])

@router.post('/businesses/', response_model=BusinessSchema)
def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    """Create a new business"""
    db_business = Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

@router.get('/businesses/{business_id}', response_model=BusinessSchema)
def get_business(business_id: str, db: Session = Depends(get_db)):
    """Get business by ID"""
    business = db.query(Business).filter(Business.business_id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put('/businesses/{business_id}', response_model=BusinessSchema)
def update_business(business_id: str, business_update: BusinessUpdate, db: Session = Depends(get_db)):
    """Update business profile"""
    business = db.query(Business).filter(Business.business_id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    for field, value in business_update.dict(exclude_unset=True).items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    return business

@router.get('/businesses/{business_id}/digest')
def get_business_digest(business_id: str, db: Session = Depends(get_db)):
    """Generate weekly runway digest for business"""
    from runway.digest.services.digest import DigestService
    
    digest_service = DigestService(db)
    try:
        digest_data = digest_service.calculate_runway(business_id)
        return digest_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
