# RowCol Phase 2: Smart Tier Features - Detailed Build Plan

**Version**: 1.0  
**Date**: 2025-10-01  
**Target**: Tier 2 "Smart Runway Controls" features (~72h)  
**Pricing**: $150/client/month (3x Tier 1)  
**Timeline**: Build offline while Phase 1 is in production being user-tested

---

## Overview

Phase 2 adds "smart" features that enhance the core ritual with intelligence and planning capabilities. These features justify 3x pricing by saving advisors 2-3 hours per client per week through automation, planning ahead, and smarter decision support.

### Value Proposition
- **Tier 1** ($50): Spreadsheet replacement - visibility and basic decisions
- **Tier 2** ($150): Smart controls - planning, automation awareness, time-saving intelligence

### Phase 2 Features (Priority Order)
1. **Earmarking / Reserved Bill Pay** (12h) - Plan ahead, vacation mode
2. **Runway Impact Calculator** (6h) - Show deltas everywhere
3. **3-Stage Collection Workflows** (15h) - Automated follow-ups
4. **Bulk Payment Matching / Stripe Unbundling** (15h) - E-commerce support
5. **Vacation Mode Planning** (8h) - Set it and forget it
6. **Smart Hygiene Prioritization** (10h) - Fix what matters most
7. **Variance Alerts / Drift Detection** (6h) - Proactive notifications

**Total Phase 2**: ~72 hours

---

## Feature 1: Earmarking / Reserved Bill Pay (12h)

### Problem Statement
Advisors need to "reserve" money for must-pay bills (rent, payroll) so they don't accidentally approve other bills that would drain needed funds. Current scheduled payments in QBO don't affect available balance, which can lead to cash crunches.

### User Story
> "As an advisor, I want to earmark my client's $5k rent payment for Oct 1st, so the system knows that money is reserved and shows me only the remaining available balance when I'm approving other bills."

### Solution Overview
Add earmarking capability to bills. When earmarked:
- Money is treated as "spent" in available balance calculation
- Runway calculation uses available balance, not current balance
- Advisor sees: "Available: $45k (Current: $52k, Earmarked: $7k)"

### Tasks

#### Task 2.1.1: Extend Bill Model for Earmarking (2h) - **EXECUTION READY**
- **File**: `domains/ap/models/bill.py`
- **Changes**:
  ```python
  class Bill(Base):
      # Existing fields...
      is_earmarked = Column(Boolean, default=False)
      earmarked_date = Column(DateTime, nullable=True)
      earmarked_by = Column(String, nullable=True)  # advisor_id
      earmark_reason = Column(String, nullable=True)  # "rent", "payroll", "vacation mode"
  ```
- **Schema**: Update `domains/ap/schemas/bill.py` with earmark fields
- **Migration**: `infra/database/migrations/002_add_bill_earmarking.py`
- **Success Criteria**: 
  - ✅ Bill model has earmark fields
  - ✅ Migration runs without errors
  - ✅ Can save earmarked bills to database

**Validation**: Create test bill with earmark fields, query successfully

---

#### Task 2.1.2: Create Earmark API Endpoints (3h) - **EXECUTION READY**
- **File**: `runway/routes/bills.py`
- **Endpoints**:
  
  **1. Earmark Bill**
  ```python
  POST /clients/{client_id}/bills/{bill_id}/earmark
  Request: {
      "earmark_date": "2025-10-15",
      "reason": "rent" | "payroll" | "vacation_mode" | "other"
  }
  Response: Updated bill with earmark fields
  ```

  **2. Un-earmark Bill**
  ```python
  DELETE /clients/{client_id}/bills/{bill_id}/earmark
  Response: Updated bill with earmark cleared
  ```

  **3. Get Earmarked Bills**
  ```python
  GET /clients/{client_id}/bills/earmarked
  Response: List of all earmarked bills for client
  ```

- **Business Logic**:
  - Validate bill belongs to client
  - Log earmark action in audit log
  - Trigger runway recalculation (cache invalidation)
  - Update `last_worked_at` for client

