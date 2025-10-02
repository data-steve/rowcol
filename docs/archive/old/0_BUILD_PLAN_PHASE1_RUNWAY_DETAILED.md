# RowCol Phase 1: Runway MVP - Detailed Build Plan

**Version**: 1.0  
**Date**: 2025-10-01  
**Target**: Productionizable Tier 1 MVP in 4 weeks (~120-180h)  
**Goal**: Spreadsheet replacement for advisors managing 20-50 clients

## ⚠️ **CRITICAL BUILD PLAN REALITY CHECK**

**This build plan is naively simplistic and handwavy over massive complexity.**

### **What This Build Plan Actually Is:**
- **Phases and stages** - not detailed requirements
- **High-level direction** - not implementation specifications
- **Hopelessly underspecified** - missing critical details
- **Needs massive healing** - like we did with v5 build plan on Oodaloo

### **What This Build Plan Is NOT:**
- ❌ **Real requirement doc** - too simplistic for actual complexity
- ❌ **Implementation guide** - missing critical details
- ❌ **Ready for execution** - needs discovery and solutioning first
- ❌ **Accurate time estimates** - based on assumptions, not reality

### **Required Healing Process:**
1. **Discovery Phase** - understand what actually exists vs. what build plan assumes
2. **Gap Analysis** - identify where build plan is wrong or missing details
3. **Solutioning Phase** - design actual solutions for complex problems
4. **Self-Healing Tasks** - convert build plan to executable/solutioning tasks
5. **Reality Grounding** - base tasks on actual codebase, not assumptions

### **Core Demands Are Same as Oodaloo v5:**
- **Multi-tenancy complexity** - advisor-client relationships
- **QBO integration challenges** - API fragility, rate limiting, data sync
- **Service boundary issues** - domains vs runway separation
- **Authentication complexity** - advisor-scoped access control
- **Data orchestration** - complex data flows across multiple systems

**This build plan is a starting point, not a finish line.**

---

## Overview

Phase 1 delivers the core "ritual" that makes advisors choose RowCol over spreadsheets. NO "smart" features yet - just visibility, speed, and basic decision-making across all clients.

### Success Criteria
- Advisor can see all 50 clients' runway days in <2 seconds
- Advisor can drill into any client and make basic AP/AR decisions
- Advisor can identify which clients need attention immediately
- System is production-ready (secure, performant, deployable)

### What's Explicitly NOT in Phase 1
- ❌ Earmarking / reserved payments (Tier 2)
- ❌ Smart collections / 3-stage drips (Tier 2)
- ❌ Runway impact calculator (Tier 2)
- ❌ Forecasting / benchmarking (Tier 3)
- ❌ Automation rules (Tier 4)
- ❌ Subscription tier enforcement (comes after P1 deploy)

### Phase 1 Scope
- ✅ Client list with batch runway visibility
- ✅ 3-tab client view (Digest, Hygiene, Console)
- ✅ Basic bill approval & scheduled payment (QBO native)
- ✅ Basic collection triggering (manual emails)
- ✅ Hygiene tray (data quality issues)
- ✅ Basic export/reporting
- ✅ Email alerts (weekly digest)
- ✅ Audit trail (decision history)

---

## Week 0: Foundation & Technical Debt (24-30h)

**Goal**: Clean slate - fix critical tech debt before building new features

### Task 0.1: Database Schema Migration (8h)

**Problem**: Current codebase uses `firm_id` but we need `advisor_id` for advisor-first positioning

**Tasks**:
- **[ ] Update all models with advisor_id** *Effort: 3h*
  - Files: `domains/core/models/*.py`, `domains/ap/models/*.py`, `domains/ar/models/*.py`
  - Find/replace: `firm_id` → `advisor_id`
  - Update foreign key relationships
  - **Success**: All models reference `advisor_id`, no `firm_id` references remain

- **[ ] Create Alembic migration script** *Effort: 2h*
  - File: `infra/database/migrations/001_firm_to_advisor_id.py`
  - SQL: `ALTER TABLE [tables] RENAME COLUMN firm_id TO advisor_id;`
  - Test: Migration runs without errors on test database
  - **Success**: Migration tested on SQLite and Postgres

- **[ ] Update all services to use advisor_id** *Effort: 2h*
  - Files: `domains/*/services/*.py`, `runway/services/*.py`
  - Update service constructors, queries, filters
  - Update `TenantAwareService` base class
  - **Success**: All services use `advisor_id` for multi-tenancy

