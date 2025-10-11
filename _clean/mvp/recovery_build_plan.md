# RowCol MVP Recovery Build Plan

*Version 2.0 — Strangler-Fig Recovery with Smart Sync Architecture*

## **Purpose (Read First)**

We are recovering from architectural rot by carving a **minimal, safe MVP** from a large codebase. The MVP is **QBO-only** and includes: **Bills**, **Balances**, **Invoices**. It must establish proper **Smart Sync patterns** with **Domain Gateways**, **Sync Orchestrator**, **Transaction Log**, and **State Mirror**.

**Critical Context**: The current domains contain architectural rot - they bypass the Smart Sync pattern and violate proper service boundaries. We must establish the clean architecture first, then rebuild domains to follow it.

**Architecture Enforcement**: `runway/ → domains/ → infra/` (no back edges, ever). Domains define interfaces; Infra implements them; Runway composes.

## **CRITICAL: Use Executable Tasks Document**

**This recovery build plan has been restructured into proper executable tasks. Use `_clean/mvp/0_EXECUTABLE_TASKS.md` instead of this document for execution.**

**The executable tasks document provides:**
1. **Proper Task Structure** - 8 tasks in correct priority order with checkboxes
2. **Comprehensive Discovery** - Mandatory discovery commands for each task
3. **Recursive Triage Process** - Safe execution patterns to prevent mistakes
4. **Specific Implementation Patterns** - Code examples and file structures
5. **Verification Steps** - Clear success criteria for each task
6. **Progress Tracking** - Checkbox status and git commit instructions

**This approach ensures hands-free execution with proper validation and prevents the mistakes that led to the original architectural rot.**

## **CRITICAL: Read These Files First (MANDATORY)**

### **Architecture Context (2-3 most relevant):**
- `_clean/architecture/comprehensive_architecture.md` - Complete architecture vision
- `_clean/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy with Smart Sync
- `_clean/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles

### **Product Context (1-2 most relevant):**
- `_clean/mvp/mvp_comprehensive_prd.md` - **COMPREHENSIVE MVP PRD** (read this first!)
- `_clean/e2e/product_strategy.md` - Complete e2e product vision
- `_clean/product/hygiene_tray_prd.md` - Hygiene Tray PRD (post-Ramp era)

### **Recovery Context (1-2 most relevant):**
- `_clean/strangled_fig/migration_manifest.md` - File-by-file porting instructions
- `_clean/strangled_fig/stepped_plan.md` - Detailed implementation roadmap

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Data Architecture**: Local mirroring + Smart Sync pattern for live data
- **Database**: SQLite (`rowcol.db`) for MVP, not `oodaloo.db`
- **Testing**: Real QBO API calls, no mocking - use sandbox credentials

---

## **CRITICAL: Setup Requirements (MANDATORY)**

### **Environment Setup**
```bash
# 1. Navigate to project root
cd /Users/stevesimpson/projects/rowcol

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install dependencies
cd _clean
pip install -e .

# 4. Set up environment variables
# .env already has all the QBO credentials you need

```

### **QBO Sandbox Credentials (REQUIRED)**
```bash
# THESE ARE ALREADY IN  .env file .... JUST USE THEM:
# IN FACT infra/qbo/config.py handles a lot of this stuff 
# make moving it to _clean a priority (cleansed)
QBO_CLIENT_ID=your_sandbox_client_id
QBO_CLIENT_SECRET=your_sandbox_client_secret
QBO_REDIRECT_URI=http://localhost:8000/auth/callback
QBO_SANDBOX_BASE_URL=https://sandbox-quickbooks.api.intuit.com
QBO_PRODUCTION_BASE_URL=https://quickbooks.api.intuit.com
```

### **Database Setup**
```bash
# SQLite database (not oodaloo.db)
DATABASE_URL=sqlite:///rowcol.db

# Initialize database
python -c "from infra.db.session import create_tables; create_tables()"
```

### **Test Data Sources**
- **NO MOCKING**: Use real QBO sandbox data
- **Existing QBO Infrastructure**: Use `infra/qbo/` (config, auth, utils, client, DTOs)
- **Real API Calls**: All services must hit real QBO API
- **Test Fixtures**: Use existing `tests/sandbox/` data as reference

### **Discovery Commands (MANDATORY)**
```bash
# Find all QBO-related code
grep -r "qbo" . --include="*.py" | head -20
grep -r "QBO" . --include="*.py" | head -20

# Find sync patterns
grep -r "sync" . --include="*.py" | head -20
grep -r "mirror" . --include="*.py" | head -20

# Find domain patterns
grep -r "domains/" . --include="*.py" | head -20
grep -r "runway/" . --include="*.py" | head -20

# Check current database
ls -la *.db
```

### **Validation Commands**
```bash
# Test current state
uvicorn main:app --reload
curl http://localhost:8000/healthz

# Test QBO connection
python -c "from infra.qbo.client import QBORawClient; print('QBO client imported successfully')"

# Test database
python -c "from infra.database.session import get_db; print('Database session works')"
```

---

## **0) Scope & Non-Negotiables**

### **MVP Features**
- **Read**: QBO **Bills**, **Invoices**, **Balances** (bank account balances via QBO; Plaid comes *later*)
- **Write**: 
  - **Hygiene Tray**: Update QBO data to fix hygiene issues (vendor names, categorization, missing fields)
  - **Digest**: Read-only advisor overview dashboard
  - **Tray**: Read/write to clean and organize bills/invoices
  - **Console**: Read-only insights (no bill payments until Ramp integration)
- **Views**: Three separate pages - **Digest** (read-only), **Tray** (read/write), **Console** (read-only)

### **Concrete MVP Example: Grounded in Existing Product Vision**

