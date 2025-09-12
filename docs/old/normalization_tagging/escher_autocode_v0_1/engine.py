import re
import csv
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import yaml

@dataclass
class Rule:
    type: str
    pattern: Any  # str for exact/contains/regex; dict for amount_range; str for heuristics
    output: Dict[str, Any]

@dataclass
class EngineConfig:
    auto_post_threshold: float = 0.9
    review_threshold: float = 0.6
    locked_accounts: List[str] = field(default_factory=lambda: ["Balance Sheet:Cash", "Equity:Retained Earnings"])

class AutoCoder:
    def __init__(self, rules: Dict[str, Any]):
        self.rules_raw = rules
        self.config = self._load_config(rules)
        self.rules = self._load_rules(rules)

    @staticmethod
    def _load_config(rules: Dict[str, Any]) -> EngineConfig:
        g = (rules or {}).get("global", {})
        return EngineConfig(
            auto_post_threshold = float(g.get("auto_post_threshold", 0.9)),
            review_threshold = float(g.get("review_threshold", 0.6)),
            locked_accounts = list(g.get("locked_accounts", ["Balance Sheet:Cash", "Equity:Retained Earnings"]))
        )

    @staticmethod
    def _normalize_rules(rule_list: List[Dict[str, Any]], rtype: str) -> List[Rule]:
        out: List[Rule] = []
        for r in rule_list or []:
            out.append(Rule(type=rtype, pattern=r.get("pattern") if rtype!="amount_range" else {"min": r.get("min"), "max": r.get("max")}, output=r.get("output", {})))
        return out

    def _load_rules(self, rules: Dict[str, Any]) -> Dict[str, List[Rule]]:
        r = (rules or {}).get("rules", {})
        return {
            "exact": self._normalize_rules(r.get("exact", []), "exact"),
            "contains": self._normalize_rules(r.get("contains", []), "contains"),
            "regex": self._normalize_rules(r.get("regex", []), "regex"),
            "amount_range": self._normalize_rules(r.get("amount_range", []), "amount_range"),
            "transfer_heuristic": self._normalize_rules(r.get("transfer_heuristic", []), "transfer_heuristic"),
        }

    @staticmethod
    def _h(s: str) -> str:
        return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]

    def _match_rule(self, row: Dict[str, Any]) -> Tuple[Optional[Rule], Dict[str, Any]]:
        desc = str(row.get("description","")).upper()
        counterparty = str(row.get("counterparty","")).upper()
        amount = float(row.get("amount", 0) or 0)

        # 1) exact
        for rule in self.rules["exact"]:
            pat = str(rule.pattern).upper()
            if desc == pat or counterparty == pat:
                return rule, {"why": f"exact match '{pat}'"}

        # 2) contains
        for rule in self.rules["contains"]:
            pat = str(rule.pattern).upper()
            if pat in desc or pat in counterparty:
                return rule, {"why": f"contains '{pat}'"}

        # 3) regex
        for rule in self.rules["regex"]:
            pat = str(rule.pattern)
            if re.search(pat, desc, flags=re.IGNORECASE) or re.search(pat, counterparty, flags=re.IGNORECASE):
                return rule, {"why": f"regex '{pat}'"}

        # 4) amount_range
        for rule in self.rules["amount_range"]:
            rng = rule.pattern or {}
            mn = float(rng.get("min", float("-inf")))
            mx = float(rng.get("max", float("inf")))
            if amount >= mn and amount <= mx:
                return rule, {"why": f"amount_range {mn}..{mx}"}

        # 5) transfer heuristic
        for rule in self.rules["transfer_heuristic"]:
            pat = str(rule.pattern).upper()
            if pat in desc or pat in counterparty:
                return rule, {"why": f"transfer_heuristic '{pat}'"}

        return None, {}

    def decide(self, proposed: Dict[str, Any]) -> Tuple[bool, bool, str]:
        """Return (auto_post, needs_review, reason) based on confidence + locked accounts."""
        conf = float(proposed.get("confidence", 0))
        acct = str(proposed.get("account", "")).strip()

        # Locked accounts guardrail
        if acct in self.config.locked_accounts:
            return False, True, f"Account '{acct}' is locked; force review"

        if conf >= self.config.auto_post_threshold:
            return True, False, "Confidence >= auto_post_threshold"
        if conf >= self.config.review_threshold:
            return False, True, "Confidence in review band"
        return False, True, "Low confidence"

    def autocode_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        rule, meta = self._match_rule(row)
        out = dict(row)  # preserve original
        explain = {"rule_type": None, "rule_why": None, "applied": False}

        if rule:
            proposed = dict(rule.output)
            explain["rule_type"] = rule.type
            explain["rule_why"] = meta.get("why")
            auto_post, needs_review, reason = self.decide(proposed)
            out.update({
                "proposed_account": proposed.get("account"),
                "proposed_class": proposed.get("class"),
                "proposed_location": proposed.get("location"),
                "proposed_memo": proposed.get("memo"),
                "proposed_tax_flag": proposed.get("tax_flag"),
                "confidence": proposed.get("confidence", 0.0),
                "auto_post": auto_post,
                "needs_review": needs_review,
                "decision_reason": reason,
                "explain_rule_type": explain["rule_type"],
                "explain_rule_why": explain["rule_why"],
            })
            return out

        # Fallback heuristic (very light)
        out.update({
            "proposed_account": None,
            "proposed_class": None,
            "proposed_location": None,
            "proposed_memo": None,
            "proposed_tax_flag": None,
            "confidence": 0.0,
            "auto_post": False,
            "needs_review": True,
            "decision_reason": "No rule match",
            "explain_rule_type": None,
            "explain_rule_why": None,
        })
        return out

    @staticmethod
    def _normalize_headers(row: Dict[str, Any]) -> Dict[str, Any]:
        m = {k.lower().strip(): v for k, v in row.items()}
        # Ensure required fields exist
        if "description" not in m:
            # try alternatives
            for alt in ["memo", "narrative", "details"]:
                if alt in m:
                    m["description"] = m[alt]
                    break
            else:
                m["description"] = ""
        if "amount" in m:
            try:
                m["amount"] = float(str(m["amount"]).replace(",",""))
            except:
                m["amount"] = 0.0
        else:
            m["amount"] = 0.0
        if "txn_id" not in m or not str(m.get("txn_id","")).strip():
            # derive a stable id from date+descr+amount
            base = f"{m.get('date','')}-{m.get('description','')}-{m.get('amount','')}"
            m["txn_id"] = AutoCoder._h(base)
        return m

    def autocode(self, csv_path: str, out_path: str) -> None:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = [self._normalize_headers(r) for r in reader]

        coded = [self.autocode_row(r) for r in rows]

        # Write output
        fieldnames = list(coded[0].keys()) if coded else []
        with open(out_path, "w", newline="", encoding="utf-8") as w:
            writer = csv.DictWriter(w, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(coded)

def load_rules_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_rules_yaml(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def learn_from_corrections(corrections_csv: str, rules_yaml_path: str, out_rules_yaml_path: str, scope: str = "client") -> None:
    """Promote corrections to deterministic rules (contains by default)."""
    rules = load_rules_yaml(rules_yaml_path)
    rules_section = rules.setdefault("rules", {})
    contains_list = rules_section.setdefault("contains", [])

    with open(corrections_csv, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Expect columns: txn_id, description, final_account, final_class, final_location, pattern(optional)
            pattern = (r.get("pattern") or r.get("description") or "").strip()
            if not pattern:
                continue
            out = {"account": r.get("final_account", "").strip()}
            if r.get("final_class"):
                out["class"] = r["final_class"].strip()
            if r.get("final_location"):
                out["location"] = r["final_location"].strip()
            out["confidence"] = 0.9  # learned rules default

            # Prepend for higher priority
            contains_list.insert(0, {"pattern": pattern, "output": out})

    save_rules_yaml(out_rules_yaml_path, rules)
