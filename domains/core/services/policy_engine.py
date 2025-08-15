from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from domains.core.models.rule import Rule as RuleModel
from domains.core.models.correction import Correction as CorrectionModel
from domains.core.models.suggestion import Suggestion as SuggestionModel
from domains.core.models.policy_profile import PolicyProfile as PolicyProfileModel
from domains.ap.models.policy_rule_template import PolicyRuleTemplate
from domains.ap.models.vendor_category import VendorCategory
from domains.core.schemas.suggestion import Suggestion
from domains.core.schemas.correction import Correction
from domains.core.schemas.rule import Rule
import re
import json

class PolicyEngineService:
    def __init__(self, db: Session):
        self.db = db

    def categorize_transaction(self, txn: Dict, firm_id: str, client_id: Optional[int] = None) -> SuggestionModel:
        """Categorize a transaction using real policy rules from database."""
        # Get applicable policy rules for this transaction
        rules = self.db.query(PolicyRuleTemplate).filter(
            PolicyRuleTemplate.is_active == True,
            PolicyRuleTemplate.rule_type == "categorization"
        ).order_by(PolicyRuleTemplate.priority).all()
        
        # Apply rules to determine categorization
        top_k = []
        for rule in rules:
            if self._evaluate_rule_conditions(txn, rule.conditions):
                confidence = self._compute_confidence(txn, rule)
                top_k.append({
                    "account": rule.actions.get("default_account", "6000-Expenses"),
                    "confidence": confidence,
                    "rule_id": str(rule.rule_id),  # Ensure rule_id is always a string
                    "rule_name": rule.rule_name
                })
        
        # Sort by confidence and take top 3
        top_k.sort(key=lambda x: x["confidence"], reverse=True)
        top_k = top_k[:3]
        
        # If no rules matched, use vendor category lookup
        if not top_k:
            vendor_category = self._get_vendor_category(txn.get("vendor_name", ""))
            if vendor_category:
                top_k.append({
                    "account": vendor_category.default_gl_account or "6000-Expenses",
                    "confidence": 0.6,
                    "rule_id": "vendor_category",  # Use string instead of None
                    "rule_name": f"Vendor Category: {vendor_category.category_name}"
                })
        
        # Default fallback
        if not top_k:
            top_k.append({
                "account": "6000-Expenses",
                "confidence": 0.3,
                "rule_id": "default",  # Use string instead of None
                "rule_name": "Default Category"
            })
        
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
        return suggestion

    def categorize(self, firm_id: str, description: str, amount: float, client_id: Optional[int] = None) -> SuggestionModel:
        """Categorize a transaction by description and amount (wrapper for categorize_transaction)."""
        txn = {
            "description": description,
            "amount": amount,
            "txn_id": f"txn_{hash(description)}"
        }
        return self.categorize_transaction(txn, firm_id, client_id)

    def add_rule(self, firm_id: str, pattern: str, output: Dict, client_id: Optional[int] = None, priority: int = 10, match_type: str = "exact") -> RuleModel:
        """Add a new rule to the policy engine."""
        rule = RuleModel(firm_id=firm_id, client_id=client_id, priority=priority, match_type=match_type, pattern=pattern, output=output, scope="client" if client_id else "global")
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def apply_correction(self, correction: Correction, firm_id: str) -> CorrectionModel:
        """Persist a correction and update rules if applicable."""
        db_correction = CorrectionModel(**correction.dict())
        self.db.add(db_correction)
        self.db.commit()
        self.db.refresh(db_correction)
        return db_correction

    def _evaluate_rule_conditions(self, txn: Dict, conditions: str) -> bool:
        """Evaluate rule conditions against transaction data."""
        try:
            cond = json.loads(conditions) if isinstance(conditions, str) else conditions
            
            # Check amount conditions
            if "amount_greater_than" in cond:
                if txn.get("amount", 0) <= cond["amount_greater_than"]:
                    return False
            
            if "amount_less_than" in cond:
                if txn.get("amount", 0) >= cond["amount_less_than"]:
                    return False
            
            # Check category conditions
            if "category" in cond and cond["category"] != "any":
                if txn.get("category") != cond["category"]:
                    return False
            
            # Check vendor type conditions
            if "vendor_type" in cond:
                vendor_name = txn.get("vendor_name", "")
                if cond["vendor_type"] == "individual" and not self._is_individual_vendor(vendor_name):
                    return False
            
            return True
            
        except (json.JSONDecodeError, KeyError):
            return False

    def _is_individual_vendor(self, vendor_name: str) -> bool:
        """Determine if vendor is an individual based on name patterns."""
        # Simple heuristic - could be enhanced with ML or external data
        individual_indicators = ["llc", "inc", "corp", "corporation", "company", "co", "ltd"]
        vendor_lower = vendor_name.lower()
        return not any(indicator in vendor_lower for indicator in individual_indicators)

    def _get_vendor_category(self, vendor_name: str) -> Optional[VendorCategory]:
        """Get vendor category based on vendor name patterns."""
        if not vendor_name:
            return None
        
        # Simple keyword matching - could be enhanced with ML
        vendor_lower = vendor_name.lower()
        
        if any(word in vendor_lower for word in ["office", "supply", "staples", "amazon"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Office Supplies"
            ).first()
        elif any(word in vendor_lower for word in ["legal", "law", "attorney", "cpa", "accountant"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Professional Services"
            ).first()
        elif any(word in vendor_lower for word in ["software", "tech", "computer", "it"]):
            return self.db.query(VendorCategory).filter(
                VendorCategory.category_name == "Technology"
            ).first()
        
        return None

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

    def _compute_confidence(self, txn: Dict, rule: PolicyRuleTemplate) -> float:
        """Compute confidence score based on real business rules and data."""
        base_confidence = 0.7  # Base confidence for template rules
        
        # Adjust confidence based on rule priority
        priority_boost = (10 - rule.priority) * 0.05  # Higher priority = higher confidence
        
        # Adjust based on transaction data quality
        data_quality_score = 1.0
        if not txn.get("vendor_name"):
            data_quality_score *= 0.8
        if not txn.get("amount"):
            data_quality_score *= 0.9
        
        # Adjust based on rule type
        rule_type_score = 1.0
        if rule.rule_type == "compliance":
            rule_type_score = 1.1  # Compliance rules get higher confidence
        elif rule.rule_type == "fraud_detection":
            rule_type_score = 0.9  # Fraud detection rules get lower confidence
        
        confidence = (base_confidence + priority_boost) * data_quality_score * rule_type_score
        return min(max(confidence, 0.0), 1.0)