#### **Tray Service (Hygiene & Data Quality) - READ/WRITE**
```python
class TrayService:
    def get_hygiene_tray(self, advisor_id: str, business_id: str) -> HygieneTray:
        """Get data quality issues and sync problems for advisor review"""
        # Read QBO data via domain gateways
        bills = self.bills_gateway.list(ListBillsQuery(advisor_id, business_id, "OPEN"))
        invoices = self.invoices_gateway.list(ListInvoicesQuery(advisor_id, business_id, "OPEN"))
        balances = self.balances_gateway.get(BalancesQuery(advisor_id, business_id))
        
        # Check data freshness and quality
        hygiene_issues = self.check_data_hygiene(advisor_id, business_id)
        
        return HygieneTray(
            stale_data_issues=[issue for issue in hygiene_issues if issue.type == "STALE_DATA"],
            sync_failures=[issue for issue in hygiene_issues if issue.type == "SYNC_FAILURE"],
            data_discrepancies=[issue for issue in hygiene_issues if issue.type == "DISCREPANCY"],
            total_issues=len(hygiene_issues),
            last_sync_status=self.get_last_sync_status(advisor_id, business_id)
        )
    
    def get_bill_tray(self, advisor_id: str, business_id: str) -> BillTray:
        """Get bills organized by status for advisor review"""
        # Read bills from QBO via domain gateway
        bills = self.bills_gateway.list(ListBillsQuery(
            advisor_id=advisor_id, 
            business_id=business_id, 
            status="OPEN", 
            freshness_hint="CACHED_OK"
        ))
        
        # Organize by status for advisor workflow
        return BillTray(
            urgent_bills=[b for b in bills if b.days_until_due <= 7],
            upcoming_bills=[b for b in bills if 7 < b.days_until_due <= 30],
            overdue_bills=[b for b in bills if b.days_until_due < 0],
            total_amount=sum(b.amount for b in bills),
            runway_impact_days=self.calculate_runway_impact(bills)
        )
    
    def fix_bill_hygiene(self, advisor_id: str, business_id: str, bill_id: str, fixes: dict) -> bool:
        """Fix hygiene issues in QBO bill data"""
        # Update QBO bill with corrected data
        return self.bills_gateway.update_bill(
            advisor_id=advisor_id,
            business_id=business_id, 
            bill_id=bill_id,
            updates=fixes  # e.g., {"vendor_name": "Corrected Name", "category": "Office Supplies"}
        )
    
    def fix_invoice_hygiene(self, advisor_id: str, business_id: str, invoice_id: str, fixes: dict) -> bool:
        """Fix hygiene issues in QBO invoice data"""
        # Update QBO invoice with corrected data
        return self.invoices_gateway.update_invoice(
            advisor_id=advisor_id,
            business_id=business_id,
            invoice_id=invoice_id,
            updates=fixes  # e.g., {"customer_name": "Corrected Name", "category": "Services"}
        )
```

#### **Digest Service (Reporting & Insights) - READ-ONLY**
```python
class DigestService:
    def get_weekly_digest(self, advisor_id: str, business_id: str) -> WeeklyDigest:
        """Get weekly summary of data quality and business insights"""
        # Read QBO data via domain gateways
        bills = self.bills_gateway.list(ListBillsQuery(advisor_id, business_id, "OPEN"))
        invoices = self.invoices_gateway.list(ListInvoicesQuery(advisor_id, business_id, "OPEN"))
        balances = self.balances_gateway.get(BalancesQuery(advisor_id, business_id))
        
        # Calculate insights and hygiene status
        return WeeklyDigest(
            cash_position=sum(b.available for b in balances),
            total_ap=sum(b.amount for b in bills),
            total_ar=sum(i.amount for i in invoices),
            runway_days=self.calculate_runway_days(bills, balances),
            data_quality_score=self.calculate_data_quality_score(advisor_id, business_id),
            hygiene_flags=self.get_hygiene_flags(advisor_id, business_id),
            recommendations=self.generate_recommendations(bills, invoices, balances)
        )
```

#### **Console Service (Insights & Recommendations) - READ-ONLY**
```python
class ConsoleService:
    def get_financial_overview(self, advisor_id: str, business_id: str) -> FinancialOverview:
        """Get financial overview (no decision-making in QBO-only MVP)"""
        # Read QBO data via domain gateways
        bills = self.bills_gateway.list(ListBillsQuery(advisor_id, business_id, "OPEN"))
        invoices = self.invoices_gateway.list(ListInvoicesQuery(advisor_id, business_id, "OPEN"))
        balances = self.balances_gateway.get(BalancesQuery(advisor_id, business_id))
        
        # Simple financial overview (no bill approval decisions)
        return FinancialOverview(
            cash_position=sum(b.available for b in balances),
            bills_due_this_week=len([b for b in bills if b.days_until_due <= 7]),
            total_ap=sum(b.amount for b in bills),
            total_ar=sum(i.amount for i in invoices),
            runway_days=self.calculate_runway_days(bills, balances),
            data_freshness_status=self.get_data_freshness_status(advisor_id, business_id)
        )
```

### **Architecture (Fixed)**
- **Runway (product)**: Orchestration & product calculators (business value), DTOs, HTTP routes
- **Domains (rail-agnostic contracts)**: Gateway interfaces + domain models + repo interfaces (mirror/log)
- **Infra (implementations)**: QBO client/mapper, **Sync Orchestrator**, **Transaction Log repo**, **Mirror repos**, DB session

### **Data Stores**
- **Transaction Log (append-only, durable)**: OUTBOUND intents + INBOUND facts (webhook/poll)
- **State Mirror (mutable)**: Current, denormalized rows for fast reads
- **Cache (ephemeral)**: Optional, safe to flush, never a source of truth

### **MVP Hub Model (QBO-Centric)**
- **QBO (Ledger Hub)**: Source of truth for financial data (bills, invoices, balances) - read for insights, write for hygiene fixes
- **RowCol (Orchestrator)**: Coordinates QBO operations and provides advisor interface
  - **Read Operations**: Bills, invoices, balances for insights and reporting
  - **Write Operations**: Data hygiene fixes (vendor names, categorization, missing fields)
- **Future Rails (Spokes)**: Will be added later with specific responsibilities:
  - **Ramp (A/P Execution Rail)**: Bill payment scheduling and execution
  - **Plaid (Verification Rail)**: Bank account verification and real-time balances
  - **Stripe (A/R Execution Rail)**: Invoice payment processing

**Note**: In MVP, QBO is the ledger hub with read/write capabilities for data hygiene fixes. We're proving the Smart Sync pattern with a single rail. In the full e2e vision, RowCol becomes the operational hub that orchestrates multiple rails while QBO remains the authoritative ledger.

### **Advisor-First Model (CORE FOUNDATION)**
- **Primary Identifier**: `advisor_id` (not `client_id` or `business_id`)
- **Business Relationship**: `advisor_id` → `business_id` (one advisor can manage multiple businesses)
- **Authentication Context**: All requests include `advisor_id` in context
- **Data Isolation**: All data queries filtered by `advisor_id` first, then `business_id`
- **Future Multi-Tenancy**: Firm-level multi-tenancy comes later; MVP is advisor-centric

### **Dependency Direction**
`runway/ → domains/ → infra/` (no back edges, ever)

---

## **1) Folder Layout (MVP Nucleus)**

