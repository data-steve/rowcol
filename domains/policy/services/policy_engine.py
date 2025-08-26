from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from domains.ap.models.policy_rule_template import (
    PolicyRuleTemplate as PolicyRuleTemplate,
)
from domains.policy.models.rule import Rule as RuntimeRule
from domains.policy.models.correction import Correction as CorrectionModel
from domains.policy.models.suggestion import Suggestion as SuggestionModel
from domains.policy.models.policy_profile import PolicyProfile as PolicyProfileModel
from domains.ap.models.vendor_category import VendorCategory
from domains.policy.schemas.suggestion import Suggestion
from domains.policy.schemas.correction import Correction
from domains.policy.schemas.rule import Rule
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

    def add_rule(self, firm_id: str, pattern: str, output: Dict, client_id: Optional[int] = None, priority: int = 10, match_type: str = "exact") -> RuntimeRule:
        """Add a new runtime rule (not a template)."""
        rule = RuntimeRule(
            firm_id=firm_id,
            client_id=client_id,
            priority=priority,
            match_type=match_type,
            pattern=pattern,
            output=output,
            scope="client" if client_id else "global",
        )
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

    def get_servicepro_rules(self, firm_id: str) -> List[Dict[str, Any]]:
        """Get ServicePro-specific business rules for contractor categorization."""
        # These rules are designed to handle the messy reality of service contractor expenses
        # that make accountants fall back to Excel
        
        servicepro_rules = [
            # Materials & Supplies
            {
                "rule_name": "Home Depot Materials",
                "pattern": "home depot",
                "match_type": "contains",
                "confidence": 0.95,
                "actions": {
                    "default_account": "5000-Materials",
                    "job_allocation": "by_job_size",
                    "category": "Materials & Supplies",
                    "requires_receipt": True
                },
                "vendor_keywords": ["home depot", "lowes", "menards", "ace hardware", "true value"],
                "amount_range": "0-10000"
            },
            {
                "rule_name": "Landscape Materials",
                "pattern": "landscape|mulch|soil|plants|trees|shrubs",
                "match_type": "regex",
                "confidence": 0.90,
                "actions": {
                    "default_account": "5000-Materials",
                    "job_allocation": "by_job_size",
                    "category": "Landscape Materials",
                    "requires_receipt": True
                },
                "vendor_keywords": ["nursery", "garden center", "landscape supply", "mulch supplier"],
                "amount_range": "0-5000"
            },
            {
                "rule_name": "Plumbing Supplies",
                "pattern": "plumbing|pipe|fixture|valve|fitting",
                "match_type": "regex",
                "confidence": 0.90,
                "actions": {
                    "default_account": "5000-Materials",
                    "job_allocation": "by_job_size",
                    "category": "Plumbing Materials",
                    "requires_receipt": True
                },
                "vendor_keywords": ["plumbing supply", "hvac supply", "contractor supply"],
                "amount_range": "0-8000"
            },
            {
                "rule_name": "HVAC Equipment",
                "pattern": "hvac|heating|cooling|furnace|ac unit|thermostat",
                "match_type": "regex",
                "confidence": 0.95,
                "actions": {
                    "default_account": "5000-Materials",
                    "job_allocation": "by_job_size",
                    "category": "HVAC Equipment",
                    "requires_receipt": True
                },
                "vendor_keywords": ["hvac supply", "carrier", "trane", "lennox", "rheem"],
                "amount_range": "0-15000"
            },
            
            # Fuel & Vehicle Expenses
            {
                "rule_name": "Fuel Reimbursements",
                "pattern": "fuel|gas|exxon|shell|bp|chevron|mobil",
                "match_type": "regex",
                "confidence": 0.90,
                "actions": {
                    "default_account": "5400-Vehicle Expenses",
                    "job_allocation": "by_crew_hours",
                    "category": "Fuel & Transportation",
                    "requires_receipt": True
                },
                "vendor_keywords": ["exxon", "shell", "bp", "chevron", "mobil", "speedway", "quik trip"],
                "amount_range": "0-500"
            },
            {
                "rule_name": "Vehicle Maintenance",
                "pattern": "oil change|tire|brake|repair|maintenance|auto",
                "match_type": "regex",
                "confidence": 0.85,
                "actions": {
                    "default_account": "5400-Vehicle Expenses",
                    "job_allocation": "by_vehicle_usage",
                    "category": "Vehicle Maintenance",
                    "requires_receipt": True
                },
                "vendor_keywords": ["jiffy lube", "firestone", "goodyear", "auto zone", "oreilly"],
                "amount_range": "0-2000"
            },
            
            # Equipment & Tools
            {
                "rule_name": "Equipment Rental",
                "pattern": "rental|equipment|tool|machinery|scaffold|lift",
                "match_type": "regex",
                "confidence": 0.85,
                "actions": {
                    "default_account": "5200-Equipment Rental",
                    "job_allocation": "by_usage_days",
                    "category": "Equipment Rental",
                    "requires_receipt": True
                },
                "vendor_keywords": ["united rentals", "sunbelt rentals", "hss", "kennards", "coates"],
                "amount_range": "0-5000"
            },
            {
                "rule_name": "Small Tools",
                "pattern": "tool|drill|saw|hammer|wrench|screwdriver",
                "match_type": "regex",
                "confidence": 0.80,
                "actions": {
                    "default_account": "5100-Small Tools",
                    "job_allocation": "by_job_count",
                    "category": "Small Tools",
                    "requires_receipt": True
                },
                "vendor_keywords": ["harbor freight", "northern tool", "grainger", "mcmaster carr"],
                "amount_range": "0-1000"
            },
            
            # Subcontractor Services
            {
                "rule_name": "Subcontractor Services",
                "pattern": "subcontractor|sub|specialty|licensed|certified",
                "match_type": "regex",
                "confidence": 0.90,
                "actions": {
                    "default_account": "6000-Subcontractor Services",
                    "job_allocation": "by_job_size",
                    "category": "Subcontractor Services",
                    "requires_contract": True
                },
                "vendor_keywords": ["licensed", "certified", "specialty", "subcontractor"],
                "amount_range": "0-50000"
            },
            
            # Insurance & Permits
            {
                "rule_name": "Insurance & Permits",
                "pattern": "insurance|permit|license|bond|certificate",
                "match_type": "regex",
                "confidence": 0.95,
                "actions": {
                    "default_account": "7000-Insurance & Permits",
                    "job_allocation": "by_job_count",
                    "category": "Insurance & Permits",
                    "requires_documentation": True
                },
                "vendor_keywords": ["state farm", "allstate", "geico", "city hall", "county clerk"],
                "amount_range": "0-10000"
            },
            
            # Office & Administrative
            {
                "rule_name": "Office Supplies",
                "pattern": "office|supply|paper|ink|toner|staples",
                "match_type": "regex",
                "confidence": 0.85,
                "actions": {
                    "default_account": "6100-Office Supplies",
                    "job_allocation": "by_job_count",
                    "category": "Office Supplies",
                    "requires_receipt": True
                },
                "vendor_keywords": ["staples", "office depot", "amazon", "walmart"],
                "amount_range": "0-500"
            },
            
            # Professional Services
            {
                "rule_name": "Professional Services",
                "pattern": "cpa|accountant|attorney|lawyer|consultant|engineer",
                "match_type": "regex",
                "confidence": 0.90,
                "actions": {
                    "default_account": "6200-Professional Services",
                    "job_allocation": "by_job_count",
                    "category": "Professional Services",
                    "requires_invoice": True
                },
                "vendor_keywords": ["cpa", "attorney", "lawyer", "consultant", "engineer"],
                "amount_range": "0-10000"
            }
        ]
        
        return servicepro_rules

    def categorize_servicepro_transaction(self, txn: Dict, firm_id: str, client_id: Optional[int] = None) -> Dict[str, Any]:
        """Categorize ServicePro transactions using specialized business rules."""
        # Get ServicePro rules
        servicepro_rules = self.get_servicepro_rules(firm_id)
        
        # Extract transaction details
        description = txn.get("description", "").lower()
        vendor_name = txn.get("vendor_name", "").lower()
        amount = abs(txn.get("amount", 0))
        memo = txn.get("memo", "").lower()
        
        # Combine all text for pattern matching
        all_text = f"{description} {vendor_name} {memo}".lower()
        
        best_match = None
        highest_confidence = 0.0
        
        # Apply ServicePro rules
        for rule in servicepro_rules:
            confidence = self._calculate_servicepro_rule_confidence(rule, all_text, vendor_name, amount)
            
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_match = rule
        
        if best_match and highest_confidence >= 0.65:
            return {
                "account": best_match["actions"]["default_account"],
                "confidence": highest_confidence,
                "rule_name": best_match["rule_name"],
                "category": best_match["actions"]["category"],
                "job_allocation": best_match["actions"]["job_allocation"],
                "requires_receipt": best_match["actions"].get("requires_receipt", False),
                "requires_contract": best_match["actions"].get("requires_contract", False),
                "requires_documentation": best_match["actions"].get("requires_documentation", False),
                "requires_invoice": best_match["actions"].get("requires_invoice", False),
                "suggested_action": f"Auto-categorized as {best_match['actions']['category']} using {best_match['rule_name']}"
            }
        
        # Fallback to general categorization
        suggestion = self.categorize_transaction(txn, firm_id, client_id)
        # Convert SuggestionModel to dictionary for consistency
        return {
            "account": suggestion.suggested_account if hasattr(suggestion, 'suggested_account') else "Uncategorized",
            "confidence": suggestion.confidence if hasattr(suggestion, 'confidence') else 0.5,
            "category": suggestion.suggested_category if hasattr(suggestion, 'suggested_category') else "General",
            "rule_name": "General categorization",
            "requires_receipt": False,
            "suggested_action": suggestion.explanation if hasattr(suggestion, 'explanation') else "Manual review needed"
        }
    
    def _calculate_servicepro_rule_confidence(self, rule: Dict, all_text: str, vendor_name: str, amount: float) -> float:
        """Calculate confidence score for ServicePro rule matching."""
        confidence = 0.0
        
        # Pattern matching (40% weight)
        if rule["match_type"] == "contains":
            if rule["pattern"] in all_text:
                confidence += 0.4
        elif rule["match_type"] == "regex":
            import re
            if re.search(rule["pattern"], all_text, re.IGNORECASE):
                confidence += 0.4
        
        # Vendor keyword matching (30% weight)
        vendor_score = 0.0
        for keyword in rule.get("vendor_keywords", []):
            if keyword in vendor_name:
                vendor_score = max(vendor_score, 0.3)
            elif keyword in all_text:
                vendor_score = max(vendor_score, 0.2)
        confidence += vendor_score
        
        # Amount range matching (20% weight)
        amount_range = rule.get("amount_range", "0-999999")
        try:
            min_amt, max_amt = map(float, amount_range.split("-"))
            if min_amt <= amount <= max_amt:
                confidence += 0.2
        except:
            pass
        
        # Text complexity bonus (10% weight)
        # More complex descriptions get higher confidence
        if len(all_text) > 50:
            confidence += 0.1
        
        return min(1.0, confidence)

    def _match_rule(self, txn: Dict, rule: PolicyRuleTemplate) -> bool:
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