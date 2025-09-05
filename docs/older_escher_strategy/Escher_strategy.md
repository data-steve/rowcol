# Escher Strategy

## Overview
Escher is the company behind BookClose, a white-label, automation-first monthly close service designed to transform bookkeeping for accounting firms. By automating 70-80% of the book-to-close process, Escher enables firms to reduce manual work, enhance efficiency, and focus on high-value advisory services. Positioned as a hybrid service-technology provider, Escher offers a scalable solution that integrates seamlessly with QuickBooks Online (QBO), targeting small-to-mid-size firms with a D+5 close SLA and audit-ready deliverables.

## Positioning
- **Model**: White-label close service running under firm branding; future SaaS licensing for broader adoption.
- **Edge**: Automation-first, proven in a “service lab” (pilot clients), scalable to multi-firm operations with controller-level insights (e.g., AR creep, margin compression).
- **Endgame**: High-margin service arm with acquisition potential (e.g., by RowCol/CloudFirms) and technology licensing to accounting platforms.

## Market Outreach
- **Target Firms**:
  - **No CAS Team**: Small firms or regional CPAs needing turnkey close solutions (easiest early wins).
  - **Frustrated CAS Teams**: Mid-size firms seeking efficiency gains for existing teams (higher barrier, larger capacity upside).
- **Strategy**:
  - Identify 20+ pilot firms via LinkedIn Sales Navigator, CPA society directories, and AccountingToday Top 100.
  - Outreach message: “Join Escher to shape a white-label close service that automates 70-80% of your bookkeeping, delivering audit-ready binders by D+5.”
  - Deliverable: Spreadsheet of firm contacts, interest levels, and pilot potential (aim for 1-2 pilot firms, 3-5 clients).
- **Competitive Analysis**:
  - Analyze Keeper, ClientHub, Karbon, Financial Cents, Jetpack Workflow for feature parity, pricing, and UX gaps.
  - Key differentiators: BookClose’s automation depth (70-80% vs. Keeper’s manual-heavy workflows), QBO-deep integration (webhooks, CDC), and white-label branding.
  - Deliverable: Teardown doc with features, pricing, screenshots, and Escher’s unique value proposition.

## Standard Operating Procedure (SOP)
### Daily/Weekly Workflows
- **AP**: Collect bills (API, portal, email, lockbox for paper), code to COA, schedule payments (QBO/Melio), reconcile vendor statements.
- **AR**: Create/send invoices (pull from POS/CRM), apply payments, follow up on collections, manage credit memos.
- **Bank/CC**: Match feeds to transactions, record transfers, handle manual entries for non-feed accounts.
- **Inventory**: Track receipts, sales, and adjustments; perform spot counts for high-value SKUs.
- **Payroll**: Post journals, remit taxes/benefits, handle adjustments (e.g., benefits, garnishments).

### Close Process
1. **Ingest & Normalize**: Sync QBO data (COA, transactions, vendors, reports) into a canonical schema; normalize vendors (strip tokens, uppercase).
2. **Auto-Classify & Suggest**: Apply rules (e.g., `STRIPE PAYOUT` → `Clearing:Stripe`) for 70-80% transaction categorization; queue mid-confidence items (0.6-0.89) for review.
3. **Reconcile & Resolve**: Perform bank/CC/subledger tie-outs, flag discrepancies, chase missing documents via Provided by Client (PBC) requests.
4. **Variance Review**: Flag MoM/YoY deltas (>10% or $2500), explain with tickmarks (✓=reconciled, Δ=JE, A=accrual, P=prepaid, T=tie-out, V=variance).
5. **Deliverables**: Generate working binder (Excel), final binder (PDF) with cover, index, tickmark legend, BS/IS tabs, JEs, close summary narrative, management commentary, and AP/AR snapshots.

### Close Calendar
- **D-3 to D-1**: Issue PBC requests (bank statements, payroll, inventory).
- **D+0**: Freeze GL, sync QBO data, start bank/CC reconciliations.
- **D+2**: Complete subledger tie-outs, post accruals (payroll, AP, revenue).
- **D+3**: Conduct variance analysis, draft working binder.
- **D+4**: Perform internal QA, send to firm reviewer.
- **D+5**: Incorporate reviewer notes, issue final binder.

## Pricing Model
- **Tiers**:
  - **Tier 1 (Low)**: <200 txns/mo, 1 entity, 1 bank feed; $500-$750/mo; 70% margin.
  - **Tier 2 (Medium)**: 2-4 entities, light inventory; $1000-$1500/mo; 60% margin.
  - **Tier 3 (High)**: Multi-entity, heavy inventory, exceptions; $2000+/mo; 50% margin.
- **Onboarding Fee**: Covers cleanup (1.5x-2x ongoing rate).
- **Add-Ons**:
  - Weekly cadence: +25-40%.
  - PBC chasing: $50-$150/mo.
  - AP/AR management: $150-$400/mo.
  - Year-end prep (e.g., 1099s): $100-$250/mo.
  - Management reporting: $150-$500/mo.
- **Philosophy**: Price 20-30% below in-house costs; premium for review efficiency (<5 review notes per binder).

## L6 Role
- **Responsibilities**:
  - Own delivery for 3-5 pilot clients across 1-2 firms.
  - Standardize close processes, documentation, and tickmarks.
  - Train automation rules by identifying patterns (e.g., vendor keywords, recurring JEs).
  - Flag tasks for automation (e.g., AP ingestion, bank reconciliation).
  - Translate Escher’s vision into firm workflows, ensuring reviewer empathy.
- **Impact**: Bridges tech and operations, ensuring BookClose aligns with firm needs and delivers consistent, audit-ready outputs.

## Offshore Strategy
- **Tasks**: AR collections, vendor disputes, historical cleanup, manual reconciliations, complex accruals.
- **Execution**: Route to offshore staff via task queue (`categorization_queue.html`); price into tiers to maintain margins.
- **Benefit**: Frees onshore team for high-value tasks (review, insights).

## Advisory Boundaries
- **Scope**: Controller-level insights (AR over 90 days, cash flow dips, margin compression) surfaced in close summary narrative.
- **Out-of-Scope**: Tax structuring, speculative forecasting, M&A recommendations.
- **Value**: Enables firms to resell insights as advisory services without requiring CPA licensing.

## Pilot Strategy
- **Setup**: Engage 1-2 firms with 3-5 clients (QBO sandbox or small real clients).
- **Process**: Run manual closes for 1-2 cycles to log pain points; iterate automation rules and SOP starting with Stage 0 (QBO sync, rules, onboarding).
- **Metrics**:
  - Automation penetration: % transactions auto-suggested/accepted.
  - Time-to-close: Days from period end to binder delivery.
  - Review hours saved: Compared to baseline manual process.
  - Error rate: Post-close adjustments required.
  - Client satisfaction: Partner feedback or NPS scores.

## Backlog
- Xero/NetSuite integrations.
- Year-end prep (1099/1096, fixed asset additions, retained earnings reconciliation).
- Tax prep alignment.
- CRM integration.

## Parking Lot
- ML-based categorization and variance commentary (Phase 3).
- OCR for document ingestion (Phase 3).
- Lockbox scanning for paper-based clients (Phase 3).
- Real-time P&L reporting (Phase 3).
- Named Entity Recognition (NER) for vendor extraction.
- Multi-entity accounting (deferred to Backlog if needed).