```
_clean/
  pyproject.toml         # (or requirements.txt)
  .cursorrules           # edit-scope guard (see below)
  scripts/
    ci_guard.sh          # blocks edits outside MVP lane
  mvp/
    api/
    routes.py        # FastAPI endpoints: /snapshot, /approve
    services/
    runway_orchestrator.py  # composes gateways + calculators
    calculators/            # (existing product math you keep)
    schemas/
    dto.py
    wiring.py          # composition root (bind interfaces→impls)
    domains/
    ap/
        models.py
        gateways.py          # interfaces (BillsGateway, PaymentsGateway)
        repositories.py      # interfaces (BillsMirrorRepo, PaymentsMirrorRepo, LogRepo)
    ar/
        models.py
        gateways.py          # InvoicesGateway
        repositories.py
    bank/
        models.py
        gateways.py          # BalancesGateway
        repositories.py
    infra/
    db/
        session.py
        schema.sql           # tables: integration_log, mirror_bills, mirror_invoices, mirror_payments
    repos/
        ap_repo.py    # implements BillsMirrorRepo/PaymentsMirrorRepo
        ar_repo.py    # implements Invoices mirror
        log_repo.py   # implements LogRepo
    rails/
        qbo/
        client.py          # QBO auth/client
        mappers.py         # QBO DTO → domain
    sync/
        orchestrator.py      # freshness, idempotency key helper, strict-refresh flow
    gateways/
        ap_qbo_gateway.py    # implements BillsGateway using QBO client + sync
        ar_qbo_gateway.py    # implements InvoicesGateway using QBO client + sync
        bank_qbo_gateway.py  # implements BalancesGateway using QBO client + sync
```

> **Note:** This is a **new nucleus**. We will copy only a curated subset of files from the old repo into `_clean/mvp/infra/...` (see Whitelist below). Everything else stays behind.

---

## **HITL Email Integration Decision**

### **Market Reality Assessment**
- **Ramp's 99% Accuracy**: Significantly reduces basic data quality issues
- **Plaid's Data Quality Issues**: Real-time bank data has its own accuracy problems
- **Vendor Normalization**: QBO handles first-time normalization, but ongoing issues persist
- **Keeper/ClientHub**: Focus on bookkeeping automation, not advisor-focused data quality

### **HITL Email Strategy**
- **Phase 1 (MVP)**: Focus on sync issues, vendor normalization, and cross-system validation
- **Phase 2 (Post-MVP)**: Smart HITL emails for complex, high-value issues only
- **Phase 3 (Future)**: AI-powered email triggers based on client preferences and issue complexity

### **Integration with Existing Tools**
- **Uncat.com Style**: Transaction categorization and vendor clarification
- **Ramp Integration**: Use Ramp's accuracy to reduce false positives
- **Plaid Integration**: Use bank data to validate transactions
- **Client Preferences**: Let clients opt into different levels of HITL

---

## **2) Who Does What (Precise)**

### **Runway Layer**
- **routes.py**: HTTP handlers (FastAPI)
- **runway_orchestrator.py**: Composes domain gateways (+ product calculators) to build the **Snapshot** (Digest/Console/Hygiene)
- **calculators/**: *Product* math (runway buffer, priorities). These belong in Runway, not in domains or infra
  - **data_quality_calculator.py**: Existing hygiene scoring logic (integrate with Hygiene Tray)
  - **runway_calculator.py**: Cash runway calculations (integrate with Console)
  - **priority_calculator.py**: Issue prioritization (integrate with Digest)

### **Domains Layer (Contracts Only)**
- **gateways.py**: Rail-agnostic interfaces
  - `BillsGateway.list(q), BillsGateway.schedule_payment(...)`
  - `InvoicesGateway.list(q)`
  - `BalancesGateway.get(q)`
- **repositories.py**: Mirror + log **interfaces** only

### **Infra Layer (Implementations)**
- **rails/qbo/**: QBO client + mappers (no business rules)
- **sync/orchestrator.py**: Strict-refresh logic, TTL policy, idempotency key
- **repos/**: SQLite implementations for **Mirror** and **Transaction Log**
- **gateways/**: Implement domain interfaces using QBO client + sync orchestrator
- **db/schema.sql**: 3–4 tables created here
- **config/**: Product-specific clean definitions and feature gates
  - **feature_gates.py**: `multi_rail_hygiene` flags for Hygiene Tray
  - **clean_definitions.py**: Client-specific "clean" criteria (future)

---

## **3) Data Flow (Smart Sync Pattern)**

### **Sync Orchestrator Interface (Concrete)**
```python
# infra/sync/orchestrator.py
class SyncOrchestrator:
    def read_refresh(
        self,
        entity: str,                    # "bills", "invoices", "balances"
        client_id: str,                 # advisor_id in MVP
        hint: Literal["CACHED_OK", "STRICT"],
        mirror_is_fresh: Callable[[str, str, dict], bool],  # (entity, client_id, policy) -> bool
        fetch_remote: Callable[[], tuple[list[dict], str | None]],  # returns (raw, source_version)
        upsert_mirror: Callable[[list[dict], str | None, datetime], None],
        read_from_mirror: Callable[[], list[Any]],
        on_hygiene: Callable[[str, str], None],  # (client_id, code) -> None
    ) -> list[Any]:
        # Policy-driven freshness check
        # STRICT or stale/expired → rail → INBOUND log → mirror upsert → return mirror
        # CACHED_OK + fresh → return mirror
        # Error → log failure + hygiene flag + return stale mirror

    def write_idempotent(
        self,
        operation: str,                 # "ap.post_bill_payment"
        client_id: str,                 # advisor_id in MVP
        idem_key: str,                  # stable key for deduplication
        call_remote: Callable[[], dict],
        optimistic_apply: Callable[[dict], None],
        on_hygiene: Callable[[str, str], None],
    ) -> dict:
        # OUTBOUND intent log → rail call → OUTBOUND result log → optimistic mirror apply
        # Error → log failure + hygiene flag + raise exception
```

### **Entity Policy (Configuration)**
```python
# core/freshness_policy.py
ENTITY_POLICY = {
    "bills":    {"soft_ttl_s": 300,  "hard_ttl_s": 3600},   # 5min soft, 1hr hard
    "invoices": {"soft_ttl_s": 900,  "hard_ttl_s": 3600},   # 15min soft, 1hr hard
    "balances": {"soft_ttl_s": 120,  "hard_ttl_s": 600},    # 2min soft, 10min hard
}
```

### **Read Operations (Smart Sync)**
```
User Request → Runway Service → Domain Gateway → Infra Gateway → Sync Orchestrator → Mirror/Rail → Log INBOUND → Mirror Update
```

1. Runway → Domains(Gateway) → Infra(Gateway) → Sync Orchestrator
2. If `freshness_hint=STRICT` **or** mirror stale:
   a) Infra.Sync fetch from QBO
   b) **append INBOUND** to **Transaction Log**
   c) **upsert Mirror**
   d) return from Mirror

### **Write Operations (Future Rails Only)**
```
User Action → Runway Service → Domain Gateway → Infra Gateway → Log OUTBOUND → Rail API → Log OUTBOUND Result → Mirror Update
```

**Note**: QBO MVP supports read operations for insights and write operations for data hygiene fixes. Bill payment execution will be handled by Ramp rail in future phases.
- QBO = Ledger Hub (read for insights, write for hygiene fixes, source of truth)
- Ramp = A/P Execution Rail (write operations, bill payments)
- Plaid = Verification Rail (bank account verification)
- Stripe = A/R Execution Rail (invoice payments)

### **Sync Operations (Webhooks/Recon)**
```
Scheduled Job → Sync Orchestrator → Rail API → Log INBOUND → Mirror Update
```

- Infra handler → **INBOUND log** → Mirror upsert
- Hygiene flags are produced in Runway if mirrors are stale or last sync failed

---

## **4) Where Business Logic Lives (Fixed)**

- **Runway**: Holds **product calculators** (runway buffer math, priority, insights)
- **Domains**: Do **data orchestration contracts** - they define *what* data is needed (Bills, Invoices, Balances) and provide a stable interface
- **Infra**: Does **how** to get it (QBO adapters, sync, retries, log/mirror writes)

> **Key Fix**: Current "data orchestrators" that *fetch and shape data for Runway* should become **domain gateways** (interfaces) + **infra gateway implementations** (QBO), while the *business/value math* stays in **Runway calculators**.

---

## **5) File Selection — What to Bring (Whitelist) vs Skip (Blacklist)**

> Cursor: copy **only** the items below into `mvp/infra/...`. Everything else stays in the legacy repo.

### **Whitelist (Copy Now; Minimal)**

#### **QBO Client & Mapping (Read/Write Only)**
- `infra/qbo/client.py` → `infra/rails/qbo/client.py`
- `infra/qbo/qbo_mapper.py` and `infra/qbo/dtos.py` → `infra/rails/qbo/mappers.py`
- Minimal `infra/qbo/auth.py` if needed for tokens

#### **Sync Core (Adapted)**
- `infra/jobs/base_sync_service.py` → `infra/sync/base_sync_service.py` (keep as-is for HTTP/retry/dedupe)
- **CREATE** `infra/sync/orchestrator.py` with concrete interface:
  - `read_refresh(entity, client_id, hint, mirror_is_fresh, fetch_remote, upsert_mirror, read_from_mirror, on_hygiene)`
  - `write_idempotent(operation, client_id, idem_key, call_remote, optimistic_apply, on_hygiene)`
  - Uses `BaseSyncService.execute_sync_call()` internally
  - Policy-driven TTLs per entity type

#### **SQLite Session**
- `infra/database/session.py` (or a 20-line replacement)

#### **Transaction Log + Mirror Repos**
- **PORT** from `domains/core/services/transaction_log_service.py` → `infra/repos/log_repo.py`
- **PORT** domain models → mirror table implementations
- **Reference**: See migration manifest for exact porting instructions

### **Blacklist (Do NOT Bring Into MVP Nucleus)**

- `runway/services/data_orchestrators/*` (deprecated; replaced by gateways)
- `domains/*/services/*` (contain architectural rot; will be rebuilt as gateways)
- `infra/qbo/*` not needed for Bills/Invoices/Payments auth/DTOs
- `infra/jobs/job_scheduler.py`, `job_storage.py`, **priority queues** (post-MVP)
- Non-QBO rails (Plaid, Ramp, Stripe)
- Cross-rail identity graphs, advanced reconciliation utilities
- Legacy routes under domains/*/routes (HTTP belongs in Runway)

