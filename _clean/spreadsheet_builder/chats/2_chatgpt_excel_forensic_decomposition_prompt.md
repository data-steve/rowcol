
## Attach both files when you run it: `design_meetings/mfo_cash_forecast_8.1.25.xlsx` and `design_meetings/spreadsheet_layout_color_coding.png`.


You are an expert Excel forensic analyst and technical writer. I’m building an MVP that auto‑generates this exact workbook from QBO data. Please fully decompose the attached Excel and produce a paste‑ready Markdown section for my repo file `_clean/spreadsheet_builder/ROWCOL_MVP_PRODUCT_SPECIFICATION.md`.

Context:
- Product: RowCol MVP (cash forecast automation for CAS firms)
- Goal: Precisely replicate this workbook from QBO (beginning cash + AR/AP timing + payroll + recurring vendors), preserving formulas and layout.
- Files attached:
  - mfo_cash_forecast_8.1.25.xlsx (primary)
  - spreadsheet_layout_color_coding.png (legend/reference)

What to deliver (structure and depth matter):
1) Workbook overview
   - List all worksheets with visibility (visible/hidden) in order.
   - For each: purpose, inputs, outputs, and relationships to other sheets.
   - If helpful, include a one‑line “role” per sheet.

2) Sheet‑by‑sheet deep dive (most important)
   For each worksheet, document:
   - Core layout: header rows, month header row, first month column, month count, and the roll‑forward pattern (e.g., EOMONTH).
   - Row blocks with exact row numbers (e.g., “Row 2: Beginning Cash”, “Rows 4–24: Inflows/Recurring”, “Row 25: Total Inflows”, “Rows 27–38: Outflows/Recurring”, “Row 39: One‑time”, “Row 42: Payroll”, etc.). Use the actual row numbers from this file.
   - 5–10 representative formulas with exact cell addresses as they appear (e.g., `C63 = C2 + C62`, `D2 = C63`, `C60 = SUM(C4,C8)`, `month headers = EOMONTH(...)`).
   - Named ranges (if any) and what they cover.
   - External references within the workbook (e.g., “Summary” pulling from “RA Edits…”, “Details by Vendor” feeding Outflows).
   - If a sheet is a variant (e.g., “Cash Flow-Ops”, “Cash Flow wsavings”), call out what differs (rows added/removed, different groupings).

3) Color & visual system
   - From the PNG + workbook fills: list the color categories used (name + hex if you can) and the rows/sections they correspond to (e.g., orange = Recurring vendors, magenta = Major gifts, blue = Payroll, etc.).

4) Pivot(s) and summaries
   - Identify pivot tables: source range, fields, and what they summarize.
   - For “Summary By Vendor and Class”, show which sheet/rows it references and the aggregation pattern.

5) YAML “template_map” (implementation contract)
   Output a concise YAML block that my renderer can consume, with exact placements and essentials:
   ```yaml
   template_name: "MissionFirst_Cash_Runway"
   month_header:
     row: <row_num>
     start_col: <letter>     # e.g., C
     month_formula: "<as-in-sheet>"
     horizon: <count>        # number of visible month columns
   rows:
     beginning_cash: <row>
     inflows:
       recurring_row: <row>
       major_row: <row>
       total_row: <row>
     outflows:
       recurring_start_row: <row>
       recurring_end_row: <row>
       one_time_row: <row>
       payroll_header_row: <row>
       payroll_block_start_row: <row>
       payroll_block_end_row: <row>
       pending_or_unmapped_row: <row>    # if present
       total_row: <row>
     net_change_row: <row>
     ending_cash_row: <row>
   formulas:
     ending_cash: "<as-in-sheet>"        # e.g., C63 = C2 + C62; D2 = C63 cascade
     total_inflows: "<cell formula>"
     total_outflows: "<cell formula>"
   ```
   Use the actual row numbers and formulas from this workbook.

6) Data requirements (JSON)
   Provide a JSON block that captures the data we must fetch/compute to populate those cells:
   ```json
   {
     "beginning_cash": { "source": "QBO.BankBalance", "when": "start_of_leftmost_month" },
     "inflows": {
       "from_ar": { "source": "QBO.Invoices.Open", "bucketing": "due_date + historical DPO → month" },
       "major_vs_recurring": { "rule": "amount thresholds and/or recurrence" }
     },
     "outflows": {
       "from_ap": { "source": "QBO.Bills.Open", "bucketing": "due_date (or policy) → month" },
       "recurring_vendors": { "source": "VendorFrequencyMap", "fields": ["vendor","amount","cadence","default_day"] },
       "payroll": { "source": "QBO Payroll or heuristic from historical cycles" }
     },
     "details_by_vendor": { "grid": "vendor × month amounts", "fields": ["vendor","gl","frequency","tag"] }
   }
   ```

7) Rendering contract (cell placements)
   - Enumerate the exact cell ranges the generator must write for each month/section (e.g., “Write recurring inflows to row X, col per month; write payroll totals to row Y, …”). Keep this precise and minimal.

8) Acceptance checks (copy‑pastable)
   - 10–15 concrete assertions (cell‑level) to verify a generated workbook matches the template’s math/flow (e.g., “D2 equals prior month ending cash in C63”, “C60 equals SUM of inflow section anchors”, etc.).

9) Variant guidance
   - Briefly compare “RA Edits‑Cash Flow‑Ops with Sa”, “Cash Flow‑Ops”, and “Cash Flow wsavings”; recommend which to target as the MVP baseline and how to toggle variants from the same renderer.

Important:
- Use the exact worksheet names and visibility from this workbook.
- Include real row numbers, column letters, and formula text as they appear.
- Keep formulas authoritative—renderer should place values and let Excel compute totals/roll‑forward.
- Output only Markdown + the two code blocks (YAML + JSON). No screenshots.
- Be precise and unambiguous; this will be handed to engineers to implement against.

If anything is ambiguous in the workbook, note it under “Open Questions” at the end with suggested resolutions.
