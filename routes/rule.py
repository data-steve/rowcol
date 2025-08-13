from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.rule import Rule as RuleModel
from schemas.rule import Rule
from database import get_db

router = APIRouter(prefix="/api", tags=["Rules"])

@router.post("/rules", response_model=Rule)
async def create_rule(rule: Rule, db: Session = Depends(get_db)):
    db_rule = RuleModel(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/rules/{rule_id}", response_model=Rule)
async def get_rule(rule_id: int, firm_id: str, db: Session = Depends(get_db)):
    rule = db.query(RuleModel).filter(RuleModel.rule_id == rule_id, RuleModel.firm_id == firm_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule