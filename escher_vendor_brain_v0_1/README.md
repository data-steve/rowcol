# Escher Vendor Brain v0.1

Bootstraps vendor normalization & category mapping for Book→Close automation.

**What it does**

- Pulls **USASpending** vendor data (NAICS-coded) and MCC/NAICS reference files.
- Normalizes business names and bank descriptors (case, punctuation, tokens).
- Builds a **vendor → COA category** table using **MCC** primary, **NAICS** fallback.
- Emits artifacts:
  - `data/out/vendor_canonical.csv` (canonical vendor table)
  - `data/out/rules.yaml` (deterministic rules for Escher Autocode)
  - `data/out/mcc_to_coa_map.csv` / `naics_to_coa_map.csv` (reference maps)

**Why this matters**

This gives you a high‑coverage seed so juniors/AI only handle true edge cases. Deterministic, explainable, and easy to extend per‑client.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Configure sources & COA in config/
python src/build.py  # end-to-end: download → clean → map → emit artifacts
```

Outputs land in `data/out/`.

---

## Configuration

- `config/data_sources.yaml` – endpoints and fetch toggles.
- `config/coa_map.yaml` – your Standard Chart of Accounts mapping for MCC/NAICS.
- `config/normalize.yaml` – tokens to strip and normalization choices.

`SAM.gov` can be added later (requires API key). USASpending is open.

---

## Integration with Escher Autocode

- Copy `data/out/rules.yaml` into your autocode project.
- Or point your engine at `vendor_canonical.csv` to apply exact/contains rules first,
  then fall back to regex/heuristics.

---

## Notes

- This pipeline is **deterministic-first**. ML can be layered later using the correction logs.
- State registries vary widely; this repo ships with a plugin slot (`src/plugins/state_*`) to add them incrementally.
- A tiny seed dataset is included so you can run without internet and see the whole flow.

— Generated 2025-08-11