- **[ ] Update all routes to use advisor_id** *Effort: 1h*
  - Files: `runway/routes/*.py`, `domains/*/routes/*.py`
  - Update path parameters: `/advisor/{advisor_id}/clients`
  - Update request/response schemas
  - **Success**: All API endpoints use `advisor_id` consistently

**Dependencies**: None - do this first  
**Validation**: Run full test suite, all tests pass with `advisor_id`

---

### Task 0.2: Authentication & Security (6h)

**Problem**: Hardcoded `"api_user"` in routes, no proper auth context

**Tasks**:
- **[ ] Implement auth context middleware** *Effort: 3h*
  - File: `infra/auth/context.py`
  - Middleware extracts JWT token, validates, adds user to request context
  - Available via: `get_current_user(request)` helper
  - **Success**: All routes can access `current_user.advisor_id`

- **[ ] Replace hardcoded "api_user" references** *Effort: 2h*
  - Files: 
    - `runway/routes/bills.py` (lines 172, 253)
    - `runway/routes/reserve_runway.py` (lines 66, 111, 164, 279)
  - Replace with: `current_user = get_current_user(request)`
  - **Success**: No more hardcoded user references, all use auth context

- **[ ] Add advisor-level access control** *Effort: 1h*
  - Decorator: `@require_advisor_access(advisor_id)`
  - Check: `current_user.advisor_id == advisor_id`
  - Return 403 if mismatch
  - **Success**: Advisors can only access their own clients

**Dependencies**: Task 0.1 (need `advisor_id` in place)  
**Validation**: Test with multiple advisor accounts, verify isolation

---

### Task 0.3: Basic Onboarding Flow (6h)

**Problem**: No way to add new clients to system

**Tasks**:
- **[ ] Create "Add Client" API endpoint** *Effort: 2h*
  - File: `runway/routes/onboarding.py`
  - Endpoint: `POST /advisor/{advisor_id}/clients`
  - Request: `{ "qbo_company_id": "123", "name": "Acme Corp" }`
  - Response: `{ "client_id": "456", "status": "pending_qbo_auth" }`
  - **Success**: Can create client record

- **[ ] Implement QBO OAuth initiation** *Effort: 2h*
  - File: `infra/qbo/auth_flow.py`
  - Endpoint: `GET /clients/{client_id}/qbo/authorize`
  - Generate OAuth URL, redirect to QBO
  - Callback: `GET /clients/{client_id}/qbo/callback?code=...`
  - **Success**: Client can authorize QBO access

- **[ ] Initial data sync after auth** *Effort: 2h*
  - After OAuth callback, trigger initial sync:
    - Pull bills (last 90 days)
    - Pull invoices (last 90 days)
    - Pull bank accounts & balances
    - Calculate initial runway
  - Status: `client.status = 'active'`
  - **Success**: Client appears in client list with runway data

**Dependencies**: None  
**Validation**: Can add client, authorize QBO, see data in system

---

### Task 0.4: QBO Integration Hardening (4-6h)

**Problem**: Current QBO integration may have mocking, need real API calls

**Tasks**:
- **[ ] Verify QBO API provider uses real calls** *Effort: 2h*
  - File: `infra/qbo/client.py`
  - Remove any `_get_mock_response()` calls
  - Ensure all methods call actual QBO API
  - **Success**: All QBO calls hit real API, no mocks

- **[ ] Add QBO connection health check** *Effort: 2h*
  - File: `infra/qbo/health.py`
  - Check: Token valid, API reachable, rate limits OK
  - Expose: `GET /advisor/{advisor_id}/qbo/health`
  - **Success**: Can verify QBO connection status

- **[ ] Implement token refresh handling** *Effort: 2h*
  - File: `infra/qbo/auth.py`
  - Auto-refresh tokens before expiry (1 hour)
  - Store refresh token in database (encrypted)
  - Retry failed requests once with new token
  - **Success**: QBO calls don't fail due to expired tokens

**Dependencies**: None  
**Validation**: Make real QBO API calls, verify data accuracy

---

## Week 1: Core Runway Primitives (35-45h)

**Goal**: Build the core "batch visibility" that replaces spreadsheets

### Task 1.1: Client List View - Backend (12h)

**Problem**: Advisor needs to see all clients with runway days at a glance

