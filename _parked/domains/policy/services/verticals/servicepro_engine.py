from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy import text
import json
import re
import uuid
from datetime import datetime

from domains.policy.services.policy_engine import PolicyEngineService

# Cashola CDM policy groupings
CDM_MUST_PAY = {
    "PAYROLL_TOTAL", "RENT_UTILITIES", "INSURANCE", "DEBT_SERVICE", "TAXES_GOVT"
}
CDM_CAN_DELAY = {
    "SAAS_FEES", "OWNER_DRAWS", "CAPEX", "OTHER"
}

@dataclass
class LedgerRowDTO:
    id: str
    company_id: str
    counterparty: str
    amount_cents: int
    currency: str
    posted_at: str
    direction: str

class ServiceProPolicyEngine(PolicyEngineService):
    """
    Vertical extension of PolicyEngineService:
      - Contractor/vendor heuristics (ServicePro rules)
      - CDM mapping + ledger categorization for Cashola
    """

    # ---------- ServicePro rules ----------
    def get_servicepro_rules(self, firm_id: str) -> List[Dict[str, Any]]:
        """Get ServicePro-specific business rules for contractor categorization."""
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

    def _calculate_servicepro_rule_confidence(self, rule: Dict, all_text: str, vendor_name: str, amount: float) -> float:
        """Calculate confidence score for ServicePro rule matching."""
        confidence = 0.0
        
        # Pattern matching (40% weight)
        if rule["match_type"] == "contains":
            if rule["pattern"] in all_text:
                confidence += 0.4
        elif rule["match_type"] == "regex":
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
        if len(all_text) > 50:
            confidence += 0.1
        
        return min(1.0, confidence)

    def categorize_servicepro_transaction(self, txn: Dict, firm_id: str, client_id: Optional[int] = None) -> Dict[str, Any]:
        """Categorize ServicePro transactions using specialized business rules."""
        servicepro_rules = self.get_servicepro_rules(firm_id)
        
        description = txn.get("description", "").lower()
        vendor_name = txn.get("vendor_name", "").lower()
        amount = abs(txn.get("amount", 0))
        memo = txn.get("memo", "").lower()
        
        all_text = f"{description} {vendor_name} {memo}".lower()
        
        best_match = None
        highest_confidence = 0.0
        
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
        
        # Fallback to generic categorizer
        suggestion = self.categorize_transaction(txn, firm_id, client_id)
        return {
            "account": getattr(suggestion, 'suggested_account', "Uncategorized"),
            "confidence": getattr(suggestion, 'confidence', 0.5),
            "category": getattr(suggestion, 'suggested_category', "General"),
            "rule_name": "General categorization",
            "requires_receipt": False,
            "suggested_action": getattr(suggestion, 'explanation', "Manual review needed")
        }

    # ---------- CDM mapping + ledger adapter (Cashola) ----------
    def _map_account_or_category_to_cdm_policy(self, account: Optional[str], category: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        a = (account or "").lower()
        c = (category or "").lower()

        # Heuristics by account
        if any(k in a for k in ["payroll", "wages", "salary", "gusto", "adp", "paychex"]):
            return "PAYROLL_TOTAL", "MUST_PAY"
        if any(k in a for k in ["utilities", "rent", "lease"]):
            return "RENT_UTILITIES", "MUST_PAY"
        if any(k in a for k in ["insurance", "workers comp", "general liability"]):
            return "INSURANCE", "MUST_PAY"
        if any(k in a for k in ["loan", "interest", "note", "equipment finance", "stripe capital"]):
            return "DEBT_SERVICE", "MUST_PAY"
        if any(k in a for k in ["tax", "irs", "state tax", "sales tax"]):
            return "TAXES_GOVT", "MUST_PAY"
        if any(k in a for k in ["software", "saas", "subscription", "stripe fee", "processing fee"]):
            return "SAAS_FEES", "CAN_DELAY"
        if any(k in a for k in ["owner draw", "distribution", "member draw"]):
            return "OWNER_DRAWS", "CAN_DELAY"
        if any(k in a for k in ["capex", "equipment", "capital", "asset"]):
            return "CAPEX", "CAN_DELAY"

        # Heuristics by category
        if "professional services" in c:
            return "OTHER", "CAN_DELAY"
        if "office" in c:
            return "OTHER", "CAN_DELAY"
        if "materials" in c or "cogs" in c or "subcontractor" in c:
            return "OTHER", "CAN_DELAY"

        return None, None

    def classify_ledger_row(self, row: LedgerRowDTO, firm_id: str, client_id: Optional[int] = None) -> Tuple[Optional[str], Optional[str], dict]:
        """
        Uses ServicePro specialization + base categorizer to get (account, category),
        then maps to (cdm_key, policy). Returns (cdm_key, policy, debug_info).
        """
        txn = {
            "txn_id": row.id,
            "description": row.counterparty or "",
            "vendor_name": row.counterparty or "",
            "amount": abs(row.amount_cents) / 100.0,
            "memo": "",
            "category": None,
        }

        sp = self.categorize_servicepro_transaction(txn, firm_id=firm_id, client_id=client_id)
        account = sp.get("account")
        category = sp.get("category")
        debug = {"servicepro": sp}

        if sp.get("confidence", 0) < 0.65:
            sugg = self.categorize_transaction(txn, firm_id=firm_id, client_id=client_id)
            account = getattr(sugg, "suggested_account", account) or account
            category = getattr(sugg, "suggested_category", category) or category
            debug["fallback"] = {"suggested_account": account, "suggested_category": category}

        cdm_key, policy = self._map_account_or_category_to_cdm_policy(account, category)
        return cdm_key, policy, debug

    def categorize_ledger_rows(self, company_id: str, since_iso: str, firm_id: Optional[str] = None, client_id: Optional[int] = None) -> int:
        """
        Reads cash_ledger rows since `since_iso`, sets (cdm_key, policy) or opens UNMAPPED exception.
        Returns number of rows updated. SQLite-safe.
        """
        rows = self.db.execute(
            text("""
                SELECT id, company_id, COALESCE(counterparty,''), amount_cents, COALESCE(currency,'USD'),
                       posted_at, direction
                FROM cash_ledger
                WHERE company_id = :cid AND posted_at >= :since
            """),
            {"cid": company_id, "since": since_iso}
        ).fetchall()

        updated = 0
        for r in rows:
            row = LedgerRowDTO(id=r[0], company_id=r[1], counterparty=r[2],
                               amount_cents=r[3], currency=r[4], posted_at=r[5], direction=r[6])

            cdm_key, policy, debug = self.classify_ledger_row(row, firm_id=firm_id or company_id, client_id=client_id)

            if cdm_key and policy:
                # SQLite vs others JSON handling
                if self.db.bind.dialect.name == "sqlite":
                    self.db.execute(
                        text("""
                            UPDATE cash_ledger
                            SET cdm_key=:cdm, policy=:pol,
                                provenance_json = json_set(COALESCE(provenance_json,'{}'), '$.policy_debug', :dbg)
                            WHERE id=:id
                        """),
                        {"cdm": cdm_key, "pol": policy, "dbg": json.dumps({"policy_debug": debug}), "id": row.id}
                    )
                else:
                    self.db.execute(
                        text("""
                            UPDATE cash_ledger
                            SET cdm_key=:cdm, policy=:pol, provenance_json=:dbg
                            WHERE id=:id
                        """),
                        {"cdm": cdm_key, "pol": policy, "dbg": json.dumps({"policy_debug": debug}), "id": row.id}
                    )
                updated += 1
            else:
                # Open UNMAPPED exception if not already open for this ledger row
                if self.db.bind.dialect.name == "sqlite":
                    self.db.execute(
                        text("""
                            INSERT INTO exception (id, company_id, kind, status, context_json, created_at)
                            SELECT :id, :cid, 'UNMAPPED', 'open', :ctx, :now
                            WHERE NOT EXISTS (
                                SELECT 1 FROM exception
                                WHERE company_id=:cid AND kind='UNMAPPED' AND status='open'
                                  AND json_extract(context_json, '$.ledger_id') = :lid
                            )
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "cid": company_id,
                            "lid": row.id,
                            "ctx": json.dumps({"ledger_id": row.id, "counterparty": row.counterparty}),
                            "now": datetime.utcnow().isoformat()
                        }
                    )
                else:
                    self.db.execute(
                        text("""
                            INSERT INTO exception (id, company_id, kind, status, context_json, created_at)
                            VALUES (:id, :cid, 'UNMAPPED', 'open', :ctx, :now)
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "cid": company_id,
                            "ctx": json.dumps({"ledger_id": row.id, "counterparty": row.counterparty}),
                            "now": datetime.utcnow().isoformat()
                        }
                    )

        self.db.commit()
        return updated