---

## **6) DB Schema (SQLite, Minimal)**

```sql
-- Append-only transaction log (audit, retry/replay)
CREATE TABLE IF NOT EXISTS integration_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  direction TEXT CHECK(direction IN ('OUTBOUND','INBOUND')) NOT NULL,
  rail TEXT NOT NULL,           -- 'qbo'
  operation TEXT NOT NULL,      -- 'list_bills', 'post_bill_payment'
  idem_key TEXT,                -- stable key for writes
  http_code INTEGER,
  status TEXT,                  -- 'OK','RETRY','FAILED'
  payload_json TEXT,            -- raw rail payload
  source_version TEXT,          -- etag or change token if available
  advisor_id TEXT NOT NULL,     -- primary identifier (advisor-first model)
  business_id TEXT NOT NULL,    -- foreign key to business
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- State mirrors (fast reads) - all include advisor_id for data isolation
CREATE TABLE IF NOT EXISTS mirror_bills (
  bill_id TEXT PRIMARY KEY,
  advisor_id TEXT NOT NULL,     -- primary identifier
  business_id TEXT NOT NULL,    -- foreign key to business
  vendor_id TEXT,
  due_date TEXT,
  amount NUMERIC,
  status TEXT,                  -- 'OPEN','SCHEDULED','PAID'
  source_version TEXT,
  last_synced_at DATETIME,
  INDEX idx_advisor_business (advisor_id, business_id)
);

CREATE TABLE IF NOT EXISTS mirror_invoices (
  invoice_id TEXT PRIMARY KEY,
  advisor_id TEXT NOT NULL,     -- primary identifier
  business_id TEXT NOT NULL,    -- foreign key to business
  customer_id TEXT,
  due_date TEXT,
  amount NUMERIC,
  status TEXT,                  -- 'OPEN','PARTIAL','PAID'
  source_version TEXT,
  last_synced_at DATETIME,
  INDEX idx_advisor_business (advisor_id, business_id)
);

CREATE TABLE IF NOT EXISTS mirror_payments (
  payment_id TEXT PRIMARY KEY,
  bill_id TEXT,
  advisor_id TEXT NOT NULL,     -- primary identifier
  business_id TEXT NOT NULL,    -- foreign key to business
  amount NUMERIC,
  paid_on TEXT,
  source_version TEXT,
  last_synced_at DATETIME,
  INDEX idx_advisor_business (advisor_id, business_id)
);

-- Advisor-Business relationship table
CREATE TABLE IF NOT EXISTS advisor_businesses (
  advisor_id TEXT NOT NULL,
  business_id TEXT NOT NULL,
  business_name TEXT,
  qbo_realm_id TEXT,            -- QBO company ID
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (advisor_id, business_id)
);
```

---

## **7) Domain Interfaces (Keep Tiny and Stable)**

### **domains/ap/gateways.py**
```python
from typing import Protocol, List, Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class Bill(BaseModel):
    id: str
    vendor_id: str | None = None
    due_date: date | None = None
    amount: Decimal
    status: Literal["OPEN","SCHEDULED","PAID"]

class ListBillsQuery(BaseModel):
    advisor_id: str              # primary identifier (advisor-first model)
    business_id: str             # foreign key to business
    status: Literal["OPEN","ALL"] = "OPEN"
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> List[Bill]: ...
    # Note: Bill payment scheduling is handled by Ramp (future rail), not QBO
```

