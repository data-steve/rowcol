# Smart Features Reference Library

**Version**: 1.0  
**Date**: 2025-10-01  
**Purpose**: Complete catalog of "smart" features from V6.0 owner-first build plan, translated to advisor-first use cases for RowCol runway/ product

---

## Overview

This document preserves the sophisticated "smart" feature thinking from the V6.0 Oodaloo build plan and translates it for advisor-first RowCol use cases. These features represent the intelligence layer that justifies premium pricing tiers beyond basic spreadsheet replacement.

### Smart Definition (from V6.0)

**Our features are designed to be 'smart' by reducing cognitive load and providing actionable insights at the moment of decision, not through complex AI or over-predictive models.**

Three tiers of intelligence:

1. **Connective Intelligence**: Linking AP, AR, and cash runway in real-time to show cross-domain decision impacts, unlike QBO's siloed approach
2. **Workflow Intelligence**: Transforming a passive ledger into an active decision-making ritual with guided, prioritized actions
3. **Light-Touch Predictive Intelligence**: Offering simple, actionable heuristics (e.g., 'This customer pays in 47 days on average') instead of complex forecasts that create noise

---

## Important Notes

### **Feature Consolidations from V5**
- **Historical Data / Time Travel**: Not a separate feature—folded into Tier 3 analytics and reporting (trend charts, historical snapshots)
- **2-4 Week Forecast vs. 13-Week Forecast**: Sequential builds (2-4 week first, then extend to 13 weeks)
- **Scenario What-If vs. Runway Impact**: Different complexity levels:
  - Runway Impact (Tier 2): "If you do X, runway changes by Y"
  - What-If Scenarios (Tier 3): Compare multiple plans side-by-side

---

## Feature Catalog by Domain

### SMART AP (Accounts Payable Intelligence)

#### **1. Earmarking / Reserved Bill Pay** 
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 12h

**V6.0 Owner Use Case**: Owner earmarks rent payment to ensure it's covered before vacation

**Advisor Use Case**: Advisor earmarks must-pay bills (rent, payroll) so they know money is reserved and won't accidentally approve other bills that would drain needed funds

**Key Insight**: Once earmarked, money is treated as "spent" in available balance calculation, even though QBO hasn't sent payment yet

**Implementation**:
- Add `earmarked` boolean and `earmarked_date` to Bill model
- Calculate `available_balance = current_balance - earmarked_bills`
- Show in UI: "Available: $45k (Current: $52k, Earmarked: $7k)"
- Runway calculation uses available balance, not current balance

**Trade-offs**:
- ✅ Cognitive Load: Don't have to review same bill twice
- ✅ Assurance: Guarantee must-pay bills are covered
- ✅ Available Balance Accuracy: Shows what you CAN spend
- ✅ Vacation Mode: Set it and forget it
- ⚠️ Flip Side: Can't use earmarked money for other bills

**Use Cases**:
1. **Must-pay bills** (rent, payroll): Earmark immediately when due date known
2. **Can-delay bills**: Don't earmark, keep money available for better uses
3. **Vacation planning**: Earmark all essentials before leaving, return to review only discretionary

**Success Criteria**:
- Advisor can earmark bill for future date
- Available balance reflects earmarked amount
- Runway calculation uses available balance
- Can un-earmark if plans change

**Files**:
- `domains/ap/models/bill.py` - Add earmark fields
- `runway/services/runway_calculator.py` - Use available balance
- `runway/routes/bills.py` - Earmark endpoints
- UI components for earmark status badge

---

#### **2. Runway Impact Calculator**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 6h

**V6.0 Owner Use Case**: "Paying this $5k bill now costs 4 days of runway"

**Advisor Use Case**: Show advisor explicit runway delta when making any AP decision: "If you delay this $5k rent to Oct 6, you gain +3 days runway"

**Implementation**:
- Real-time calculation when bill payment date changes
- Formula: `runway_delta = (bill_amount / daily_burn_rate) in days`
- Show in UI: "Delay to Oct 6 → **+3 days runway**"

**Integration Points**:
- Decision Console: Show delta on every bill action
- Earmarking: "Earmarking $7k reduces runway by 5 days BUT protects payroll"
- Batch decisions: "These 3 actions net **+8 days runway**"

**Success Criteria**:
- Every bill action shows runway impact before execution
- Delta is accurate based on current runway calculation
- Positive deltas (gains) shown in green, negative (costs) in red

