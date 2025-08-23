from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.policy.services.rule import RuleService
from domains.policy.schemas.rule import Rule
from database import get_db

router = APIRouter(prefix="/api", tags=["Rules"])

@router.post("/rules", response_model=Rule)
async def create_rule(rule: Rule, db: Session = Depends(get_db)):
    service = RuleService(db)
    return service.create_rule(rule)

@router.get("/rules/{rule_id}", response_model=Rule)
async def get_rule(rule_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = RuleService(db)
    try:
        return service.get_rule(rule_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))