### **domains/ar/gateways.py**
```python
from typing import Protocol, List, Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class Invoice(BaseModel):
    id: str
    customer_id: str | None = None
    due_date: date | None = None
    amount: Decimal
    status: Literal["OPEN","PARTIAL","PAID"]

class ListInvoicesQuery(BaseModel):
    advisor_id: str              # primary identifier (advisor-first model)
    business_id: str             # foreign key to business
    status: Literal["OPEN","ALL"] = "OPEN"
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class InvoicesGateway(Protocol):
    def list(self, q: ListInvoicesQuery) -> List[Invoice]: ...
```

### **domains/bank/gateways.py**
```python
from typing import Protocol, List, Literal
from pydantic import BaseModel

class AccountBalance(BaseModel):
    account_id: str
    available: float

class BalancesQuery(BaseModel):
    advisor_id: str              # primary identifier (advisor-first model)
    business_id: str             # foreign key to business
    freshness_hint: Literal["CACHED_OK","STRICT"] = "CACHED_OK"

class BalancesGateway(Protocol):
    def get(self, q: BalancesQuery) -> List[AccountBalance]: ...
```

### **runway/schemas.py (MVP Data Models)**
```python
from typing import List, Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class BillTray(BaseModel):
    """Bills organized by urgency for advisor workflow"""
    urgent_bills: List[Bill]      # due within 7 days
    upcoming_bills: List[Bill]    # due in 8-30 days
    overdue_bills: List[Bill]     # past due
    total_amount: Decimal
    runway_impact_days: int

class ConsoleSnapshot(BaseModel):
    """Complete financial snapshot for advisor dashboard"""
    cash_position: float
    bills_due_this_week: int
    total_ap: Decimal            # accounts payable
    total_ar: Decimal            # accounts receivable
    runway_days: int
    hygiene_flags: List[str]     # data freshness issues

class HygieneFlag(BaseModel):
    """Data quality and freshness indicators"""
    code: str                    # e.g., "QBO_THROTTLED", "STALE_BILLS"
    message: str
    severity: Literal["WARNING", "ERROR"]
```

### **repositories.py (Pattern)**
```python
from typing import Protocol, List, Any
from datetime import datetime

class BillsMirrorRepo(Protocol):
    def list_open(self, advisor_id: str, business_id: str) -> list[Any]: ...
    def upsert_many(self, advisor_id: str, business_id: str, raw: list[dict], source_version: str | None, synced_at: datetime): ...
    def is_fresh(self, advisor_id: str, business_id: str, policy: dict) -> bool: ...

class LogRepo(Protocol):
    def append(self, *, direction: str, rail: str, operation: str, advisor_id: str, business_id: str,
               idem_key: str | None = None, http_code: int | None = None,
               status: str | None = None, payload_json: str | None = None,
               source_version: str | None = None) -> None: ...
    def flag_hygiene(self, advisor_id: str, code: str) -> None: ...
```

---

## **8) Infra Gateway Implementation (Example)**

### **infra/gateways/ap_qbo_gateway.py**
```python
# infra/gateways/ap_qbo_gateway.py (implements the domain interface)
class QBOBillsGateway(BillsGateway):
    def __init__(self, qbo_client: QBOClient, sync: SyncOrchestrator,
                 log: LogRepo, mirror: BillsMirrorRepo):
        self.qbo = qbo_client
        self.sync = sync
        self.log = log
        self.mirror = mirror

    def list(self, q: ListBillsQuery) -> list[Bill]:
        return self.sync.read_refresh(
            entity="bills",
            client_id=q.advisor_id,  # advisor_id is the primary identifier
            hint=q.freshness_hint,
            mirror_is_fresh=lambda e, c, p: self.mirror.is_fresh(q.advisor_id, q.business_id, p),
            fetch_remote=lambda: self.qbo.list_bills(company_id=q.business_id, status=q.status),
            upsert_mirror=lambda raw, ver, ts: self.mirror.upsert_many(q.advisor_id, q.business_id, raw, ver, ts),
            read_from_mirror=lambda: self.mirror.list_open(q.advisor_id, q.business_id),
            on_hygiene=lambda c, code: self.log.flag_hygiene(c, code)
        )

    # Note: QBO BillsGateway only handles read operations
    # Bill payment scheduling will be handled by Ramp gateway (future rail)
    # QBO is the ledger hub - we read bills from QBO, but payments go through Ramp
```

---

## **9) Composition Root (runway/wiring.py)**

```python
# runway/wiring.py (composition root)
def create_console_service(advisor_id: str, business_id: str) -> ConsoleService:
    # Bind Domain interfaces → Infra implementations
    bills_gateway = QBOBillsGateway(
        qbo_client=QBOClient(business_id),  # QBO uses business_id (QBO realm)
        sync=SyncOrchestrator(advisor_id),  # Sync uses advisor_id for context
        log=LogRepo(),
        mirror=BillsMirrorRepo()
    )
    balances_gateway = QBOBalancesGateway(
        qbo_client=QBOClient(business_id),  # QBO uses business_id (QBO realm)
        sync=SyncOrchestrator(advisor_id),  # Sync uses advisor_id for context
        log=LogRepo(),
        mirror=BalancesMirrorRepo()
    )
    
    return ConsoleService(bills_gateway, balances_gateway)
```

> **Runway must only import domain interfaces + wiring.** Never import rails or sync from Runway.

---

## **10) Operational Mode Flags ("Simple Mode" for MVP)**

Set via env:
```
SYNC_ENABLE_RETRY=false         # or 1 retry
SYNC_ENABLE_DEDUP=true          # writes
SYNC_CACHE_TTL_BILLS=900        # 15 min
SYNC_CACHE_TTL_INVOICES=900
SYNC_CACHE_TTL_BALANCES=120
SYNC_SCHEDULER_ENABLED=false    # no background churn yet
SYNC_NIGHTLY_RECON_HOUR=03      # one recon pass nightly
STRICT_ON_SNAPSHOT=true         # strict freshness at experience edge
```

---

## **11) Tests the MVP Must Include (and Pass)**

1. **STRICT beats cache (snapshot edge)**
   - With warm mirrors, `freshness_hint=STRICT` triggers QBO fetch → INBOUND log → mirror upsert → returns mirror

2. **Bill tray service works correctly**
   - Bills load from QBO and organize into urgent/upcoming/overdue categories
   - Runway impact calculation works correctly

3. **Console snapshot service works correctly**
   - All QBO data (bills, invoices, balances) loads and calculates correctly
   - Cash position, AP/AR totals, runway days calculated correctly