**Files**:
- `runway/services/runway_impact.py` - New service
- `runway/routes/bills.py` - Include delta in responses
- UI components for delta display

---

#### **3. Latest Safe Pay Date Calculation**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 8h

**V6.0 Owner Use Case**: "You can safely delay this bill until Oct 6 without late fees"

**Advisor Use Case**: For bills with known payment terms, calculate the absolute latest date to pay without penalties. Useful for advisory conversations: "We can delay this 14 more days without risking the relationship"

**Implementation**:
- Parse payment terms from bill (Net 30, 2/10 Net 30, etc.)
- Calculate: `latest_safe_date = due_date` (or invoice_date + term days)
- Factor in vendor relationship history (if available)
- Show in UI: "Safe to delay until Oct 6 (Net 30 terms)"

**Why Tier 3**: Requires vendor relationship tracking, payment terms management - more sophisticated than basic earmarking

**Success Criteria**:
- Accurate calculation for standard payment terms
- Shows days remaining until latest safe date
- Integrates with runway impact calculator

**Files**:
- `domains/ap/services/payment_terms.py` - New service
- `domains/ap/models/vendor.py` - Add payment_terms field
- `runway/services/runway_impact.py` - Integrate safe date logic

---

#### **4. Statement Reconciliation / Credit Card Matching**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 12h

**V6.0 Owner Use Case**: Match Amex statement charges to QBO bills

**Advisor Use Case**: Client has Amex statement with 20 charges. Auto-match to existing QBO bills or flag as new bills needing entry. Critical for accurate AP when clients use credit cards heavily.

**Implementation**:
- Pull credit card transactions from QBO (via bank feeds)
- Match to existing bills by: amount, date range, vendor name
- Confidence scoring: 95% match = auto-match, <80% = manual review
- Unbundle charges: Single payment → multiple bills

**Why Important**: Many clients pay bills via credit card, creating reconciliation complexity

**Success Criteria**:
- Auto-match 70%+ of credit card charges to bills
- Flag unmatched charges for review
- Show confidence scores for manual review
- Handle partial matches (e.g., bill + fee)

**Files**:
- `domains/ap/services/statement_reconciliation.py` - Already exists, needs enhancement
- `domains/bank/services/transaction_matching.py` - New matching logic
- `runway/routes/reconciliation.py` - API endpoints

---

#### **5. Vendor Normalization & Consolidation**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 4h (already built, just integrate)

**V6.0 Owner Use Case**: Consolidate "Amazon.com", "Amazon Inc", "AMZN" → one vendor

**Advisor Use Case**: Clean vendor data for accurate reporting. "Your client has 47 vendors, but 12 are duplicates of 5 actual vendors"

**Implementation**:
- `domains/vendor_normalization/` already exists in codebase
- Fuzzy matching algorithm for vendor names
- Suggest consolidations with confidence scores
- Batch apply across all clients

**Why Important**: Critical for clean reporting, spend analysis, payment terms tracking

**Success Criteria**:
- Auto-suggest vendor consolidations with 85%+ accuracy
- One-click batch consolidation
- Undo capability if incorrect

**Files**:
- `domains/vendor_normalization/services/normalizer.py` - Exists
- `runway/routes/vendors.py` - Expose consolidation UI

---

### SMART AR (Accounts Receivable Intelligence)

#### **6. 3-Stage Collection Workflows**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 15h

**V6.0 Owner Use Case**: Automated 3-stage email drip for owner's overdue customers

**Advisor Use Case**: Advisor triggers 3-stage collection sequence on behalf of client. Emails sent from client's email (via SendGrid) to client's customers.

**Collection Stages**:
1. **Day 0-30**: Gentle reminder ("Friendly check-in about Invoice #123")
2. **Day 31-60**: Urgent follow-up ("Payment now 30 days past due")
3. **Day 61+**: Final notice ("Final reminder before escalation")

**Implementation**:
- Template library for each stage
- Advisor triggers for specific invoices or auto-triggers at thresholds
- Auto-pause when payment detected (via QBO sync)
- Track attempts per customer in database

**Customization**:
- Per-client timing (some clients: 30/60/90, others: 45/75/105)
- Custom message overrides
- BCC advisor on all emails for transparency

**Why Tier 2**: Core async advisory tool - advisor manages collections without constant client contact

**Success Criteria**:
- Advisor can trigger sequence with 2 clicks
- Auto-pause on payment (checked daily via QBO sync)
- Template library covers common scenarios
- Track success rate per customer

