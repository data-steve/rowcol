import os, json, math
import pandas as pd
import requests
from pathlib import Path
from typing import Dict, Any
from tqdm import tqdm

RAW = Path("data/raw")

def get_json(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def download_usaspending(cfg: dict) -> Path:
    if not cfg.get("enabled", False):
        return None
    # We'll pull NAICS reference and a recipient listing sample (open endpoints)
    # Note: API structure may change; adjust as needed.
    # For bootstrap, we fetch the NAICS reference tree (single call) and a limited recipient listing.
    ref_path = RAW / "usaspending_naics.json"
    if not ref_path.parent.exists():
        ref_path.parent.mkdir(parents=True, exist_ok=True)
    # Reference endpoint
    ref_url = cfg.get("endpoint")
    try:
        data = get_json(ref_url)
        ref_path.write_text(json.dumps(data))
    except Exception as e:
        print("[WARN] Could not fetch NAICS reference from USASpending:", e)

    # Recipient listing — sample
    recip_path = RAW / "usaspending_recipients_sample.json"
    try:
        url = "https://api.usaspending.gov/api/v2/recipient/"
        # The recipient endpoint supports pagination; we pull a few pages.
        max_pages = int(cfg.get("max_pages", 3))
        page_size = int(cfg.get("page_size", 1000))
        all_rows = []
        for page in tqdm(range(1, max_pages+1), desc="USASpending recipients"):
            payload = {"page": page, "limit": page_size, "ordering": "recipient_name"}
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            js = r.json()
            results = js.get("results", [])
            for row in results:
                all_rows.append({
                    "recipient_name": row.get("recipient_name"),
                    "uei": row.get("uei"),
                    "duns": row.get("duns"),
                    "parent_uei": row.get("parent_uei"),
                    "state": row.get("location", {}).get("state_code"),
                })
        pd.DataFrame(all_rows).to_csv(RAW / "usaspending_recipients_sample.csv", index=False)
        recip_path.write_text("ok")
    except Exception as e:
        print("[WARN] Could not fetch recipients sample from USASpending:", e)

    return recip_path

def ensure_mcc_reference(cfg: dict) -> Path:
    path = RAW / "mcc_reference.csv"
    if cfg.get("url"):
        try:
            df = pd.read_csv(cfg["url"])
            df.to_csv(path, index=False)
            return path
        except Exception as e:
            print("[WARN] Failed to download MCC reference; using seed:", e)
    # fallback seed
    seed = RAW / "mcc_reference_seed.csv"
    seed.rename(path, overwrite=True)
    return path

def ensure_naics_reference(cfg: dict) -> Path:
    path = RAW / "naics_reference.csv"
    if cfg.get("url"):
        try:
            df = pd.read_csv(cfg["url"])
            df.to_csv(path, index=False)
            return path
        except Exception as e:
            print("[WARN] Failed to download NAICS reference; using seed:", e)
    seed = RAW / "naics_reference_seed.csv"
    seed.rename(path, overwrite=True)
    return path