4. **Throttle hygiene (QBO 429)**
   - On list operations, one bounded retry (per flag); hygiene flag visible in snapshot

5. **Stale mirror hygiene**
   - If mirror past hard TTL, snapshot shows hygiene flag but still returns last known state

---

## **12) Cursor Guards (Make Drift Impossible)**

### **.cursorrules** (Place in both repo root and `cleaned/`)
```
You may modify files ONLY under:
- cleaned/**
Do not create, edit, or delete files outside the paths above.

When asked to use legacy code, prefer:
- copying only the minimal functions needed into infra/** but they have to be sanitized first.
- assume it will need refactoring to align with new requirements
- and possibly also implementing a thinned down version so we get out from under scope-creep and pivot-cruft


Do not import from legacy folders:
- runway/services/data_orchestrators/**
- domains/*/services/** (contain architectural rot)
- infra/qbo/** (legacy paths outside MVP)
- infra/jobs/** (job scheduler, job storage)
- plaid/**, ramp/**, stripe/**

All Runway code must depend on Domains gateway interfaces only.
```

### **scripts/ci_guard.sh**
```bash
#!/usr/bin/env bash
set -euo pipefail
CHANGED=$(git diff --name-only origin/main...HEAD || true)
echo "$CHANGED" | grep -Ev '^(mvp_qbo/|scripts/|\.github/|README\.md)' >/dev/null && {
  echo "❌ Changes outside MVP lane detected."; exit 1; } || true
```

---

## **CRITICAL: Discovery & Validation Process (MANDATORY)**

### **Phase 1: Discovery & Reality Check (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

#### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

### **Phase 2: Implementation**
1. **Implement the actual task** - Use discovered reality, not assumptions
2. **Handle discovered gaps** - Fix issues found during discovery
3. **Test thoroughly** - Verify everything works
4. **Update documentation** - Keep build plans accurate

---

## **13) Migration Playbook (Cursor Step-by-Step)**

### **Step 1 — Bootstrap Nucleus**
- Create `_cleaned/{mvp,e2e}` layout above
- Add `.cursorrules`, `scripts/ci_guard.sh`, basic `pyproject.toml`, and `FastAPI` app in `api/routes.py` with `/healthz`

### **Step 2 — Copy Minimal QBO Client & Mappers**
**MANDATORY Discovery Commands:**
```bash
# Find existing QBO infrastructure
ls -la infra/qbo/
grep -r "QBORawClient" . --include="*.py"
grep -r "QBOConfig" . --include="*.py"
grep -r "QBOAuthService" . --include="*.py"
grep -r "QBOUtils" . --include="*.py"

# Check existing QBO files
cat infra/qbo/config.py | head -20
cat infra/qbo/utils.py | head -20
cat infra/qbo/auth.py | head -20
cat infra/qbo/dtos.py | head -20
```

**What to Copy & Sanitize:**
- `infra/qbo/config.py` → `_clean/mvp/infra/rails/qbo/config.py` (sanitize for MVP)
- `infra/qbo/utils.py` → `_clean/mvp/infra/rails/qbo/utils.py` (keep as-is)
- `infra/qbo/auth.py` → `_clean/mvp/infra/rails/qbo/auth.py` (sanitize for MVP)
- `infra/qbo/dtos.py` → `_clean/mvp/infra/rails/qbo/dtos.py` (keep as-is)
- `infra/qbo/client.py` → `_clean/mvp/infra/rails/qbo/client.py` (uncomment needed methods)
- `infra/qbo/health.py` → `_clean/mvp/infra/rails/qbo/health.py` (optional - may be overkill for MVP, but contains gold monitoring patterns for production)

**Validation:**
```bash
# Test existing QBO infrastructure
python -c "from infra.qbo.config import qbo_config; print('QBO config imported successfully')"
python -c "from infra.qbo.utils import QBOUtils; print('QBO utils imported successfully')"
python -c "from infra.qbo.auth import QBOAuthService; print('QBO auth imported successfully')"
python -c "from infra.qbo.dtos import QBOIntegrationDTO; print('QBO DTOs imported successfully')"
python -c "from infra.qbo.client import QBORawClient; print('QBO client imported successfully')"

# Test QBO config
python -c "from infra.qbo.config import qbo_config; print(f'QBO API URL: {qbo_config.api_base_url}')"
```

### **Step 3 — Build Domain Interfaces**
**MANDATORY Discovery Commands:**
```bash
# Find existing domain patterns
grep -r "domains/" . --include="*.py" | head -20
grep -r "gateways" . --include="*.py" | head -20
grep -r "repositories" . --include="*.py" | head -20

# Find bill/invoice/balance patterns
grep -r "Bill" . --include="*.py" | head -20
grep -r "Invoice" . --include="*.py" | head -20
grep -r "Balance" . --include="*.py" | head -20
```

**What to Create:**
- `_clean/mvp/domains/ap/gateways.py` - BillsGateway interface
- `_clean/mvp/domains/ar/gateways.py` - InvoicesGateway interface
- `_clean/mvp/domains/bank/gateways.py` - BalancesGateway interface
- `_clean/mvp/domains/*/repositories.py` - Mirror and Log repo interfaces

**Validation:**
```bash
# Test domain interfaces import
python -c "from domains.ap.gateways import BillsGateway; print('BillsGateway imported successfully')"
```

### **Step 4 — Implement Infra Repos**
**MANDATORY Discovery Commands:**
```bash
# Find existing database patterns
grep -r "sqlite" . --include="*.py" | head -20
grep -r "mirror" . --include="*.py" | head -20
grep -r "log" . --include="*.py" | head -20

# Find transaction log patterns
grep -r "transaction_log" . --include="*.py" | head -20
grep -r "TransactionLog" . --include="*.py" | head -20
```

**What to Create:**
- `_clean/mvp/infra/db/schema.sql` - Database schema
- `_clean/mvp/infra/db/session.py` - Database session
- `_clean/mvp/infra/repos/ap_repo.py` - Bills mirror repo
- `_clean/mvp/infra/repos/ar_repo.py` - Invoices mirror repo
- `_clean/mvp/infra/repos/log_repo.py` - Transaction log repo

**Validation:**
```bash
# Test database connection
python -c "from infra.db.session import get_db; print('Database session works')"

# Test repo imports
python -c "from infra.repos.ap_repo import BillsMirrorRepo; print('BillsMirrorRepo imported successfully')"
```

### **Step 5 — Implement Sync Orchestrator**
**MANDATORY Discovery Commands:**
```bash
# Find existing sync patterns
grep -r "BaseSyncService" . --include="*.py" | head -20
grep -r "sync.*service" . --include="*.py" | head -20
grep -r "orchestrator" . --include="*.py" | head -20
```