**Files**:
- `domains/ar/services/collections.py` - Enhance existing
- `runway/services/collection_workflows.py` - Orchestration
- `infra/email/templates/collections/` - Email templates
- `runway/routes/collections.py` - API endpoints

---

#### **7. Bulk Payment Matching / Stripe Unbundling**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 15h

**V6.0 Owner Use Case**: (Not in V6.0 - new for advisor-first)

**Advisor Use Case**: E-commerce or service pro clients take Stripe/Square payments bundled across multiple invoices. Need to unbundle: "$5,000 Stripe deposit" → Invoice #123 ($2k) + Invoice #124 ($1.5k) + Invoice #125 ($1.5k)

**Implementation**:
- Detect bulk deposits from payment processors (Stripe, Square, PayPal)
- Match deposit total to sum of multiple invoices
- Confidence scoring: 
  - 100% match = auto-apply
  - 95-99% match = suggest with high confidence
  - <95% match = manual review
- Handle processor fees: $5k deposit might be $5,150 invoices - $150 fee

**Why Critical**: Without this, runway accuracy breaks for e-commerce clients. Can't just match 1:1 like professional services.

**Success Criteria**:
- Auto-match 80%+ of bulk deposits to correct invoices
- Show confidence scores for manual review
- Handle common processor fee structures
- Support Stripe, Square, PayPal patterns

**Files**:
- `domains/ar/services/payment_matching.py` - Exists, needs enhancement
- `domains/ar/services/payment_unbundling.py` - New service
- `runway/routes/payment_matching.py` - API endpoints

---

#### **8. AR Priority Scoring**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 6h

**V6.0 Owner Use Case**: Prioritize which customers to chase first

**Advisor Use Case**: Show advisor which invoices to prioritize for collections based on: amount, age, customer payment history, runway impact

**Scoring Algorithm**:
```python
priority_score = (
    (invoice_amount / 1000) * 2 +  # Amount weight (larger = higher priority)
    (days_overdue / 10) * 3 +       # Age weight (older = higher priority)
    customer_risk_multiplier * 2 +  # History weight (risky = higher priority)
    (runway_impact_days) * 1.5      # Runway weight (bigger impact = higher)
)
```

**Customer Risk Levels**:
- **Reliable** (avg pay 25 days): Low priority unless very overdue
- **Slow** (avg pay 55 days): Medium priority
- **Risky** (avg pay 90+ days or history of non-payment): High priority

**Implementation**:
- Calculate score for each overdue invoice
- Sort collection tray by score (descending)
- Show score components in UI: "High Priority: $8k, 47 days overdue, risky customer, 6 days runway impact"

**Success Criteria**:
- Scoring algorithm validates with advisor feedback
- Top 3 scored invoices match advisor intuition 85%+ of time
- Score updates in real-time as invoices age

**Files**:
- `domains/ar/services/priority_scoring.py` - New service
- `domains/ar/services/customer.py` - Add risk calculation
- `runway/routes/collections.py` - Include scores in API

---

#### **9. Customer Payment Profiles**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 8h

**V6.0 Owner Use Case**: "This customer pays in 47 days on average"

**Advisor Use Case**: Historical payment patterns for forecasting and advisory conversations. "Customer A typically pays in 52 days. This invoice is 60 days overdue, so it's outside their normal pattern - worth escalating."

**Profile Data**:
- Average days to pay
- Payment variance (consistent vs. erratic)
- Preferred payment method
- Seasonal patterns
- Contact responsiveness

**Use Cases**:
1. **Forecasting**: Predict when AR will convert to cash for runway projections
2. **Advisory conversations**: "Here's why I'm prioritizing Customer A over B"
3. **Collection timing**: Don't chase reliable customer at 35 days if they always pay at 45

**Why Tier 3**: This is an insight for advisory deliverables, not day-to-day operations

**Success Criteria**:
- Track payment history for each customer
- Calculate average and variance
- Show in collection UI: "Typical pay time: 45 days (±7)"
- Use in forecasting: "Expected $25k AR conversion in next 14 days"

**Files**:
- `domains/ar/models/customer.py` - Add profile fields
- `domains/ar/services/payment_profiles.py` - New service
- `runway/services/forecasting.py` - Integration

---

### SMART HYGIENE (Data Quality Intelligence)

#### **10. Smart Hygiene Prioritization**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 10h

