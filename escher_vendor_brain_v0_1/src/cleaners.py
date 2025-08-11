import pandas as pd
import yaml, re
from pathlib import Path
from typing import Tuple
from rapidfuzz import process, fuzz
from .utils import strip_tokens, collapse_ws, strip_digits_runs, strip_punct

PROC = Path("data/processed")

def load_normalize_cfg(path: str = "config/normalize.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def normalize_descriptor(s: str, cfg: dict) -> str:
    if s is None:
        return ""
    s0 = str(s)
    if cfg["normalize"].get("uppercase", True):
        s0 = s0.upper()
    s0 = strip_tokens(s0, cfg["normalize"].get("remove_tokens", []))
    s0 = strip_digits_runs(s0, cfg["normalize"].get("strip_digits_runs_over", 6))
    if cfg["normalize"].get("strip_punctuation", True):
        s0 = strip_punct(s0)
    if cfg["normalize"].get("collapse_whitespace", True):
        s0 = collapse_ws(s0)
    return s0

def build_vendor_canonical(usaspending_csv: str = None) -> pd.DataFrame:
    # Use whatever we have: USASpending recipients sample and seeds.
    frames = []
    p = Path("data/raw/usaspending_recipients_sample.csv")
    if p.exists():
        frames.append(pd.read_csv(p))
    # Seed examples
    seed = pd.DataFrame({
        "recipient_name": [
            "UBER TECHNOLOGIES, INC.",
            "LYFT, INC.",
            "BLUE BOTTLE COFFEE, INC.",
            "DELTA AIR LINES, INC.",
            "COMCAST CABLE COMMUNICATIONS, LLC",
            "AMAZON.COM SERVICES LLC",
            "DUKE ENERGY CORPORATION",
            "UNITED STATES POSTAL SERVICE",
            "STRIPE, INC."
        ]
    })
    frames.append(seed)
    df = pd.concat(frames, ignore_index=True).drop_duplicates()
    # Canonical vendor slug
    df["vendor_canonical"] = df["recipient_name"].str.upper().str.replace(r"[^A-Z0-9 ]","", regex=True).str.replace(r"\s+"," ", regex=True).str.strip()
    return df[["vendor_canonical","recipient_name"]].drop_duplicates()

def normalize_bank_descriptors(input_csv: str, normalize_cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    df["descriptor_norm"] = df["description"].apply(lambda s: normalize_descriptor(s, normalize_cfg))
    return df

def fuzzy_match_descriptors(descriptors: pd.Series, vendor_table: pd.DataFrame, limit: int = 1, score_cutoff: int = 90) -> pd.DataFrame:
    # Fast fuzzy lookup: returns best vendor match (if any) for each descriptor
    cands = vendor_table["vendor_canonical"].tolist()
    matches = []
    for s in descriptors:
        best = process.extractOne(s, cands, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
        if best:
            matches.append({"descriptor_norm": s, "vendor_canonical": best[0], "score": best[1]})
        else:
            matches.append({"descriptor_norm": s, "vendor_canonical": None, "score": None})
    return pd.DataFrame(matches)