**Tasks**:
- **[ ] Create Client model (if not exists)** *Effort: 2h*
  - File: `runway/models/client.py`
  - Fields:
    - `client_id` (UUID, primary key)
    - `advisor_id` (UUID, foreign key)
    - `qbo_company_id` (String)
    - `name` (String)
    - `status` (Enum: pending, active, inactive)
    - `last_worked_at` (DateTime)
    - `created_at`, `updated_at` (DateTime)
  - Schema: `runway/schemas/client.py`
  - **Success**: Client model matches requirements

- **[ ] Create ClientListService** *Effort: 4h*
  - File: `runway/services/client_list.py`
  - Method: `get_clients_for_advisor(advisor_id) -> List[ClientSummary]`
  - Returns:
    ```python
    ClientSummary(
        client_id=UUID,
        name=str,
        runway_days=int,
        runway_status=Enum(red/yellow/green),  # <30 / 30-60 / >60
        last_worked_at=datetime,
        alert_count=int  # hygiene issues + overdue items
    )
    ```
  - Query optimization: Single query with joins, <2s for 50 clients
  - **Success**: Returns complete client list with metrics

- **[ ] Create Client List API endpoint** *Effort: 3h*
  - File: `runway/routes/clients.py`
  - Endpoint: `GET /advisor/{advisor_id}/clients`
  - Query params:
    - `sort_by`: runway_days | last_worked | name (default: runway_days ASC)
    - `filter_status`: red | yellow | green (optional)
  - Response: `{ "clients": [...], "summary": { "red": 5, "yellow": 12, "green": 33 } }`
  - **Success**: Returns sorted, filtered client list

- **[ ] Add "last worked" tracking** *Effort: 2h*
  - Update `last_worked_at` when advisor:
    - Approves bill
    - Triggers collection
    - Views client detail
  - Middleware: `@track_client_access(client_id)`
  - **Success**: Last worked timestamp updates correctly

- **[ ] Test client list performance** *Effort: 1h*
  - Seed database: 50 clients with varying data
  - Measure: Query execution time
  - Target: <2 seconds for full list
  - Optimize: Add indexes if needed
  - **Success**: Meets performance target

**Dependencies**: Task 0.1 (advisor_id), Task 0.3 (onboarding creates clients)  
**Validation**: Can load 50 clients with runway data in <2s

---

### Task 1.2: Runway Calculator Service (10h)

**Problem**: Need accurate runway calculation for each client

**Tasks**:
- **[ ] Create RunwayCalculatorService** *Effort: 6h*
  - File: `runway/services/runway_calculator.py`
  - Method: `calculate_runway(client_id) -> RunwayData`
  - Formula:
    ```python
    current_balance = sum(bank_account_balances)
    daily_burn = calculate_daily_burn_rate(last_90_days)
    upcoming_ap = sum(bills_due_next_30_days)
    expected_ar = sum(invoices_not_overdue_90_days)
    
    available_cash = current_balance + expected_ar - upcoming_ap
    runway_days = available_cash / daily_burn
    ```
  - Handle edge cases:
    - Zero or negative burn rate (growing businesses)
    - No bank accounts connected
    - Insufficient historical data (<30 days)
  - **Success**: Accurate runway calculation with edge case handling

- **[ ] Create RunwayData response model** *Effort: 2h*
  - File: `runway/schemas/runway.py`
  - Fields:
    ```python
    RunwayData(
        runway_days=int,
        current_balance=Decimal,
        daily_burn_rate=Decimal,
        upcoming_ap_total=Decimal,
        upcoming_ap_count=int,
        expected_ar_total=Decimal,
        expected_ar_count=int,
        calculation_date=datetime,
        data_quality_score=float  # 0-1, based on completeness
    )
    ```
  - **Success**: Complete runway data structure

- **[ ] Cache runway calculations** *Effort: 2h*
  - Store calculated runway in `client` table: `cached_runway_days`, `runway_calculated_at`
  - Recalculate when:
    - Bill approved/paid
    - Invoice created/paid
    - Bank balance changes
    - Once per day (background job)
  - API can return cached value if < 4 hours old
  - **Success**: Fast API responses, fresh data

**Dependencies**: QBO data sync working  
**Validation**: Test against known QBO company, verify accuracy

---

### Task 1.3: 3-Tab Client View - Backend (13-15h)

**Problem**: Advisor needs detailed view of single client in 3 contexts

**Tasks**:
- **[ ] Create Digest Tab API** *Effort: 4h*
  - File: `runway/routes/digest.py`
  - Endpoint: `GET /clients/{client_id}/digest`
  - Response: Complete `RunwayData` + key alerts
  - Include:
    - Runway summary
    - Top 3 bills due soon
    - Top 3 overdue invoices
    - Critical hygiene issues (count)
  - **Success**: Returns digest data in <1s