**V6.0 Owner Use Case**: Detect data quality issues

**Advisor Use Case**: Prioritize which data quality issues to fix based on runway impact. "Fix these 5 issues to unlock 8 days runway accuracy"

**Hygiene Issue Types**:
1. **Critical** (blocks runway calculation):
   - Unmatched bank deposits
   - Bills missing due dates
   - Negative balances
   - Duplicate transactions
   
2. **High** (affects runway accuracy):
   - Invoices missing customer
   - Bills missing vendor
   - Uncategorized transactions
   
3. **Medium** (affects reporting):
   - Duplicate vendors
   - Missing payment terms
   - Old unresolved items

**Smart Prioritization**:
- Calculate runway impact of each issue
- Show: "5 unmatched deposits worth $15k = 11 days runway uncertainty"
- Batch fix capability: "Fix all critical issues (8 items)"

**Implementation**:
- Scan QBO data for common issues
- Calculate impact on runway accuracy
- Sort by impact (descending)
- One-click fixes where possible

**Success Criteria**:
- Detect 90%+ of common hygiene issues
- Accurate runway impact calculation
- Advisor can fix 70%+ of issues in <5 minutes
- Track data quality score over time

**Files**:
- `runway/services/hygiene_analyzer.py` - New service
- `domains/core/services/data_quality.py` - Issue detection
- `runway/routes/hygiene.py` - API endpoints

---

#### **11. Data Quality Scoring**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 6h

**V6.0 Owner Use Case**: "Your books are 87% clean"

**Advisor Use Case**: Show client data quality vs. industry average. "Your books are 92% clean, vs. 78% average for similar clients"

**Scoring Components**:
- **Bank reconciliation**: 100% matched deposits/withdrawals
- **AP completeness**: 95%+ bills have due dates, vendors
- **AR completeness**: 90%+ invoices have customers, payment terms
- **Categorization**: 95%+ transactions categorized
- **Duplicates**: <1% duplicate entries

**Overall Score**: Weighted average of components

**Why Tier 3**: This becomes a deliverable in client reports - "Here's your financial health score"

**Success Criteria**:
- Accurate score calculation
- Show score trend over time
- Benchmark against peer clients
- Actionable recommendations: "Add due dates to 12 bills to reach 95%"

**Files**:
- `domains/core/services/data_quality_scoring.py` - New service
- `runway/routes/analytics.py` - Include in analytics API

---

### SMART ANALYTICS (Forecasting & Insights)

#### **12. Cash Flow Forecasting (2-4 weeks)**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 12h  
**Note**: This is a **prerequisite** for 13-week forecast (also Tier 3, 25h additional)

**V6.0 Owner Use Case**: Predict runway 2-4 weeks out

**Advisor Use Case**: "Based on patterns, your client's runway will be 38 days in 2 weeks" - helps advisor plan proactively

**Forecasting Method** (light-touch, not complex ML):
- Historical burn rate trend (last 8 weeks)
- Known upcoming AP (bills due in next 30 days)
- Expected AR (based on customer payment profiles)
- Seasonal adjustments (if pattern detected)

**Confidence Bands**:
- High confidence (±3 days): Next 7 days
- Medium confidence (±7 days): 8-14 days
- Low confidence (±12 days): 15-30 days

**Implementation**:
- Calculate daily: `forecast_runway = current_runway + expected_AR - expected_AP - (daily_burn * days)`
- Adjust for known events: "Big invoice expected Oct 10 → runway spike"
- Show as line chart with confidence band

**Why Tier 3**: Advisory insight, not operational necessity

**13-Week Forecast Extension**: Once 2-4 week forecasting is working, extend to 13 weeks with similar logic but wider confidence bands (Tier 3, additional 25h).

**Success Criteria**:
- 90%+ accuracy over 7-day window
- 75%+ accuracy over 14-day window
- Clear confidence indicators
- Updates daily

**Files**:
- `runway/services/forecasting.py` - New service (V6.0 had `ForecastingService`, enhance it)
- `runway/routes/analytics.py` - API endpoints

---

#### **13. Variance Alerts / Drift Detection**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 6h

**V6.0 Owner Use Case**: "Runway shortened by 7 days today from 3 bills + 1 missed AR"

**Advisor Use Case**: Alert advisor when client's runway changes significantly. Aggregate multiple events into one alert to avoid spam.

**Alert Triggers**:
- Runway drops >5 days in single day
- Multiple bills entered at once
- Large unexpected expense
- Expected AR payment doesn't arrive