- **Success Criteria**:
  - ✅ Can earmark/un-earmark bills via API
  - ✅ Earmark actions logged in audit trail
  - ✅ Returns proper error codes (404, 403, etc.)

**Validation**: API tests cover happy path and error cases

---

#### Task 2.1.3: Update Runway Calculator for Available Balance (4h) - **SOLUTIONING NEEDED**
- **File**: `runway/services/runway_calculator.py`
- **Problem**: Current calculator uses `current_balance`. Need to calculate `available_balance`.

- **New Calculation**:
  ```python
  def calculate_runway(client_id) -> RunwayData:
      current_balance = sum(bank_account_balances)
      
      # NEW: Calculate earmarked total
      earmarked_bills = get_earmarked_bills(client_id)
      earmarked_total = sum(bill.amount for bill in earmarked_bills)
      
      # NEW: Available balance
      available_balance = current_balance - earmarked_total
      
      # Use available balance for runway calculation
      upcoming_ap = sum(bills_due_next_30_days) - earmarked_total  # Don't double-count
      expected_ar = sum(invoices_not_overdue_90_days)
      
      net_cash = available_balance + expected_ar - upcoming_ap
      runway_days = net_cash / daily_burn_rate
      
      return RunwayData(
          runway_days=runway_days,
          current_balance=current_balance,
          available_balance=available_balance,  # NEW field
          earmarked_total=earmarked_total,      # NEW field
          # ... other fields
      )
  ```

- **Schema Update**:
  - File: `runway/schemas/runway.py`
  - Add: `available_balance`, `earmarked_total` fields

- **Success Criteria**:
  - ✅ Runway calculation uses available balance
  - ✅ Earmarked bills don't count in upcoming AP
  - ✅ Available balance visible in API response

**Solutioning Questions**:
- Should earmarked bills affect daily burn rate calculation?
- How to handle partially earmarked bills (split payments)?
- What if earmark date is past but bill not paid? (Alert advisor?)

**Validation**: Test with known scenario, verify math is correct

---

#### Task 2.1.4: Add Earmark UI Components (3h) - **EXECUTION READY**
- **File**: `ui/components/EarmarkButton.tsx`
- **Component**: Button to earmark/un-earmark bill from Console tab

- **UI Flow**:
  1. Click "Earmark" on bill card
  2. Modal opens: Select date (date picker), select reason (dropdown)
  3. Confirm → API call → Update UI
  4. Bill card shows orange "EARMARKED" badge
  5. Available balance updates at top of page

- **File**: `ui/components/AvailableBalanceDisplay.tsx`
- **Component**: Shows current vs. available balance
  ```tsx
  <div className="balance-display">
    <div>Current: $52,000</div>
    <div>Earmarked: -$7,000</div>
    <div className="available">Available: $45,000</div>
  </div>
  ```

- **Integration**:
  - Add earmark button to Console tab bill cards
  - Show available balance in Digest tab
  - Filter option: "Show only earmarked bills"

- **Success Criteria**:
  - ✅ Can earmark bill from UI
  - ✅ Earmark badge visible on bills
  - ✅ Available balance updates instantly

**Validation**: Manual UI testing of earmark flow

---

## Feature 2: Runway Impact Calculator (6h)

### Problem Statement
Advisors need to see explicit runway impact ("**+3 days runway**") when making any AP decision. Currently they have to do mental math.

### User Story
> "As an advisor, when I'm deciding whether to approve or delay a $5k bill, I want to see '**+3 days runway if delayed to Oct 6**' so I can make informed decisions without mental calculations."

### Solution Overview
Calculate runway delta for every action and show it inline. Formula: `runway_delta = (bill_amount / daily_burn_rate) in days`

### Tasks