- **[ ] Create Hygiene Tab API** *Effort: 5h*
  - File: `runway/routes/hygiene.py`
  - Endpoint: `GET /clients/{client_id}/hygiene`
  - Detect issues:
    - Unmatched bank deposits
    - Bills missing due dates
    - Invoices missing customers
    - Duplicate vendors
    - Uncategorized transactions
  - Response:
    ```python
    HygieneIssue(
        issue_id=UUID,
        type=Enum(missing_due_date, unmatched_deposit, etc),
        severity=Enum(critical, high, medium),
        description=str,
        affected_entity_id=UUID,
        suggested_fix=str  # Human-readable action
    )
    ```
  - Sort by severity
  - **Success**: Returns all data quality issues

- **[ ] Create Console Tab API** *Effort: 4h*
  - File: `runway/routes/console.py`
  - Endpoint: `GET /clients/{client_id}/console`
  - Returns actionable items:
    - Bills needing approval (due ≤14 days)
    - Invoices to chase (overdue >30 days)
    - Scheduled payments (next 7 days)
  - Each item includes:
    - Entity ID
    - Amount
    - Due date / overdue days
    - Quick actions available
  - **Success**: Returns decision-ready data

**Dependencies**: Task 1.2 (runway calculator), QBO data sync  
**Validation**: Can view complete client detail across 3 tabs

---

## Week 2: Decision Console & Actions (35-45h)

**Goal**: Enable advisor to make basic AP/AR decisions

### Task 2.1: Bill Approval & Payment (12h)

**Problem**: Advisor needs to approve bills and schedule payments

**Tasks**:
- **[ ] Create Bill Approval endpoint** *Effort: 4h*
  - File: `runway/routes/bills.py`
  - Endpoint: `POST /clients/{client_id}/bills/{bill_id}/approve`
  - Request: `{ "approved": true, "notes": "..." }`
  - Actions:
    - Update bill status: `pending` → `approved`
    - Log approval: `created_by` = current user, `approved_at` = now
    - Trigger QBO sync (optional): Mark bill as ready to pay in QBO
  - Response: Updated bill with approval metadata
  - **Success**: Bill marked approved, logged

- **[ ] Create Scheduled Payment endpoint** *Effort: 4h*
  - File: `runway/routes/bills.py`
  - Endpoint: `POST /clients/{client_id}/bills/{bill_id}/schedule`
  - Request: `{ "payment_date": "2025-10-15", "payment_method": "check" }`
  - Actions:
    - Call QBO API: Schedule payment via `BillPayment` object
    - QBO handles actual payment scheduling
    - Update bill: `scheduled_payment_date`, `status` = `scheduled`
  - Response: Confirmation with QBO payment ID
  - **Success**: Payment scheduled in QBO

- **[ ] Create Batch Bill Approval** *Effort: 4h*
  - Endpoint: `POST /clients/{client_id}/bills/batch-approve`
  - Request: `{ "bill_ids": [uuid1, uuid2, ...], "notes": "..." }`
  - Actions:
    - Validate all bills belong to client
    - Approve all bills in transaction
    - Log each approval
  - Response: Summary of approved bills
  - **Success**: Can approve 10+ bills at once

**Dependencies**: QBO API integration working  
**Validation**: Approved bills appear correctly in QBO

---

### Task 2.2: Collection Triggering (8h)

**Problem**: Advisor needs to trigger collections for overdue invoices

**Tasks**:
- **[ ] Create basic collection email templates** *Effort: 2h*
  - Files: `infra/email/templates/collections/`
    - `gentle_reminder.html`
    - `urgent_follow_up.html`
    - `final_notice.html`
  - Variables: `{customer_name}`, `{invoice_number}`, `{amount}`, `{days_overdue}`
  - Tone: Professional, firm but friendly
  - **Success**: 3 email templates ready