**Aggregation**:
- Don't send 5 alerts for 5 bills
- Send 1 alert: "Client X: Runway dropped 8 days today from 4 new bills ($23k total)"

**Implementation**:
- Track daily runway snapshots
- Calculate delta: `runway_change = today_runway - yesterday_runway`
- If |change| > threshold, aggregate events and alert
- Show event breakdown: "3 bills ($15k), 1 missed AR ($8k)"

**Success Criteria**:
- <1 alert per client per day on average
- Actionable alerts (advisor can immediately see what changed)
- Configurable thresholds per client

**Files**:
- `runway/services/variance_detection.py` - New service
- `infra/notifications/alert_service.py` - Email/Slack alerts
- `runway/routes/alerts.py` - API endpoints

---

#### **14. Industry Benchmarking (RMA Integration)**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 15h

**V6.0 Owner Use Case**: "Your AR turnover is 8.2x vs. industry median 6.5x"

**Advisor Use Case**: Provide credible industry benchmarks for client advisory conversations. Uses RMA Annual Statement Studies data.

**Benchmark Metrics**:
- **Current Ratio**: Current assets / current liabilities
- **AR Turnover**: Revenue / average AR
- **AP Days**: (AP / COGS) * 365
- **Debt-to-Worth**: Total liabilities / net worth
- **Sales/Working Capital**: Revenue / (current assets - current liabilities)

**NAICS Codes for RowCol Clients**:
- 541810: Advertising Agencies
- 541613: Marketing Consulting
- 541511: Custom Computer Programming
- 541512: Computer Systems Design

**Data Source**: RMA Annual Statement Studies (licensed data)

**Implementation**:
- Pull client financial data from QBO
- Calculate ratios
- Match to NAICS code (manual or auto-classify)
- Compare to RMA percentile data (25th, median, 75th)
- Show: "Your current ratio: 1.8 vs. Industry range: 1.2-2.1"

**Why Tier 3**: High-value advisory insight that justifies premium pricing

**Success Criteria**:
- Accurate ratio calculations (match CPA standards)
- RMA data integration (API or manual data entry)
- Clear visual comparisons (client vs. industry)
- Historical self-comparison: "Your improvement vs. 6 months ago"

**Files**:
- `runway/services/industry_benchmarks.py` - New service
- `runway/services/financial_ratios.py` - Ratio calculations
- `runway/routes/analytics.py` - API endpoints

---

### SMART BUDGETING & PLANNING

#### **15. Vacation Mode Planning**
**Tier**: 2 (Smart Runway Controls)  
**Effort**: 8h

**V6.0 Owner Use Case**: Owner going on vacation, pre-approve essential bills

**Advisor Use Case**: Advisor going on vacation (or just planning ahead), earmark all essential bills for next 2-4 weeks. Return from vacation to review only discretionary items.

**Implementation**:
- Mark bills as "essential" (rent, payroll, utilities) vs. "discretionary"
- Vacation mode: Auto-earmark all essentials for date range
- Show summary: "14 bills earmarked ($32k), 8 bills queued for your return ($6k)"
- Optional: Auto-approve essentials (advisor risk tolerance)

**Use Cases**:
1. **Vacation**: Set it before leaving, forget about work
2. **Planning ahead**: Batch decisions for multiple weeks at once
3. **New client**: Set up essential/discretionary for ongoing management

**Success Criteria**:
- One-click vacation mode activation
- Clear essential/discretionary categorization
- Return summary: "Welcome back! 3 new bills need review ($4k)"
- Optional auto-approval with configurable rules

**Files**:
- `runway/services/vacation_mode.py` - New service
- `domains/ap/models/bill.py` - Add is_essential field
- `runway/routes/vacation.py` - API endpoints

---

#### **16. Decision-Time Guardrails**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 10h

**V6.0 Owner Use Case**: Real-time budget checking during payment approval

**Advisor Use Case**: Set budget limits per category (e.g., "Marketing: $5k/month"). When approving bill, see: "⚠️ This $2k marketing bill exceeds monthly budget by $500"

**Guardrail Types**:
1. **Category budgets**: Monthly spend limits by GL account
2. **Runway thresholds**: Alert if approval drops runway below 30 days
3. **Cash reserves**: Don't approve if it dips into reserved funds