**What to Create:**
- `_clean/mvp/infra/sync/orchestrator.py` - Sync orchestrator with Smart Sync pattern
- `_clean/mvp/infra/sync/base_sync_service.py` - Base sync service (copied from legacy)

**Validation:**
```bash
# Test sync orchestrator import
python -c "from infra.sync.orchestrator import SyncOrchestrator; print('SyncOrchestrator imported successfully')"
```

### **Step 6 — Implement Infra Gateways**
**MANDATORY Discovery Commands:**
```bash
# Find existing gateway patterns
grep -r "gateway" . --include="*.py" | head -20
grep -r "Gateway" . --include="*.py" | head -20
```

**What to Create:**
- `_clean/mvp/infra/gateways/ap_qbo_gateway.py` - Bills gateway implementation
- `_clean/mvp/infra/gateways/ar_qbo_gateway.py` - Invoices gateway implementation
- `_clean/mvp/infra/gateways/bank_qbo_gateway.py` - Balances gateway implementation

**Validation:**
```bash
# Test gateway imports
python -c "from infra.gateways.ap_qbo_gateway import QBOBillsGateway; print('QBOBillsGateway imported successfully')"
```

### **Step 7 — Wire Runway**
**MANDATORY Discovery Commands:**
```bash
# Find existing runway patterns
grep -r "runway/" . --include="*.py" | head -20
grep -r "orchestrator" . --include="*.py" | head -20
```

**What to Create:**
- `_clean/mvp/runway/wiring.py` - Composition root
- `_clean/mvp/runway/services/runway_orchestrator.py` - Runway orchestrator
- Update `_clean/mvp/api/routes.py` - Real endpoints

**Validation:**
```bash
# Test runway imports
python -c "from runway.wiring import create_console_service; print('Runway wiring works')"

# Test API endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/api/advisor/test/business/test/tray
```

### **Concrete API Endpoint Example**
```python
# api/routes.py
@router.get("/api/advisor/{advisor_id}/business/{business_id}/tray")
async def get_bill_tray(advisor_id: str, business_id: str):
    """Get bills organized by urgency for advisor review"""
    tray_service = create_tray_service(advisor_id, business_id)
    tray = await tray_service.get_bill_tray(advisor_id, business_id)
    return {
        "urgent_count": len(tray.urgent_bills),
        "upcoming_count": len(tray.upcoming_bills),
        "overdue_count": len(tray.overdue_bills),
        "total_amount": str(tray.total_amount),
        "runway_impact": f"{tray.runway_impact_days} days"
    }

@router.get("/api/advisor/{advisor_id}/business/{business_id}/console")
async def get_console_snapshot(advisor_id: str, business_id: str):
    """Get complete financial snapshot for advisor dashboard"""
    console_service = create_console_service(advisor_id, business_id)
    snapshot = await console_service.get_console_snapshot(advisor_id, business_id)
    return {
        "cash_position": snapshot.cash_position,
        "bills_due_this_week": snapshot.bills_due_this_week,
        "total_ap": str(snapshot.total_ap),
        "total_ar": str(snapshot.total_ar),
        "runway_days": snapshot.runway_days,
        "hygiene_flags": snapshot.hygiene_flags
    }
```

### **Step 8 — Add the 5 Tests**
**MANDATORY Discovery Commands:**
```bash
# Find existing test patterns
grep -r "test" . --include="*.py" | head -20
find . -name "test_*.py" | head -20
grep -r "pytest" . --include="*.py" | head -20
```

**What to Create:**
- `_clean/mvp/tests/test_smart_sync.py` - Smart Sync pattern tests
- `_clean/mvp/tests/test_tray_service.py` - Tray service tests
- `_clean/mvp/tests/test_console_service.py` - Console service tests
- `_clean/mvp/tests/test_qbo_throttling.py` - QBO throttling tests
- `_clean/mvp/tests/test_stale_mirror.py` - Stale mirror tests

**Test 1: STRICT beats cache (snapshot edge)**
```python
def test_strict_beats_cache():
    """With warm mirrors, STRICT hint triggers QBO fetch → INBOUND log → mirror upsert → returns mirror"""
    # Test that STRICT hint bypasses cache and fetches from QBO
    # Verify INBOUND log entry is created
    # Verify mirror is updated with fresh data
    # Verify fresh data is returned
```

**Test 2: Bill tray service works correctly**
```python
def test_bill_tray_service():
    """Bills load from QBO and organize into urgent/upcoming/overdue categories"""
    # Test bills are loaded from QBO via domain gateway
    # Test bills are organized by urgency (urgent/upcoming/overdue)
    # Test runway impact calculation works correctly
    # Test total amount calculation
```

**Test 3: Console snapshot service works correctly**
```python
def test_console_snapshot_service():
    """All QBO data loads and calculates correctly"""
    # Test bills, invoices, balances load from QBO
    # Test cash position calculation
    # Test AP/AR totals calculation
    # Test runway days calculation
    # Test hygiene flags are detected
```

**Test 4: Throttle hygiene (QBO 429)**
```python
def test_qbo_throttling():
    """On list operations, one bounded retry; hygiene flag visible in snapshot"""
    # Test QBO 429 response handling
    # Test bounded retry (1 retry max)
    # Test hygiene flag is set on throttling
    # Test stale mirror is returned on failure
```

**Test 5: Stale mirror hygiene**
```python
def test_stale_mirror_hygiene():
    """If mirror past hard TTL, snapshot shows hygiene flag but returns last known state"""
    # Test mirror past hard TTL detection
    # Test hygiene flag is set for stale mirror
    # Test last known state is returned
    # Test fresh data is attempted to be fetched
```

**Validation:**
```bash
# Run all tests
pytest _clean/mvp/tests/ -v

# Run specific test categories
pytest _clean/mvp/tests/test_smart_sync.py -v
pytest _clean/mvp/tests/test_tray_service.py -v
pytest _clean/mvp/tests/test_console_service.py -v
pytest _clean/mvp/tests/test_qbo_throttling.py -v
pytest _clean/mvp/tests/test_stale_mirror.py -v
```

### **Step 9 — Manual Smoke with QBO Sandbox**
- Use 3–5 seeded tenants. Verify digest/console/hygiene loads; one approve path works idempotently

---

## **CRITICAL: FAQ - Answers to Common Questions**

### **Q1: QBO Sandbox Credentials**
**A:** QBO sandbox credentials are already set up in `.env`. No mocking allowed.
- QBO sandbox credentials are already configured in `.env`
- All services must hit real QBO API
- Use existing `infra/qbo/` infrastructure (config, auth, utils, client)
- Reference existing `tests/sandbox/` data as needed