#### Task 2.2.1: Create Runway Impact Service (3h) - **EXECUTION READY**
- **File**: `runway/services/runway_impact.py`
- **Methods**:
  
  ```python
  class RunwayImpactService:
      def calculate_bill_impact(
          self, 
          client_id: UUID, 
          bill_amount: Decimal, 
          action: Literal["pay_now", "delay", "earmark"]
      ) -> RunwayImpact:
          """Calculate runway impact of bill action"""
          runway_data = get_cached_runway(client_id)
          daily_burn = runway_data.daily_burn_rate
          
          if action == "pay_now":
              delta_days = -(bill_amount / daily_burn)
          elif action == "delay":
              delta_days = +(bill_amount / daily_burn)
          elif action == "earmark":
              # Earmarking reduces available balance but protects runway
              delta_days = 0  # Neutral on runway, but affects available cash
          
          return RunwayImpact(
              delta_days=delta_days,
              impact_type="positive" if delta_days > 0 else "negative",
              explanation=self._generate_explanation(action, delta_days)
          )
      
      def _generate_explanation(self, action, delta_days) -> str:
          if action == "pay_now":
              return f"Paying now costs {abs(delta_days):.1f} days runway"
          elif action == "delay":
              return f"Delaying protects {delta_days:.1f} days runway"
          else:
              return f"Earmarking protects future runway without immediate impact"
  ```

- **Success Criteria**:
  - ✅ Accurate delta calculation
  - ✅ Human-readable explanations
  - ✅ Handles edge cases (zero burn, negative burn)

**Validation**: Unit tests with known scenarios

---

#### Task 2.2.2: Integrate Impact Calculator into APIs (2h) - **EXECUTION READY**
- **Files**: `runway/routes/bills.py`
- **Changes**: Add `runway_impact` field to all bill responses

- **Example Response**:
  ```json
  {
    "bill_id": "123",
    "amount": 5000,
    "due_date": "2025-10-15",
    "runway_impact": {
      "pay_now": {
        "delta_days": -3.2,
        "impact_type": "negative",
        "explanation": "Paying now costs 3.2 days runway"
      },
      "delay_to_due": {
        "delta_days": +3.2,
        "impact_type": "positive",
        "explanation": "Delaying to Oct 15 protects 3.2 days runway"
      }
    }
  }
  ```

- **Success Criteria**:
  - ✅ All bill endpoints include impact
  - ✅ Impact calculated in real-time
  - ✅ Minimal performance overhead (<100ms)

**Validation**: API response includes impact, math checks out

---

#### Task 2.2.3: Add Impact Display to UI (1h) - **EXECUTION READY**
- **File**: `ui/components/RunwayImpactBadge.tsx`
- **Component**: Color-coded badge showing impact

- **Visual Design**:
  - Positive impact (delay): Green badge "**+3 days**"
  - Negative impact (pay now): Red badge "**-3 days**"
  - Neutral (earmark): Orange badge "**Protects runway**"

- **Integration Points**:
  - Bill cards in Console tab
  - Earmark modal ("Earmarking protects runway")
  - Batch approval summary ("These 5 actions net **+8 days**")

- **Success Criteria**:
  - ✅ Impact visible on every bill action
  - ✅ Color coding clear and consistent
  - ✅ Tooltip shows detailed explanation

**Validation**: Manual UI review, confirm clarity

---

## Feature 3: 3-Stage Collection Workflows (15h)

### Problem Statement
Advisors manually write collection emails for every overdue invoice. Need automated sequences that trigger on behalf of client with professional templates.

### User Story
> "As an advisor, I want to trigger a 3-stage collection sequence for my client's $8k overdue invoice, so the emails go out automatically (gentle → urgent → final) without me writing each one."

### Solution Overview
Automated email drip campaigns with 3 stages:
1. **Day 0-30**: Gentle reminder
2. **Day 31-60**: Urgent follow-up
3. **Day 61+**: Final notice

Advisor triggers once, system sends emails automatically, pauses on payment detection.

### Tasks

