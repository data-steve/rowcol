# Escher Autocode v0.1

A lean, auditable autocoding engine for Book → Close. Deterministic first, ML later.
Works on CSV exports (bank/credit-card). Outputs categorized transactions with confidence and rule explanations.

## Quick Start

1) **Install** (Python 3.10+ recommended):
```bash
pip install pandas pyyaml
```

2) **Project files**
- `engine.py` — core rule engine
- `cli.py` — command-line interface
- `rules.yaml` — your layered rules (edit me)
- `sample/transactions.csv` — sample input
- `sample/corrections.csv` — example corrections file

3) **Run autocoding:**
```bash
python cli.py autocode sample/transactions.csv --rules rules.yaml --out out/coded.csv
```

4) **Apply human corrections to learn new rules:**
- Fill `sample/corrections.csv` (txn_id must match the coded output)
```bash
python cli.py learn sample/corrections.csv --rules rules.yaml --out rules.yaml
```

5) **Re-run with updated rules** and watch the confidence and coverage improve.

## CSV Expectations

Input CSV must have headers (case-insensitive OK):
- `txn_id` (unique per CSV) — if absent, CLI will derive a stable hash-like id
- `date` — YYYY-MM-DD or similar
- `description` — bank descriptor
- `amount` — signed (neg=debit, pos=credit)

Optional columns (if present, will be preserved and available to rules):
- `balance`, `account_name`, `counterparty`, `class`, `location`

## Confidence & Guardrails (defaults)
- `>= 0.90` → **auto_post = True**
- `0.60–0.89` → **review queue**
- `< 0.60` → **flag** (no auto-post)
- No auto-posts directly to Retained Earnings or Cash (enforced as "locked" accounts list).

## Rule Types Supported
- `exact` — full-string match on description/counterparty
- `contains` — substring match
- `regex` — regular expression
- `amount_range` — numeric range match (-100.0 to -50.0, etc.)
- `transfer_heuristic` — identifies likely transfers (same/known counterparty patterns)

Each rule can set: `account`, `class`, `location`, `memo`, `tax_flag`, `confidence`.

## Learning: Deterministic First
The `learn` command converts human corrections into new or updated deterministic rules:
- Scope can be `"client"` or `"global"` (we default to `client` here).
- New rules are added to the top of their rule group (higher priority).
- ML can be layered later using the logged corrections dataset.

## Example
```bash
python cli.py autocode sample/transactions.csv --rules rules.yaml --out out/coded.csv
python cli.py learn sample/corrections.csv --rules rules.yaml --out rules.yaml
python cli.py autocode sample/transactions.csv --rules rules.yaml --out out/coded.csv
```

## Notes
- Keep your **locked accounts** list updated (see `engine.py` defaults).
- Tie-outs and JE creation are **downstream** of this step; this engine only assigns categories + metadata and never posts to GL.
- For QBO/Xero integration, wrap `engine.autocode()` and post only rows where `auto_post == True`.

— Escher / Cloudfirms
