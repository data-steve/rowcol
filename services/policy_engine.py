from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.rule import Rule as RuleModel
from models.correction import Correction as CorrectionModel
from models.suggestion import Suggestion as SuggestionModel
from models.policy_profile import PolicyProfile as PolicyProfileModel
from schemas.suggestion import Suggestion
from schemas.correction import Correction
from schemas.rule import Rule
import re

class PolicyEngineService:
    def __init__(self, db: Session):
        self.db = db

    def categorize_transaction(self, txn: Dict, firm_id: str, client_id: Optional[int] = None) -> Suggestion:
        """Categorize a transaction using layered rules and return a suggestion."""
        rules = self.db.query(RuleModel).filter(
            RuleModel.firm_id == firm_id,
            (RuleModel.client_id == client_id) | (RuleModel.client_id.is_(None))
        ).order_by(RuleModel.priority.desc()).all()

        top_k = []
        for rule in rules:
            if self._match_rule(txn, rule):
                confidence = self._compute_confidence(txn, rule)
                top_k.append({
                    "account": rule.output.get("account"),
                    "class": rule.output.get("class"),
                    "memo": rule.output.get("memo"),
                    "confidence": confidence
                })
                if len(top_k) >= 3:
                    break

        suggestion = SuggestionModel(
            firm_id=firm_id,
            client_id=client_id,
            txn_id=txn.get("txn_id"),
            top_k=top_k,
            chosen_idx=None
        )
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(suggestion)
        return Suggestion.from_orm(suggestion)

    def apply_correction(self, correction: Correction, firm_id: str) -> Correction:
        """Persist a correction and update rules if applicable."""
        db_correction = CorrectionModel(**correction.dict())
        self.db.add(db_correction)
        self.db.commit()
        self.db.refresh(db_correction)

        # Update rule if correction improves confidence
        if correction.rationale and correction.scope == "global":
            existing_rule = self.db.query(RuleModel).filter(
                RuleModel.firm_id == firm_id,
                RuleModel.pattern == correction.raw_descriptor,
                RuleModel.match_type == "exact"
            ).first()
            if not existing_rule:
                new_rule = RuleModel(
                    firm_id=firm_id,
                    client_id=correction.client_id,
                    priority=10,  # Default priority for new rules
                    match_type="exact",
                    pattern=correction.raw_descriptor,
                    output=correction.final,
                    scope=correction.scope
                )
                self.db.add(new_rule)
                self.db.commit()

        return Correction.from_orm(db_correction)

    def _match_rule(self, txn: Dict, rule: RuleModel) -> bool:
        """Check if a transaction matches a rule."""
        descriptor = txn.get("description", "")
        amount = txn.get("amount", 0.0)
        if rule.match_type == "exact":
            return descriptor.lower() == rule.pattern.lower()
        elif rule.match_type == "regex":
            return bool(re.search(rule.pattern, descriptor, re.IGNORECASE))
        elif rule.match_type == "contains":
            return rule.pattern.lower() in descriptor.lower()
        elif rule.match_type == "amount":
            try:
                min_amt, max_amt = map(float, rule.pattern.split("-"))
                return min_amt <= abs(amount) <= max_amt
            except ValueError:
                return False
        elif rule.match_type == "transfer":
            return "transfer" in descriptor.lower()
        return False

    def _compute_confidence(self, txn: Dict, rule: RuleModel) -> float:
        """Compute confidence score for a rule match."""
        base_confidence = rule.output.get("confidence", 0.5)
        weights = {
            "vendor_prior": 0.4,
            "mcc": 0.2,
            "amount_cadence": 0.2,
            "weekday": 0.1,
            "history": 0.1
        }
        # Mock additional factors (to be expanded in Phase 1)
        vendor_score = 1.0 if rule.scope == "client" else 0.8
        mcc_score = 1.0 if "mcc" in txn else 0.5
        amount_score = 1.0 if rule.match_type == "amount" else 0.8
        weekday_score = 1.0 if "weekday" in txn else 0.9
        history_score = 1.0 if rule.scope == "global" else 0.7

        confidence = (
            base_confidence * weights["vendor_prior"] * vendor_score +
            weights["mcc"] * mcc_score +
            weights["amount_cadence"] * amount_score +
            weights["weekday"] * weekday_score +
            weights["history"] * history_score
        )
        return min(max(confidence, 0.0), 1.0)