#### Task 2.3.1: Create Collection Sequence Models (3h) - **EXECUTION READY**
- **File**: `domains/ar/models/collection_sequence.py`
- **Models**:
  
  ```python
  class CollectionSequence(Base):
      __tablename__ = "collection_sequences"
      
      sequence_id = Column(UUID, primary_key=True)
      client_id = Column(UUID, ForeignKey("clients.id"))
      invoice_id = Column(UUID, ForeignKey("invoices.id"))
      advisor_id = Column(UUID, ForeignKey("advisors.id"))
      
      status = Column(Enum("active", "paused", "completed", "cancelled"))
      current_stage = Column(Integer, default=0)  # 0=not started, 1-3=stages
      
      # Timing
      stage1_sent_at = Column(DateTime, nullable=True)
      stage2_sent_at = Column(DateTime, nullable=True)
      stage3_sent_at = Column(DateTime, nullable=True)
      
      # Timing configuration (days between stages)
      days_to_stage2 = Column(Integer, default=7)   # Send stage 2 after 7 days
      days_to_stage3 = Column(Integer, default=14)  # Send stage 3 after 14 days
      
      created_at = Column(DateTime, default=datetime.utcnow)
      updated_at = Column(DateTime, onupdate=datetime.utcnow)
  
  class CollectionAttempt(Base):
      __tablename__ = "collection_attempts"
      
      attempt_id = Column(UUID, primary_key=True)
      sequence_id = Column(UUID, ForeignKey("collection_sequences.id"))
      
      stage = Column(Integer)  # 1, 2, or 3
      template_used = Column(String)
      sent_at = Column(DateTime)
      sent_to = Column(String)  # Customer email
      status = Column(Enum("sent", "delivered", "opened", "bounced"))
  ```

- **Schema**: `domains/ar/schemas/collection_sequence.py`
- **Migration**: `infra/database/migrations/003_collection_sequences.py`

- **Success Criteria**:
  - ✅ Can create and track sequences
  - ✅ Can record attempts per sequence
  - ✅ Status tracking works

**Validation**: Create test sequence, verify database records

---

#### Task 2.3.2: Enhance Collection Email Templates (2h) - **EXECUTION READY**
- **Files**: `infra/email/templates/collections/`
  
  **Stage 1: Gentle (gentle_reminder.html)**
  ```html
  Subject: Friendly reminder: Invoice #{{invoice_number}}
  
  Hi {{customer_name}},
  
  Just a friendly reminder that Invoice #{{invoice_number}} for ${{amount}} 
  was due on {{due_date}}. 
  
  If you've already sent payment, please disregard this email. Otherwise, 
  we'd appreciate payment at your earliest convenience.
  
  [Pay Now Button]
  
  Thank you,
  {{client_name}}
  ```

  **Stage 2: Urgent (urgent_follow_up.html)**
  ```html
  Subject: Payment Required: Invoice #{{invoice_number}} ({{days_overdue}} days overdue)
  
  Hi {{customer_name}},
  
  We noticed that Invoice #{{invoice_number}} for ${{amount}} is now 
  {{days_overdue}} days past due.
  
  To avoid any service interruptions, please submit payment by {{final_date}}.
  
  [Pay Now Button]
  
  If there's an issue with this invoice, please contact us immediately.
  
  Best regards,
  {{client_name}}
  ```

  **Stage 3: Final (final_notice.html)**
  ```html
  Subject: FINAL NOTICE: Invoice #{{invoice_number}}
  
  {{customer_name}},
  
  This is our final notice regarding Invoice #{{invoice_number}} for ${{amount}}, 
  which is now {{days_overdue}} days overdue.
  
  If we don't receive payment within 7 days, we will be forced to:
  - Suspend services
  - Engage a collection agency
  - Report to credit bureaus
  
  [Pay Now Button]
  
  Please contact us immediately if you need to discuss payment arrangements.
  
  {{client_name}}
  ```

- **Variables**: All templates use same variable set
- **Styling**: Professional HTML email design with client branding

- **Success Criteria**:
  - ✅ Templates are professional and firm
  - ✅ Variables populate correctly
  - ✅ Mobile-responsive design

**Validation**: Send test emails to own inbox, verify rendering

---

