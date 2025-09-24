import yaml
import pandas as pd
from pathlib import Path
from src.downloader import download_usaspending, ensure_mcc_reference, ensure_naics_reference
from src.cleaners import load_normalize_cfg, normalize_bank_descriptors, build_vendor_canonical, fuzzy_match_descriptors
from src.mapper import load_maps, build_vendor_mapping, emit_rules_yaml, save_outputs

RAW = Path("data/raw")
PROC = Path("data/processed")
OUT = Path("data/out")

def main():
    print("[1/5] Load config")
    with open("config/data_sources.yaml","r") as f:
        sources = yaml.safe_load(f) or {}
    norm_cfg = load_normalize_cfg("config/normalize.yaml")

    print("[2/5] Download sources (or use seeds)")
    download_usaspending(sources.get("usaspending", {}))
    mcc_csv = ensure_mcc_reference(sources.get("mcc_reference", {}))
    naics_csv = ensure_naics_reference(sources.get("naics_reference", {}))

    print("[3/5] Build canonical vendor table")
    vendor_table = build_vendor_canonical()
    PROC.mkdir(parents=True, exist_ok=True)
    vendor_table.to_csv(PROC / "vendor_canonical_base.csv", index=False)

    print("[4/5] Normalize sample bank descriptors and fuzzy match")
    sample = "sample/bank_descriptors.csv"
    if Path(sample).exists():
        df_desc = normalize_bank_descriptors(sample, norm_cfg)
        df_desc.to_csv(PROC / "bank_descriptors_norm.csv", index=False)
        matches = fuzzy_match_descriptors(df_desc["descriptor_norm"].dropna().unique(), vendor_table, score_cutoff=90)
        matches.to_csv(PROC / "descriptor_matches.csv", index=False)
    else:
        print("  [warn] sample descriptors missing; skipping")

    print("[5/5] Build vendor → COA map and emit artifacts")
    mcc_map, naics_map = load_maps("config/coa_map.yaml")
    mcc_ref = pd.read_csv(mcc_csv)
    naics_ref = pd.read_csv(naics_csv)
    vendor_map = build_vendor_mapping(vendor_table, mcc_ref, naics_ref, mcc_map, naics_map)
    save_outputs(vendor_map, mcc_map, naics_map)
    emit_rules_yaml(vendor_map, "data/out/rules.yaml")

    print("Done. See data/out/ for outputs.")

if __name__ == "__main__":
    main()