**Implementation**:
- Set budgets per client per category
- Real-time checking during bill approval
- Warning modal: "This approval violates budget. Proceed anyway?"
- Track overrides for client conversation

**Why Tier 3**: Strategic planning tool, not operational necessity

**Success Criteria**:
- Prevent 70%+ budget violations before they happen
- Clear override workflow (advisor can still approve)
- Track for client reporting: "You overrode budget 3 times this month"

**Files**:
- `runway/services/budgets.py` - New service
- `runway/services/guardrails.py` - Real-time checking
- `runway/routes/bills.py` - Integrate checks

---

#### **17. What-If Scenario Planning**
**Tier**: 3 (Advisory Deliverables)  
**Effort**: 12h

**V6.0 Owner Use Case**: "What if I delay rent 2 weeks?"

**Advisor Use Case**: Show client different scenarios in advisory meeting. "Scenario A: Pay all bills now (38 days runway). Scenario B: Delay rent 2 weeks (46 days runway)."

**Scenario Types**:
1. **Delay bill**: Move payment date, see runway impact
2. **Accelerate AR**: "What if Customer A pays early?"
3. **Toggle reserve**: "What if we use emergency fund?"

**Implementation** (simple, not complex multi-scenario sandbox):
- Base scenario = current state
- One overlay scenario at a time
- Recalculate runway with changes
- Show delta: "+8 days runway in Scenario B"

**UI**: Side-by-side comparison or toggle view

**Why Tier 3**: Advisory conversation tool, not day-to-day operations

**Success Criteria**:
- Easy to create scenarios (drag bill to new date)
- Accurate runway recalculation
- Clear delta display
- No data mutation (scenarios are projections only)

**Files**:
- `runway/services/scenarios.py` - New service
- `runway/routes/scenarios.py` - API endpoints

---

### SMART AUTOMATION (Tier 4)

#### **18. Budget-Based Automation Rules**
**Tier**: 4 (Automation + Practice Scale)  
**Effort**: 20h

**V6.0 Owner Use Case**: Automate bill approvals based on budget rules

**Advisor Use Case**: Set rules: "If balance > $50k AND bill < $500 AND category = 'Software', auto-approve." Automation with awareness and oversight.

**Rule Engine**:
- Condition: Balance threshold, bill amount, category, vendor
- Action: Auto-approve, earmark, alert advisor
- Confidence scoring: Show % of past bills that would match rule

**Guardrails**:
- Dry-run mode: Show what WOULD happen without executing
- Daily digest: "3 bills auto-approved today ($1,200 total)"
- Emergency stop: One-click pause all automation
- Audit trail: Every automated action logged

**Implementation**:
- Rule builder UI (condition + action)
- Background job: Run rules daily against new bills
- Confidence scoring: Test rule against historical data
- Override capability: Advisor can reverse any automated action

**Why Tier 4**: Advanced automation for advisors managing many clients

**Success Criteria**:
- 95%+ rule execution success rate
- Zero unintended approvals (dry-run prevents mistakes)
- Advisor trust: They actually enable automation
- Time savings: 2-3 hours/week per client

**Files**:
- `runway/services/automation_rules.py` - New service
- `runway/services/rule_engine.py` - Execution engine
- `infra/jobs/automation_job.py` - Background processor
- `runway/routes/automation.py` - API endpoints

---

#### **19. Conditional Scheduled Payments**
**Tier**: 4 (Automation + Practice Scale)  
**Effort**: 15h

**V6.0 Owner Use Case**: "Approve payment if balance > $50k by Oct 6"

**Advisor Use Case**: "Schedule rent payment for Oct 6, but only if balance is above $45k. Otherwise, alert me." Future-proofing against cash crunches.

**Implementation**:
- Extend scheduled payments with conditions
- Condition types:
  - Balance threshold: "Only if balance > $X"
  - Runway threshold: "Only if runway > 30 days"
  - AR collection: "Only if Customer A pays first"
- Background job checks conditions daily
- If condition fails on due date, alert advisor

**Use Cases**:
1. **Rent payment**: Schedule for 1st of month, but only if balance is healthy
2. **Vendor payment**: Pay after big customer invoice clears
3. **Discretionary**: Approve bonus payment only if profit target hit

**Why Tier 4**: Sophisticated automation for complex clients

**Success Criteria**:
- Conditions checked accurately daily
- Advisor alerted immediately if condition fails
- Can modify conditions before due date
- Audit trail of condition checks