#### Task 2.3.3: Create Collection Sequence Service (6h) - **SOLUTIONING NEEDED**
- **File**: `domains/ar/services/collection_sequence.py`
- **Methods**:
  
  ```python
  class CollectionSequenceService:
      def start_sequence(
          self,
          client_id: UUID,
          invoice_id: UUID,
          advisor_id: UUID,
          timing_config: Optional[Dict] = None
      ) -> CollectionSequence:
          """Start new collection sequence for invoice"""
          # Check: Invoice is actually overdue
          # Check: No active sequence already exists
          # Create sequence record
          # Schedule stage 1 email (immediate or next day)
          # Return sequence
      
      def send_next_stage(self, sequence_id: UUID) -> CollectionAttempt:
          """Send next stage email in sequence"""
          # Get sequence
          # Determine which stage to send
          # Pull invoice data
          # Pull customer data
          # Render email template
          # Send via SendGrid
          # Record attempt
          # Update sequence status
          # Schedule next stage (if not final)
      
      def pause_sequence(self, sequence_id: UUID, reason: str):
          """Pause sequence (e.g., payment detected)"""
          # Update status to 'paused'
          # Cancel scheduled jobs for future stages
          # Log pause reason
      
      def check_for_payment(self, sequence_id: UUID) -> bool:
          """Check if invoice was paid (auto-pause trigger)"""
          # Query invoice status
          # If paid, pause sequence
          # Return True if payment detected
  ```

- **Background Job**:
  - File: `infra/jobs/collection_sequences_job.py`
  - Frequency: Run daily at 9am (advisor timezone)
  - Actions:
    - Find sequences needing next stage
    - Send stage emails
    - Check for payments (auto-pause)

- **Success Criteria**:
  - ✅ Sequences trigger correctly
  - ✅ Emails send on schedule
  - ✅ Auto-pause on payment works
  - ✅ Advisor can manually pause/cancel

**Solutioning Questions**:
- What if customer responds to email? (Track email opens/replies?)
- Should we integrate with QBO's collection system or standalone?
- How to handle timezone differences (advisor vs. customer)?
- Should stage timing be per-client configurable?

**Validation**: End-to-end test of full sequence

---

#### Task 2.3.4: Create Collection Workflow UI (4h) - **EXECUTION READY**
- **File**: `ui/components/CollectionWorkflowModal.tsx`
- **Modal Flow**:
  
  **Step 1: Trigger Collection**
  - Button on Console tab: "Start Collections"
  - Opens modal showing invoice details
  - Preview: "This will send gentle reminder immediately, followed by urgent (Day 7) and final (Day 14)"
  
  **Step 2: Customize (Optional)**
  - Adjust timing: Days between stages
  - Add custom message (append to template)
  - Preview each email
  
  **Step 3: Confirm & Activate**
  - Click "Start Collection Sequence"
  - Confirmation: "Collection sequence activated"
  - Modal closes, invoice card shows "In Collections" badge

- **Status Display**:
  - File: `ui/components/CollectionStatusBadge.tsx`
  - Shows: "Collections: Stage 2 of 3" with progress indicator
  - Click badge → view sequence history (emails sent, opened)

- **Manual Controls**:
  - Pause button: "Payment received? Pause sequence"
  - Send now button: "Send next stage immediately (don't wait)"
  - Cancel button: "Stop sequence entirely"

- **Success Criteria**:
  - ✅ Easy to trigger sequences
  - ✅ Clear status visibility
  - ✅ Manual override options

**Validation**: Walk through UI flow, test all controls

---

## Feature 4: Bulk Payment Matching / Stripe Unbundling (15h)

### Problem Statement
E-commerce and service pro clients take Stripe/Square payments bundled across multiple invoices. Single deposit of $5,000 might be 3-5 invoices plus fees. Need to unbundle and match correctly for runway accuracy.

### User Story
> "As an advisor, when my e-commerce client gets a $5,000 Stripe deposit, I want the system to suggest which invoices it matches (based on amounts and dates) so I can approve matches quickly without manual calculation."

### Solution Overview
Detect bulk deposits from payment processors, analyze amounts/dates, suggest matching invoices with confidence scoring, allow advisor to approve or manually adjust.

### Tasks

