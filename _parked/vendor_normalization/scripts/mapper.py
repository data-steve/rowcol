import pandas as pd
import yaml
from pathlib import Path

PROC = Path("data/processed")
OUT = Path("data/out")

def load_maps(coa_map_path: str = "config/coa_map.yaml"):
    with open(coa_map_path, "r") as f:
        m = yaml.safe_load(f) or {}
    mcc_map = m.get("mcc_to_coa", {})
    naics_map = m.get("naics_to_coa", {})
    return mcc_map, naics_map

def build_vendor_mapping(vendor_table: pd.DataFrame, mcc_ref: pd.DataFrame, naics_ref: pd.DataFrame, mcc_map: dict, naics_map: dict):
    # For bootstrap, we map vendors by heuristic MCC/NAICS guesses if known.
    # In a real pipeline, you would attach MCC via merchant data or card processor exports.
    # Here, we demonstrate fallback priority: MCC first, then NAICS.
    vendor_table = vendor_table.copy()
    vendor_table["mcc"] = None
    vendor_table["naics"] = None
    vendor_table["coa_category"] = None
    # Heuristic examples for demo
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("UBER"), "mcc"] = "4121"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("LYFT"), "mcc"] = "4121"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("COFFEE|STARBUCKS|BLUE BOTTLE"), "mcc"] = "5812"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("DELTA AIR"), "mcc"] = "4511"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("COMCAST|XFINITY"), "naics"] = "517111"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("AMAZON"), "naics"] = "454110"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("DUKE ENERGY"), "naics"] = "517111"  # simplified
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("UNITED STATES POSTAL"), "mcc"] = "4215"
    vendor_table.loc[vendor_table["vendor_canonical"].str.contains("STRIPE"), "mcc"] = "7399"

    def map_row(row):
        if row["mcc"] and row["mcc"] in mcc_map:
            return mcc_map[row["mcc"]]
        if row["naics"] and row["naics"] in naics_map:
            return naics_map[row["naics"]]
        return None

    vendor_table["coa_category"] = vendor_table.apply(map_row, axis=1)
    return vendor_table

def emit_rules_yaml(vendor_map: pd.DataFrame, out_path: str = "data/out/rules.yaml"):
    # Emit deterministic contains/exact rules for Escher Autocode.
    contains_rules = []

    for _, r in vendor_map.dropna(subset=["coa_category"]).iterrows():
        pattern = r["vendor_canonical"]
        account = r["coa_category"]
        # Commonly, we put high-precision names as contains (since bank descriptors include extra tokens).
        contains_rules.append({"pattern": pattern, "output": {"account": account, "confidence": 0.9}})

    import yaml
    doc = {
        "global": {
            "locked_accounts": ["Balance Sheet:Cash", "Equity:Retained Earnings"],
            "auto_post_threshold": 0.9,
            "review_threshold": 0.6
        },
        "rules": {
            "exact": [],
            "contains": contains_rules,
            "regex": [],
            "amount_range": [],
            "transfer_heuristic": []
        }
    }
    with open(out_path, "w") as f:
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)

def save_outputs(vendor_map: pd.DataFrame, mcc_map: dict, naics_map: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    vendor_map.to_csv(OUT / "vendor_canonical.csv", index=False)
    pd.DataFrame([{"mcc":k, "coa":v} for k,v in mcc_map.items()]).to_csv(OUT / "mcc_to_coa_map.csv", index=False)
    pd.DataFrame([{"naics":k, "coa":v} for k,v in naics_map.items()]).to_csv(OUT / "naics_to_coa_map.csv", index=False)