**Files**:
- `runway/services/conditional_payments.py` - New service
- `infra/jobs/payment_conditions_job.py` - Background checker
- `runway/routes/bills.py` - Extended API

---

#### **20. Runway Protection Automation**
**Tier**: 4 (Automation + Practice Scale)  
**Effort**: 12h

**V6.0 Owner Use Case**: Automate payment timing to protect runway

**Advisor Use Case**: Set global rule: "Never let runway drop below 30 days." System auto-delays non-essential bills if approval would breach threshold.

**Protection Rules**:
1. **Runway floor**: Minimum runway days (e.g., 30)
2. **Essential override**: Payroll/rent can breach floor, others can't
3. **Automatic rescheduling**: Delay non-essentials until runway recovers

**Implementation**:
- Check runway impact before every approval
- If approval would breach floor:
  - Essential: Warn advisor but allow
  - Non-essential: Auto-delay to later date, notify advisor
- Recalculate daily: "Runway recovered, 3 delayed bills now safe to approve"

**Why Tier 4**: Sophisticated guardrail for peace of mind

**Success Criteria**:
- Zero runway breaches for non-essential bills
- Advisor override capability for emergencies
- Clear communication: "Delayed until Oct 15 to protect runway"
- Historical tracking: "Prevented 12 runway breaches this quarter"

**Files**:
- `runway/services/runway_protection.py` - New service
- `runway/services/automation_rules.py` - Integration
- `runway/routes/bills.py` - Approval logic

---

## Feature Tier Summary

### Tier 1: Spreadsheet Replacement ($50/client/month)
**NO "Smart" features** - Just visibility and basic decisions

### Tier 2: Smart Runway Controls ($150/client/month)
- Earmarking / Reserved Bill Pay
- Runway Impact Calculator
- Vacation Mode Planning
- 3-Stage Collection Workflows
- Bulk Payment Matching / Stripe Unbundling
- AR Priority Scoring
- Smart Hygiene Prioritization
- Variance Alerts / Drift Detection
- Statement Reconciliation
- Vendor Normalization

### Tier 3: Advisory Deliverables ($250/client/month)
- Latest Safe Pay Date Calculation
- Customer Payment Profiles
- Data Quality Scoring
- Cash Flow Forecasting (2-4 weeks)
- Industry Benchmarking (RMA)
- Decision-Time Guardrails
- What-If Scenario Planning

### Tier 4: Automation + Practice Scale ($500-1050/client/month)
- Budget-Based Automation Rules
- Conditional Scheduled Payments
- Runway Protection Automation
- Bulk Operations (cross-client)
- Template Workflows
- Practice Analytics
- White-Label Reports
- API Access

---

## Implementation Priority

### Phase 1 (MVP - Tier 1)
Build foundation, NO smart features yet

### Phase 2 (Smart Controls - Tier 2)
1. Earmarking (12h) - Core smart AP
2. Runway Impact Calculator (6h) - Show deltas everywhere
3. 3-Stage Collections (15h) - Core smart AR
4. Bulk Payment Matching (15h) - Critical for e-commerce
5. Vacation Mode (8h) - Advisor planning
6. Smart Hygiene (10h) - Data quality
7. Variance Alerts (6h) - Proactive notifications

**Total Phase 2**: ~72h

### Phase 3 (Advisory Deliverables - Tier 3)
1. Cash Flow Forecasting (12h)
2. Industry Benchmarking (15h)
3. Customer Payment Profiles (8h)
4. What-If Scenarios (12h)
5. Data Quality Scoring (6h)
6. Decision Guardrails (10h)

**Total Phase 3**: ~63h

### Phase 4 (Automation - Tier 4)
1. Budget-Based Automation (20h)
2. Conditional Payments (15h)
3. Runway Protection (12h)
4. Practice Management Tools (varies)

**Total Phase 4**: ~47h + practice mgmt

---

## Success Metrics

### Tier 2 Metrics
- 80%+ advisors use earmarking feature
- Average 2-3 hours saved per client per week
- 70%+ collection email response rate
- 85%+ payment matching accuracy

### Tier 3 Metrics
- 90%+ advisors reference benchmarks in client meetings
- Forecasting accuracy >85% over 7 days
- 3+ scenario comparisons per client per month

### Tier 4 Metrics
- 95%+ automation rule success rate
- Zero unintended approvals
- 5+ hours saved per client per week
- Advisors manage 2x more clients than without automation

---

**End of Smart Features Reference Library**