#### Task 2.4.1: Payment Processor Detection (3h) - **SOLUTIONING NEEDED**
- **File**: `domains/bank/services/payment_processor_detector.py`
- **Logic**:
  
  ```python
  class PaymentProcessorDetector:
      KNOWN_PROCESSORS = {
          "stripe": ["STRIPE", "STRIPE INC", "STRIPE PAYMENTS"],
          "square": ["SQUARE", "SQ *", "SQUARE INC"],
          "paypal": ["PAYPAL", "PP *"],
      }
      
      def detect_processor(self, bank_transaction: BankTransaction) -> Optional[str]:
          """Detect if transaction is from payment processor"""
          description = bank_transaction.description.upper()
          
          for processor, patterns in self.KNOWN_PROCESSORS.items():
              if any(pattern in description for pattern in patterns):
                  return processor
          
          return None
      
      def is_bulk_deposit(self, transaction: BankTransaction) -> bool:
          """Heuristic: Is this likely a bundled payment?"""
          # Heuristics:
          # 1. From known processor
          # 2. Amount is round-ish (e.g., $5000.00 often = bundled)
          # 3. Multiple unpaid invoices exist near this amount
          # 4. Transaction date aligns with processor payout schedule
  ```

- **Success Criteria**:
  - ✅ Correctly identifies Stripe/Square/PayPal deposits
  - ✅ Flags likely bulk deposits for unbundling

**Solutioning Questions**:
- How to detect NEW payment processors not in known list?
- What if client uses custom payment processor?
- Should we learn from advisor corrections (ML?)?

**Validation**: Test with real Stripe/Square deposits

---

#### Task 2.4.2: Invoice Matching Algorithm (6h) - **SOLUTIONING NEEDED**
- **File**: `domains/ar/services/payment_unbundling.py`
- **Algorithm**:
  
  ```python
  class PaymentUnbundlingService:
      def find_matching_invoices(
          self,
          deposit_amount: Decimal,
          deposit_date: date,
          client_id: UUID,
          processor: str
      ) -> List[InvoiceMatch]:
          """Find invoices that likely match this bulk deposit"""
          
          # Step 1: Get unpaid invoices within date range
          candidates = self.get_unpaid_invoices(
              client_id=client_id,
              date_range=(deposit_date - timedelta(days=45), deposit_date)
          )
          
          # Step 2: Calculate processor fee (typical: 2.9% + $0.30)
          fee_rate = self.get_processor_fee_rate(processor)
          expected_net = deposit_amount
          expected_gross = expected_net / (1 - fee_rate)
          
          # Step 3: Find combinations of invoices that sum to expected_gross
          matches = self.find_sum_combinations(
              candidates=candidates,
              target_sum=expected_gross,
              tolerance=0.05  # ±5%
          )
          
          # Step 4: Score each combination by confidence
          scored_matches = []
          for combo in matches:
              confidence = self.calculate_confidence(
                  combo=combo,
                  deposit_date=deposit_date,
                  target_sum=expected_gross
              )
              scored_matches.append(InvoiceMatch(
                  invoices=combo,
                  confidence=confidence,
                  gross_amount=sum(inv.amount for inv in combo),
                  processor_fee=expected_gross - expected_net,
                  net_deposit=expected_net
              ))
          
          # Step 5: Return top 3 matches, sorted by confidence
          return sorted(scored_matches, key=lambda x: x.confidence, reverse=True)[:3]
      
      def calculate_confidence(self, combo, deposit_date, target_sum) -> float:
          """Confidence score 0-1"""
          # Factors:
          # - Amount match (closer to target = higher)
          # - Date proximity (invoices near deposit date = higher)
          # - Number of invoices (fewer = higher confidence)
          # - Invoice status (all unpaid = higher)
  ```