- **[ ] Create Send Collection Email endpoint** *Effort: 4h*
  - File: `runway/routes/collections.py`
  - Endpoint: `POST /clients/{client_id}/invoices/{invoice_id}/collect`
  - Request: `{ "template": "gentle" | "urgent" | "final", "custom_message": "..." }`
  - Actions:
    - Pull invoice data from QBO
    - Render email template
    - Send via SendGrid (from client's email, reply-to advisor)
    - Log collection attempt in database
  - Response: Confirmation of email sent
  - **Success**: Email delivered to customer

- **[ ] Track collection attempts** *Effort: 2h*
  - Table: `collection_attempts`
  - Fields: `client_id`, `invoice_id`, `template_used`, `sent_at`, `sent_by`
  - Query: `GET /clients/{client_id}/invoices/{invoice_id}/collection-history`
  - **Success**: Can see history of collection emails

**Dependencies**: SendGrid configured, email templates  
**Validation**: Send test email, verify delivery and content

---

### Task 2.3: Hygiene Tray Actions (10h)

**Problem**: Advisor needs to fix data quality issues

**Tasks**:
- **[ ] Create "Add Due Date" quick fix** *Effort: 3h*
  - Endpoint: `PATCH /clients/{client_id}/bills/{bill_id}/due-date`
  - Request: `{ "due_date": "2025-10-15" }`
  - Actions:
    - Update bill in database
    - Sync to QBO via API
    - Remove from hygiene tray
  - **Success**: Due date updated in QBO

- **[ ] Create "Match Deposit" quick fix** *Effort: 4h*
  - Endpoint: `POST /clients/{client_id}/deposits/{deposit_id}/match`
  - Request: `{ "invoice_id": uuid }`
  - Actions:
    - Match bank deposit to invoice
    - Mark invoice as paid
    - Update QBO payment record
    - Remove from hygiene tray
  - **Success**: Deposit matched, invoice paid

- **[ ] Create "Merge Vendors" quick fix** *Effort: 3h*
  - Endpoint: `POST /clients/{client_id}/vendors/merge`
  - Request: `{ "primary_vendor_id": uuid, "duplicate_vendor_ids": [uuid, ...] }`
  - Actions:
    - Reassign all bills from duplicates to primary
    - Update QBO vendor records
    - Remove duplicates from hygiene tray
  - **Success**: Vendors consolidated

**Dependencies**: QBO API write access working  
**Validation**: Changes appear correctly in QBO

---

### Task 2.4: Audit Trail & History (5-7h)

**Problem**: Advisor needs to track what decisions were made

**Tasks**:
- **[ ] Create Audit Log model** *Effort: 2h*
  - File: `domains/core/models/audit_log.py` (enhance existing)
  - Fields:
    - `event_type`: bill_approved, payment_scheduled, collection_sent, etc.
    - `entity_type`: bill, invoice, client
    - `entity_id`: UUID
    - `advisor_id`: Who made the decision
    - `client_id`: Which client
    - `event_data`: JSON (before/after, notes, etc.)
    - `timestamp`: When it happened
  - **Success**: Comprehensive audit schema

- **[ ] Add audit logging to all actions** *Effort: 2h*
  - Decorator: `@audit_log(event_type="bill_approved")`
  - Apply to:
    - Bill approval/scheduling
    - Collection triggering
    - Hygiene fixes
    - Any QBO write operation
  - **Success**: All actions logged

- **[ ] Create Audit History API** *Effort: 2h*
  - Endpoint: `GET /clients/{client_id}/audit-log`
  - Query params: `event_type`, `date_range`, `limit`
  - Response: Paginated list of audit events
  - **Success**: Can review client history

**Dependencies**: None  
**Validation**: All actions appear in audit log correctly

---

## Week 3: UI/Brand System & Polish (30-40h)

**Goal**: Build professional, responsive UI that advisors want to use

### Task 3.1: Design System Foundation (10h)

**Problem**: Need consistent design tokens and component library

**Tasks**:
- **[ ] Define design tokens** *Effort: 3h*
  - File: `ui/design-tokens.css`
  - Colors:
    - Primary: Navy (#1E3A5F)
    - Secondary: Coral (#FF6B6B)
    - Success: Green (#4CAF50)
    - Warning: Yellow (#FFC107)
    - Danger: Red (#F44336)
    - Neutral: Gray scale (100-900)
  - Typography:
    - Font family: Inter (sans-serif)
    - Sizes: xs (12px), sm (14px), base (16px), lg (18px), xl (20px), 2xl (24px)
    - Weights: normal (400), medium (500), semibold (600), bold (700)
  - Spacing: 4px base scale (0, 4, 8, 12, 16, 24, 32, 48, 64)
  - **Success**: Design tokens file complete

- **[ ] Set up Tailwind config** *Effort: 2h*
  - File: `ui/tailwind.config.js`
  - Import design tokens
  - Configure custom utilities
  - **Success**: Tailwind uses design system

- **[ ] Create base components** *Effort: 5h*
  - Files: `ui/components/`
    - `Button.tsx` - Primary, secondary, ghost variants
    - `Card.tsx` - Container with shadow, padding
    - `Badge.tsx` - Status badges (red/yellow/green)
    - `Input.tsx` - Form input with validation
    - `Select.tsx` - Dropdown with search
    - `Table.tsx` - Data table with sorting
  - Use TypeScript + React
  - **Success**: Base component library

**Dependencies**: None  
**Validation**: Components render correctly, design tokens applied

---

### Task 3.2: Client List UI (8h)

**Problem**: Need responsive, sortable client list

**Tasks**:
- **[ ] Build ClientListTable component** *Effort: 5h*
  - File: `ui/components/ClientListTable.tsx`
  - Columns:
    - Client name (link to detail)
    - Runway days (with badge color)
    - Last worked (relative time)
    - Alerts (count badge)
  - Features:
    - Sortable columns (click header)
    - Filter by status (red/yellow/green)
    - Search by name
  - Responsive: Table on desktop, card list on mobile
  - **Success**: Full-featured client list

- **[ ] Build ClientListSummary component** *Effort: 2h*
  - File: `ui/components/ClientListSummary.tsx`
  - Display: "5 clients under 30 days runway"
  - Breakdown: Red: 5, Yellow: 12, Green: 33
  - Filters: Click status to filter list
  - **Success**: Summary matches API data

- **[ ] Build ClientList page** *Effort: 1h*
  - File: `ui/pages/ClientList.tsx`
  - Layout: Summary at top, table below
  - Load data from API: `/advisor/{advisor_id}/clients`
  - **Success**: Complete client list page

**Dependencies**: Task 3.1 (components), Task 1.1 (API)  
**Validation**: Can view and sort 50 clients smoothly

---

### Task 3.3: Client Detail - 3-Tab View UI (12h)

**Problem**: Need tabbed interface for client detail

**Tasks**:
- **[ ] Build TabNavigation component** *Effort: 2h*
  - File: `ui/components/TabNavigation.tsx`
  - Tabs: Digest, Hygiene, Console
  - Active state styling
  - Keyboard navigation (arrow keys)
  - **Success**: Accessible tab navigation

- **[ ] Build DigestTab component** *Effort: 3h*
  - File: `ui/components/DigestTab.tsx`
  - Layout:
    - Runway summary card (days, status, metrics)
    - Top 3 upcoming bills (name, amount, due date)
    - Top 3 overdue invoices (name, amount, days overdue)
    - Critical hygiene alerts (count with link to Hygiene tab)
  - **Success**: Complete digest view

- **[ ] Build HygieneTab component** *Effort: 3h*
  - File: `ui/components/HygieneTab.tsx`
  - Layout:
    - Issue list grouped by severity
    - Each issue: Description, affected entity, quick fix button
  - Actions:
    - Click "Add Due Date" → inline date picker
    - Click "Match Deposit" → search/select invoice
    - Click "Merge Vendors" → select duplicates
  - **Success**: Interactive hygiene fixes

- **[ ] Build ConsoleTab component** *Effort: 4h*
  - File: `ui/components/ConsoleTab.tsx`
  - Layout:
    - Bills section: Cards for each bill needing approval
    - Invoices section: Cards for each invoice needing collection
    - Scheduled section: Upcoming scheduled payments
  - Actions:
    - Approve bill (single click)
    - Schedule payment (date picker modal)
    - Send collection (template picker modal)
  - **Success**: All console actions work

**Dependencies**: Task 3.1 (components), Task 1.3 (APIs)  
**Validation**: Can navigate tabs, see data, take actions

---

### Task 3.4: Responsive Layout & Polish (10h)

**Problem**: Need mobile-responsive layouts

**Tasks**:
- **[ ] Build responsive navigation** *Effort: 3h*
  - File: `ui/components/Navigation.tsx`
  - Desktop: Sidebar with logo, nav links, user menu
  - Mobile: Hamburger menu, bottom nav
  - Links: Clients, Settings, Support
  - **Success**: Works on all screen sizes

- **[ ] Implement loading states** *Effort: 2h*
  - Component: `ui/components/LoadingSpinner.tsx`
  - Apply to:
    - Client list while loading
    - Client detail tabs while loading
    - Actions while processing
  - **Success**: No blank screens during loads

- **[ ] Implement error states** *Effort: 2h*
  - Component: `ui/components/ErrorMessage.tsx`
  - Display:
    - API errors (with retry button)
    - Validation errors (form fields)
    - Network errors (connection lost)
  - **Success**: Graceful error handling

- **[ ] Add keyboard shortcuts** *Effort: 2h*
  - Shortcuts:
    - `/` - Focus search
    - `Escape` - Close modals
    - Arrow keys - Navigate lists
    - `Enter` - Approve/submit
  - Display: Help modal with `?` key
  - **Success**: Power users can work keyboard-only

- **[ ] Polish animations** *Effort: 1h*
  - Smooth transitions on:
    - Tab switching
    - Modal open/close
    - List sorting
    - Button states
  - Use Tailwind transitions
  - **Success**: Feels polished, not janky

**Dependencies**: All UI components built  
**Validation**: Test on mobile, tablet, desktop

---

## Week 4: Production Hardening (20-30h)

**Goal**: Make it production-ready - secure, performant, reliable

### Task 4.1: Export & Reporting (8h)

**Problem**: Advisors need to export data for their own analysis

**Tasks**:
- **[ ] Create CSV export service** *Effort: 4h*
  - File: `runway/services/export.py`
  - Export types:
    - Client list (all fields)
    - Bills for client (date range)
    - Invoices for client (date range)
    - Audit log for client (date range)
  - Format: CSV with headers
  - Streaming: Handle large datasets without memory issues
  - **Success**: Can export 1000+ records

- **[ ] Create Export API endpoints** *Effort: 2h*
  - Endpoint: `GET /clients/{client_id}/export/bills?start_date=...&end_date=...&format=csv`
  - Response: Streaming CSV download
  - Filename: `{client_name}_bills_{date_range}.csv`
  - **Success**: Browser downloads CSV file

- **[ ] Create Export UI buttons** *Effort: 2h*
  - Add "Export" button to:
    - Client list page
    - Bills tab in console
    - Invoices tab in console
  - Modal: Select date range, click download
  - **Success**: One-click export from UI

**Dependencies**: None  
**Validation**: Export 100 records, open in Excel, verify data

---

### Task 4.2: Email Alerts & Notifications (8h)

**Problem**: Advisors need proactive alerts when clients need attention

**Tasks**:
- **[ ] Create Email Alert Service** *Effort: 3h*
  - File: `infra/notifications/email_alerts.py`
  - Alert types:
    - Weekly digest (Monday morning)
    - Runway threshold breach (<30 days)
    - New hygiene issues detected
  - Template: `infra/email/templates/alerts/`
  - **Success**: Can send formatted alerts

- **[ ] Create Weekly Digest Alert** *Effort: 3h*
  - Schedule: Monday 6am (advisor's timezone)
  - Content:
    - Clients needing attention (red runway)
    - Total bills to approve
    - Total invoices to chase
    - Link to dashboard
  - **Success**: Weekly email delivered

- **[ ] Create Alert Preferences** *Effort: 2h*
  - Model: `advisor.alert_preferences` (JSON)
  - Settings:
    - Enable/disable weekly digest
    - Runway threshold for alerts (default: 30 days)
    - Email frequency (daily, weekly)
  - UI: Settings page
  - **Success**: Advisor can configure alerts

**Dependencies**: SendGrid configured  
**Validation**: Receive test alert, verify formatting

---

### Task 4.3: Performance Optimization (6h)

**Problem**: Need to ensure fast load times at scale

**Tasks**:
- **[ ] Add database indexes** *Effort: 2h*
  - Tables: `clients`, `bills`, `invoices`, `audit_log`
  - Indexes:
    - `clients.advisor_id` (for list queries)
    - `bills.client_id` + `bills.due_date` (for console)
    - `invoices.client_id` + `invoices.status` (for console)
    - `audit_log.client_id` + `audit_log.timestamp` (for history)
  - Test: Query performance before/after
  - **Success**: <500ms for all queries

- **[ ] Implement query result caching** *Effort: 2h*
  - Use Redis for caching:
    - Client list (cache for 5 minutes)
    - Runway calculations (cache for 4 hours)
    - Hygiene scan results (cache for 1 hour)
  - Invalidate cache on data changes
  - **Success**: Subsequent loads are instant

- **[ ] Optimize QBO API calls** *Effort: 2h*
  - Batch requests where possible
  - Implement request deduplication (same query within 1 minute)
  - Respect rate limits (120 req/min)
  - **Success**: Efficient QBO usage

**Dependencies**: Redis configured  
**Validation**: Load test with 50 clients, all pages <2s

---

### Task 4.4: Security Hardening (4h)

**Problem**: Need to ensure data security and privacy

**Tasks**:
- **[ ] Implement rate limiting** *Effort: 2h*
  - Middleware: `infra/api/rate_limiter.py`
  - Limits:
    - 100 requests per minute per advisor
    - 10 login attempts per hour per IP
  - Response: 429 Too Many Requests
  - **Success**: Rate limiting enforced

- **[ ] Add CORS configuration** *Effort: 1h*
  - File: `main.py`
  - Allow origins: Production domain only
  - Allow credentials: True (for cookies)
  - Allow methods: GET, POST, PATCH, DELETE
  - **Success**: CORS configured correctly

- **[ ] Encrypt sensitive data** *Effort: 1h*
  - QBO refresh tokens (database field encryption)
  - Advisor API keys (if implemented)
  - Use: Fernet symmetric encryption
  - **Success**: Sensitive data encrypted at rest

**Dependencies**: None  
**Validation**: Security audit checklist complete

---

### Task 4.5: Bug Fixes & Polish (4-6h)

**Problem**: Final cleanup before production

**Tasks**:
- **[ ] Run full test suite** *Effort: 1h*
  - All unit tests pass
  - All integration tests pass
  - No skipped tests
  - **Success**: Green test suite

- **[ ] Fix linter errors** *Effort: 1h*
  - Run: `ruff check .`
  - Fix all errors and warnings
  - **Success**: Clean lint output

- **[ ] Test all user flows end-to-end** *Effort: 2h*
  - Manual testing:
    - Add new client
    - View client list
    - Drill into client detail
    - Approve bill
    - Send collection
    - Fix hygiene issue
    - Export data
  - **Success**: All flows work smoothly

- **[ ] Browser compatibility testing** *Effort: 1h*
  - Test on:
    - Chrome (latest)
    - Firefox (latest)
    - Safari (latest)
    - Mobile Chrome
    - Mobile Safari
  - **Success**: Works on all browsers

**Dependencies**: All features complete  
**Validation**: Production-ready checklist complete

---

## Productionalization Checklist

After Week 4, ready to deploy. Follow these steps (separate from build plan):

### Infrastructure Setup
- [ ] Set up production Postgres database
- [ ] Configure Docker containers
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Configure SSL certificates
- [ ] Set up CDN for static assets

### Monitoring & Observability
- [ ] Sentry for error tracking
- [ ] Datadog/New Relic for APM
- [ ] CloudWatch/Stackdriver for logs
- [ ] Uptime monitoring (Pingdom)

### Security
- [ ] Penetration testing
- [ ] Security headers configured
- [ ] Secrets management (AWS Secrets Manager)
- [ ] Backup strategy (daily snapshots)

### Operations
- [ ] Runbook documentation
- [ ] On-call rotation (if team)
- [ ] Incident response plan
- [ ] Customer support SLA

**Estimated Productionalization Time**: 20-30h (separate from Phase 1 build)

---

## Phase 1 Complete: Success Metrics

### Must-Have Metrics (Launch Blockers)
- ✅ Client list loads in <2s for 50 clients
- ✅ Runway calculation accuracy: 95%+ vs. manual spreadsheet
- ✅ Zero security vulnerabilities (critical/high)
- ✅ 100% test coverage on core flows
- ✅ Can onboard new client in <5 minutes

### Nice-to-Have Metrics (Monitor Post-Launch)
- 🎯 Advisor can complete weekly ritual in <30 min (vs. 2+ hours in spreadsheet)
- 🎯 80%+ of advisors return weekly
- 🎯 <1% error rate on QBO API calls
- 🎯 Average API response time <500ms

---

## What Comes Next (Phase 2 Preview)

After Phase 1 deploys and advisors validate the core ritual works:

### Phase 2: Smart Tier Features (~72h)
- Earmarking / reserved payments
- Runway impact calculator
- 3-stage collection workflows
- Bulk payment matching
- Vacation mode planning
- Smart hygiene prioritization
- Variance alerts

**Build Phase 2 offline while Phase 1 is in production and being user-tested**

Then roll out as "upgrade to Smart tier" upsell.

---

**END OF PHASE 1 DETAILED BUILD PLAN**

**Total Estimated Effort**: 120-180 hours (4 weeks full-time)

**Files Created/Modified**: ~80-100 files across `domains/`, `runway/`, `infra/`, `ui/`

**Lines of Code**: ~15,000-20,000 (including tests)