### **Q2: Database Setup**
**A:** Use SQLite (`rowcol.db`) for MVP, not `oodaloo.db`.
- SQLite is sufficient for MVP
- Update `conftest.py` to use `rowcol.db`
- Transaction Log and State Mirror are SQLite tables
- See database schema in Step 4

### **Q3: Test Data**
**A:** Use real QBO sandbox data, no mocking.
- Set up QBO sandbox with test company
- Use real API calls for all testing
- Reference existing `tests/sandbox/` fixtures
- Create test data in QBO sandbox as needed

### **Q4: Domain Interfaces**
**A:** Start fresh in `_clean/mvp/domains/` but reference existing patterns.
- Ignore existing domain code (contains architectural rot)
- Use existing `domains/qbo/services/sync_service.py` as reference for convenience functions
- Create clean interfaces following Smart Sync pattern
- Focus on bills, invoices, balances first

### **Q5: Runway Services**
**A:** Replace with new architecture, but port business logic.
- Replace all 21 files with new architecture
- Port business logic from existing services
- Use `runway/services/calculators/` for product math
- Follow domain gateway pattern

### **Q6: Legacy Code Reference**
**A:** Use migration manifest for specific file mappings.
- Reference `_clean/strangled_fig/migration_manifest.md`
- Copy minimal functions needed
- Sanitize and refactor to align with new patterns
- Focus on QBO client, mappers, sync service, transaction log

### **Q7: Validation Approach**
**A:** The 5 tests are defined above in Step 8.
- STRICT beats cache test
- Bill tray service test
- Console snapshot service test
- QBO throttling test
- Stale mirror hygiene test

### **Q8: Starting Point**
**A:** Begin with Step 1 (Bootstrap) after running discovery commands.
- Run all discovery commands first
- Validate assumptions against reality
- Document what actually exists vs what task assumes
- Then proceed with Step 1

---

## **14) What NOT to Optimize Now**

- Multi-rail (Plaid, Ramp, Stripe) — **later**
- Priority queues / complex schedulers — **later**
- Cross-rail vendor graph — **later**
- Event bus fan-out — **later**
- Moving legacy folders — **leave in place**, just don't import them

---

## **15) Acceptance Criteria (Definition of Done)**

- Runway imports **only** domain gateway interfaces + wiring
- Strict reads **log INBOUND** then **upsert mirror**
- Read-only operations work correctly (no writes in QBO MVP)
- Nightly recon path exists (can be a callable runner; scheduler optional)
- The 5 MVP tests pass
- CI and `.cursorrules` prevent edits/imports outside `mvp_qbo/**`

### **What the MVP Delivers to Advisors**
- **Bill Tray**: Bills organized by urgency (urgent/upcoming/overdue) with runway impact
- **Console Snapshot**: Complete financial dashboard with cash position, AP/AR totals, runway days
- **Data Freshness**: Hygiene flags when QBO data is stale or unavailable
- **Multi-Business Support**: Advisor can view multiple businesses they manage
- **Real-time Insights**: Smart sync ensures data is fresh when needed, cached when appropriate

---

## **16) Recovery Strategy Context**

**Current State**: RowCol is being rebuilt using a Strangler-Fig approach to eliminate architectural rot and establish proper Smart Sync patterns.

**Why QBO-Only First**: The multi-rail vision requires a solid architectural foundation. We're starting with QBO-only MVP to prove the Smart Sync pattern, domain gateways, and transaction logging before adding complexity.

**Hub Progression**: In MVP, QBO is the hub because we're proving the Smart Sync pattern with a single rail. In the full vision, RowCol becomes the operational hub that orchestrates multiple rails while QBO remains the ledger hub for data lineage.

**Progressive Enhancement**: Once the architectural foundation is proven with QBO-only, we'll systematically add Ramp, Plaid, and Stripe integrations using the same patterns.

**Long-term Vision**: Full multi-rail Financial Control Plane with agentic automation, advanced analytics, and market-leading advisor tools.

## **17) Documentation vs Implementation Status**

### **Architecture Documentation (Complete)**
---> found now in _clean/architecture/
- ✅ **ADR-001**: Domain separation principles with domain gateways
- ✅ **ADR-003**: Multi-tenancy strategy with firm-first hierarchy  
- ✅ **ADR-005**: QBO API strategy with Smart Sync pattern specification
- ✅ **ADR-007**: Service boundaries with domain gateway pattern
- ✅ **ADR-010**: Multi-rail Financial Control Plane architecture
- ✅ **Comprehensive Architecture**: End-to-end product and architecture vision
- ✅ **Migration Manifest**: Concrete file-by-file porting instructions
- ✅ **Stepped Plan**: Detailed implementation roadmap with guards

### **What's Right (Keep)**
- Domain gateway pattern for rail-agnostic interfaces
- Smart Sync pattern with transaction logging and state mirror
- Progressive hub model (QBO-centric MVP → RowCol operational hub)
- Composition root for dependency injection
- Multi-rail Financial Control Plane vision

### **What's Wrong (Fix)**
- Data orchestrators (replace with domain gateways)
- Direct sync service calls from domain services
- Direct rail calls from runway services
- Missing transaction log integration
- Missing state mirror implementation
- Missing Smart Sync pattern implementation

### **What Needs to Be Done (Implementation)**
**Reference**: See `_clean/strangled_fig/migration_manifest.md` for concrete file-by-file porting instructions

1. **Implement Advisor-First Model** - advisor_id → business_id relationship (CORE FOUNDATION)
2. **Create Domain Gateways** - Define rail-agnostic interfaces in domains
3. **Create Infra Gateways** - Implement domain gateways with Smart Sync pattern
4. **Create Sync Orchestrator** - Centralized sync logic with transaction logging
5. **Update Runway Services** - Use domain gateways instead of direct calls
6. **Create Composition Root** - Single place for dependency injection
7. **Deprecate Data Orchestrators** - Replace with domain gateway pattern
8. **Implement Transaction Log** - Capture all data changes for audit trail
9. **Implement State Mirror** - Fast local reads with sync from external APIs
10. **Add Simple RBAC** - Advisor permissions per business (not firm-level yet)

---

### **Final Notes to Cursor**

- When in doubt, **prefer adapters over refactors**
- If a legacy function is tempting to reuse, **copy only that function** into `mvp_qbo/infra/...` and strip it down
- Do not "improve" legacy layers from within MVP. Propose comments instead
- Keep PRs tiny and sequential: Step 1 bootstrap → Step 2 client → … → Step 8 tests

---

This document is the **single source of truth** for the MVP recovery. Follow it literally. If the code you generate differs in shape, the **patterns and contracts above still apply** and must not be violated.