- **Edge Cases**:
  - Multiple valid combinations (show all, advisor picks)
  - No good matches (manual matching flow)
  - Partial matches (some invoices match, others don't)

- **Success Criteria**:
  - ✅ Finds correct matches 80%+ of time
  - ✅ Confidence scores are accurate predictors
  - ✅ Handles edge cases gracefully

**Solutioning Questions**:
- What if invoices are in different currencies?
- How to handle partial payments (invoice partially paid elsewhere)?
- Should we suggest splitting deposit across multiple matches?
- Performance: What if client has 1000+ unpaid invoices?

**Validation**: Test with real Stripe deposits, measure accuracy

---

#### Task 2.4.3: Payment Matching API (3h) - **EXECUTION READY**
- **File**: `runway/routes/payment_matching.py`
- **Endpoints**:
  
  **1. Get Matching Suggestions**
  ```python
  GET /clients/{client_id}/deposits/{deposit_id}/match-suggestions
  Response: {
    "deposit": {...},
    "suggested_matches": [
      {
        "confidence": 0.92,
        "invoices": [
          {"invoice_id": "...", "amount": 2000},
          {"invoice_id": "...", "amount": 1500}
        ],
        "gross_amount": 3500,
        "processor_fee": 104.80,
        "net_deposit": 3395.20
      },
      // ... more suggestions
    ]
  }
  ```

  **2. Apply Match**
  ```python
  POST /clients/{client_id}/deposits/{deposit_id}/apply-match
  Request: {
    "invoice_ids": ["uuid1", "uuid2"],
    "processor_fee": 104.80
  }
  Response: {
    "success": true,
    "invoices_marked_paid": 2,
    "deposit_matched": true
  }
  ```

- **Actions on Apply**:
  - Mark invoices as paid in QBO
  - Record payment application in database
  - Remove from hygiene tray
  - Trigger runway recalculation

- **Success Criteria**:
  - ✅ API returns accurate suggestions
  - ✅ Apply match updates QBO correctly
  - ✅ Audit trail logs match decisions

**Validation**: API integration tests

---

#### Task 2.4.4: Payment Matching UI (3h) - **EXECUTION READY**
- **File**: `ui/components/PaymentMatchingModal.tsx`
- **UI Flow**:
  
  **Step 1: Detect Bulk Deposit**
  - Hygiene tray shows: "Unmatched Stripe deposit: $5,000"
  - Click "Match" → Opens modal
  
  **Step 2: Show Suggestions**
  - Display top 3 matches with confidence scores
  - Each suggestion:
    - List of invoices (numbers, amounts)
    - Total gross, processor fee, net
    - Confidence badge (High 92%, Medium 75%, Low 60%)
    - "Apply This Match" button
  
  **Step 3: Manual Override**
  - "None of these? Manual match" button
  - Search/select invoices manually
  - System calculates totals
  - "Apply Match" button
  
  **Step 4: Confirmation**
  - "Match applied! 2 invoices marked paid."
  - Deposit removed from hygiene tray
  - Invoices show "Paid" status

- **Visual Design**:
  - Color-coded confidence: Green (>85%), Yellow (70-85%), Red (<70%)
  - Invoice amounts add up visually (progress bar)
  - Processor fee shown separately ("Stripe fee: $104.80")

- **Success Criteria**:
  - ✅ Intuitive matching interface
  - ✅ High-confidence suggestions feel obvious
  - ✅ Manual override available
  - ✅ Clear confirmation of actions

**Validation**: User test with real advisors

---

## Features 5-7: Quick Implementations (18h total)

### Feature 5: Vacation Mode Planning (8h)

**Brief**: Extend earmarking with "vacation mode" preset. Advisor clicks "Vacation Mode Oct 1-15", system auto-earmarks all essential bills in that range.

**Tasks** (all EXECUTION READY):
- Task 2.5.1: Add vacation mode API endpoint (3h)
- Task 2.5.2: Bill categorization (essential vs. discretionary) (3h)
- Task 2.5.3: Vacation mode UI toggle (2h)

**Details in SMART_FEATURES_REFERENCE.md**

---

### Feature 6: Smart Hygiene Prioritization (10h)

**Brief**: Sort hygiene issues by runway impact. "Fix these 5 issues to unlock 8 days runway accuracy."

**Tasks** (mostly EXECUTION READY, one SOLUTIONING):
- Task 2.6.1: Runway impact calculation per hygiene issue (4h) - **SOLUTIONING**
- Task 2.6.2: Prioritization API (3h) - **EXECUTION**
- Task 2.6.3: Prioritized hygiene tray UI (3h) - **EXECUTION**

**Solutioning Needed**: How to estimate runway impact of each issue type?

---

### Feature 7: Variance Alerts / Drift Detection (6h)

**Brief**: Daily check for runway changes. Alert advisor: "Client X: Runway dropped 8 days today from 4 new bills."

**Tasks** (all EXECUTION READY):
- Task 2.7.1: Daily runway snapshot job (2h)
- Task 2.7.2: Variance detection service (2h)
- Task 2.7.3: Aggregated alert emails (2h)

**Details in SMART_FEATURES_REFERENCE.md**

---

## Phase 2 Rollout Strategy

### Week 1-2: Core Smart Features (33h)
- Earmarking (12h)
- Runway Impact Calculator (6h)
- 3-Stage Collections (15h)

### Week 3-4: Advanced Features (39h)
- Bulk Payment Matching (15h)
- Vacation Mode (8h)
- Smart Hygiene (10h)
- Variance Alerts (6h)

### Week 5: Integration & Testing (10h)
- Feature testing
- Performance optimization
- UI polish
- Documentation

### Deployment
- Deploy as "opt-in beta" for Phase 1 users
- Gather feedback
- Roll out as Tier 2 pricing ($150/client/month)

---

## Success Metrics for Phase 2

### Adoption Metrics
- 🎯 60%+ of Phase 1 users upgrade to Tier 2 within 3 months
- 🎯 80%+ of Tier 2 users actively use earmarking feature
- 🎯 70%+ of Tier 2 users activate at least 1 collection sequence

### Time Savings
- 🎯 Advisors report 2-3 hours saved per client per week
- 🎯 Average weekly ritual time: <15 minutes (down from 30 in Tier 1)
- 🎯 Collection response rate: 50%+ (vs. <30% for manual emails)

### Technical Performance
- 🎯 Runway impact calculations: <100ms latency
- 🎯 Payment matching accuracy: 80%+ suggested matches accepted
- 🎯 Collection sequence delivery rate: >95%
- 🎯 Zero data corruption from bulk operations

### Revenue Impact
- 🎯 Phase 2 generates 3x revenue per client vs. Phase 1
- 🎯 Churn rate: <5% monthly (sticky due to automation)
- 🎯 NPS score: >50 (advisors love the smart features)

---

## Dependencies & Risks

### Dependencies
- Phase 1 must be deployed and stable
- SendGrid account configured for email sending
- QBO API write access working reliably
- Redis available for caching (performance)

### Risks & Mitigations
- **Risk**: Earmarking confuses advisors ("Why is balance different?")
  - **Mitigation**: Clear UI explanations, onboarding tutorial
  
- **Risk**: Collection emails marked as spam
  - **Mitigation**: SPF/DKIM setup, professional templates, test with multiple email providers
  
- **Risk**: Payment matching algorithm inaccurate
  - **Mitigation**: Start with manual review required, learn from corrections, improve algorithm iteratively
  
- **Risk**: Runway impact calculator gives wrong deltas
  - **Mitigation**: Extensive testing with known scenarios, show calculation logic to advisor

---

## Next Phase Preview

**Phase 3: Advisory Deliverables** (~63h)
- Industry benchmarking (RMA integration)
- Cash flow forecasting (2-4 weeks)
- Customer payment profiles
- What-if scenario planning
- Advanced reserve management
- Data quality scoring

**Pricing**: $250/client/month (5x Tier 1)

---

**END OF PHASE 2 BUILD PLAN**

**Total Estimated Effort**: 72 hours (2-3 weeks full-time, or 4-6 weeks part-time while Phase 1 is live)

**Files Created/Modified**: ~40 files across `domains/`, `runway/`, `infra/`, `ui/`

**Lines of Code**: ~8,000-10,000 (including tests)


