from sqlalchemy.orm import Session
from models.rule import Rule as RuleModel
from schemas.rule import Rule
from typing import List

class RuleService:
    def __init__(self, db: Session):
        self.db = db

    def create_rule(self, rule: Rule) -> Rule:
        """Create a new rule."""
        db_rule = RuleModel(**rule.dict())
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        return db_rule

    def get_rule(self, rule_id: int, firm_id: str) -> Rule:
        """Get a rule by ID with firm_id filtering."""
        rule = self.db.query(RuleModel).filter(
            RuleModel.rule_id == rule_id,
            RuleModel.firm_id == firm_id
        ).first()
        if not rule:
            raise ValueError("Rule not found")
        return rule

    def list_rules(self, firm_id: str, client_id: int = None) -> List[Rule]:
        """List all rules for a firm, optionally filtered by client."""
        query = self.db.query(RuleModel).filter(RuleModel.firm_id == firm_id)
        if client_id:
            query = query.filter(RuleModel.client_id == client_id)
        rules = query.all()
        return rules
