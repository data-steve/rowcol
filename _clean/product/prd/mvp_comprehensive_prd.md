# RowCol MVP Comprehensive PRD

*Comprehensive Product Requirements Document for QBO-Only MVP Recovery*

## **Purpose**

This PRD provides the comprehensive context needed to execute the recovery build plan without requiring repeated explanations. It bridges the gap between the high-level architecture documents and the specific implementation steps.

## **1. Foundational Architecture Setup**

### **Database Layer (`_clean/mvp/infra/db/`)**
**What to Build:**
- `schema.sql` - SQLite schema with:
  - `integration_log` table (generic transaction log)
  - `mirror_bills` table (mutable state mirror)
  - `mirror_invoices` table (mutable state mirror)
  - `mirror_balances` table (mutable state mirror)
  - `entity_policy` table (TTL configuration per entity)
- `session.py` - Database session management
- `migrations/` - Database migration scripts

**Discovery Commands:**
```bash
# Find existing database patterns
grep -r "sqlite" . --include="*.py" | head -20
grep -r "mirror" . --include="*.py" | head -20
grep -r "log" . --include="*.py" | head -20
grep -r "transaction_log" . --include="*.py" | head -20
grep -r "TransactionLog" . --include="*.py" | head -20

# Check existing database files
ls -la infra/database/
cat infra/database/session.py | head -20
```

**Contamination Check:**
- Review existing `infra/database/session.py` for patterns to preserve
- Check `domains/core/services/transaction_log_service.py` for transaction log patterns
- Verify SQLite usage patterns in existing code

### **Sync Orchestrator (`_clean/mvp/infra/sync/`)**
**What to Build:**
- `orchestrator.py` - Policy-driven sync orchestrator with Smart Sync pattern
- `base_sync_service.py` - Base sync service (copied from legacy)
- `entity_policy.py` - Entity TTL configuration

**Discovery Commands:**
```bash
# Find existing sync patterns
grep -r "BaseSyncService" . --include="*.py" | head -20
grep -r "sync.*service" . --include="*.py" | head -20
grep -r "orchestrator" . --include="*.py" | head -20
grep -r "SmartSync" . --include="*.py" | head -20

# Check existing sync files
ls -la infra/jobs/
cat infra/jobs/base_sync_service.py | head -20
cat domains/qbo/services/sync_service.py | head -20
```

**Contamination Check:**
- Review `infra/jobs/base_sync_service.py` for retry/dedupe patterns
- Check `domains/qbo/services/sync_service.py` for convenience functions
- Verify Smart Sync pattern implementation in existing code

### **QBO API Layer (`_clean/mvp/infra/rails/qbo/`)**
**What to Build:**
- `client.py` - Raw QBO HTTP client (uncomment needed methods)
- `config.py` - QBO configuration (sanitize for MVP)
- `auth.py` - QBO authentication (sanitize for MVP)
- `utils.py` - QBO utilities (keep as-is)
- `dtos.py` - QBO data transfer objects (keep as-is)
- `health.py` - QBO health monitoring (optional)

**Discovery Commands:**
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
cat infra/qbo/client.py | head -20
```

**Contamination Check:**
- Review existing QBO files for patterns to preserve
- Check for database dependencies that need to be removed
- Verify QBO API usage patterns in existing code

## **2. Sync Orchestrator Patterns**

### **Smart Sync Pattern Implementation**
**What to Build:**
- Policy-driven facade over `BaseSyncService`
- Entity-specific TTL configuration
- Log → Mirror ordering enforcement
- Error → Hygiene mapping

**Key Interface:**
```python
class SyncOrchestrator:
    def read_refresh(
        self,
        entity: str,                    # "bills", "invoices", "balances"
        client_id: str,                 # advisor_id in MVP
        hint: Literal["CACHED_OK", "STRICT"],
        mirror_is_fresh: Callable[[str, str, dict], bool],
        fetch_remote: Callable[[], tuple[list[dict], str | None]],
        upsert_mirror: Callable[[list[dict], str | None, datetime], None],
        read_from_mirror: Callable[[], list[Any]],
        on_hygiene: Callable[[str, str], None],
    ) -> list[Any]:
        # Policy-driven freshness check
        # STRICT or stale/expired → rail → INBOUND log → mirror upsert → return mirror
        # CACHED_OK + fresh → return mirror
        # Error → log failure + hygiene flag + return stale mirror

    def write_idempotent(
        self,
        operation: str,                 # "ap.update_bill", "ar.update_invoice"
        client_id: str,                 # advisor_id in MVP
        idem_key: str,                  # stable key for deduplication
        call_remote: Callable[[], dict],
        optimistic_apply: Callable[[dict], None],
        on_hygiene: Callable[[str, str], None],
    ) -> dict:
        # OUTBOUND intent log → rail call → OUTBOUND result log → optimistic mirror apply
        # Error → log failure + hygiene flag + raise exception
```

**Discovery Commands:**
```bash
# Find existing sync patterns
grep -r "execute_sync_call" . --include="*.py"
grep -r "mirror_is_fresh" . --include="*.py"
grep -r "upsert_mirror" . --include="*.py"
grep -r "on_hygiene" . --include="*.py"
```

**Contamination Check:**
- Review existing sync service patterns
- Check for proper log → mirror ordering
- Verify error handling and hygiene flag patterns

## **3. Domain Layer Architecture**

### **Domain Gateways (`_clean/mvp/domains/*/gateways.py`)**
**What to Build:**
- `BillsGateway` - Interface for bill operations
- `InvoicesGateway` - Interface for invoice operations
- `BalancesGateway` - Interface for balance operations

**Key Interfaces:**
```python
# domains/ap/gateways.py
class BillsGateway(Protocol):
    def list(self, q: ListBillsQuery) -> list[Bill]: ...
    def update_bill(self, advisor_id: str, business_id: str, bill_id: str, updates: dict) -> bool: ...

# domains/ar/gateways.py
class InvoicesGateway(Protocol):
    def list(self, q: ListInvoicesQuery) -> list[Invoice]: ...
    def update_invoice(self, advisor_id: str, business_id: str, invoice_id: str, updates: dict) -> bool: ...

# domains/bank/gateways.py
class BalancesGateway(Protocol):
    def get(self, q: BalancesQuery) -> list[AccountBalance]: ...
```

**Discovery Commands:**
```bash
# Find existing domain patterns
grep -r "domains/" . --include="*.py" | head -20
grep -r "gateways" . --include="*.py" | head -20
grep -r "repositories" . --include="*.py" | head -20
grep -r "Bill" . --include="*.py" | head -20
grep -r "Invoice" . --include="*.py" | head -20
grep -r "Balance" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing domain models for patterns to preserve
- Check for business logic that should be in domains
- Verify domain separation from infrastructure

### **Domain Repositories (`_clean/mvp/domains/*/repositories.py`)**
**What to Build:**
- `BillsMirrorRepo` - Interface for bill mirror operations
- `InvoicesMirrorRepo` - Interface for invoice mirror operations
- `BalancesMirrorRepo` - Interface for balance mirror operations
- `LogRepo` - Interface for transaction log operations

**Key Interfaces:**
```python
class BillsMirrorRepo(Protocol):
    def list(self, advisor_id: str, business_id: str, status: str) -> list[Bill]: ...
    def upsert_many(self, advisor_id: str, business_id: str, bills: list[dict], version: str, timestamp: datetime) -> None: ...
    def is_fresh(self, advisor_id: str, business_id: str, policy: dict) -> bool: ...

class LogRepo(Protocol):
    def log_inbound(self, advisor_id: str, business_id: str, entity: str, data: dict, source: str) -> None: ...
    def log_outbound(self, advisor_id: str, business_id: str, operation: str, data: dict, result: dict) -> None: ...
```

**Discovery Commands:**
```bash
# Find existing repository patterns
grep -r "repository" . --include="*.py" | head -20
grep -r "mirror" . --include="*.py" | head -20
grep -r "log" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing repository patterns
- Check for proper separation of concerns
- Verify data access patterns

## **4. Runway Layer Architecture**

### **Runway Orchestrator (`_clean/mvp/runway/services/runway_orchestrator.py`)**
**What to Build:**
- Composition of domain gateways
- Product-specific business logic
- Integration with existing calculators

**Key Services:**
```python
class RunwayOrchestrator:
    def __init__(self, bills_gateway: BillsGateway, invoices_gateway: InvoicesGateway, balances_gateway: BalancesGateway):
        self.bills_gateway = bills_gateway
        self.invoices_gateway = invoices_gateway
        self.balances_gateway = balances_gateway
    
    async def get_bill_tray(self, advisor_id: str, business_id: str) -> BillTray:
        # Read bills from QBO via domain gateway
        bills = self.bills_gateway.list(ListBillsQuery(advisor_id, business_id, "OPEN"))
        # Organize by urgency for advisor workflow
        return BillTray(...)
    
    async def fix_bill_hygiene(self, advisor_id: str, business_id: str, bill_id: str, fixes: dict) -> bool:
        # Update QBO bill with corrected data
        return self.bills_gateway.update_bill(advisor_id, business_id, bill_id, fixes)
```

**Discovery Commands:**
```bash
# Find existing runway patterns
grep -r "runway/" . --include="*.py" | head -20
grep -r "orchestrator" . --include="*.py" | head -20
grep -r "calculators" . --include="*.py" | head -20
grep -r "experiences" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing runway services for patterns to preserve
- Check for business logic that should be in runway
- Verify integration with existing calculators

### **Runway Wiring (`_clean/mvp/runway/wiring.py`)**
**What to Build:**
- Composition root for dependency injection
- Interface → Implementation binding
- Service factory functions

**Key Functions:**
```python
def create_bills_gateway(advisor_id: str, business_id: str) -> BillsGateway:
    # Bind domain interface to infra implementation
    return QBOBillsGateway(advisor_id, business_id, sync_orchestrator, bills_repo)

def create_tray_service(advisor_id: str, business_id: str) -> TrayService:
    # Compose runway service with domain gateways
    return TrayService(
        bills_gateway=create_bills_gateway(advisor_id, business_id),
        invoices_gateway=create_invoices_gateway(advisor_id, business_id),
        balances_gateway=create_balances_gateway(advisor_id, business_id)
    )
```

**Discovery Commands:**
```bash
# Find existing wiring patterns
grep -r "wiring" . --include="*.py" | head -20
grep -r "composition" . --include="*.py" | head -20
grep -r "factory" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing dependency injection patterns
- Check for proper interface → implementation binding
- Verify service composition patterns

## **5. Product Requirements Integration**

### **QBO-Only MVP Product Vision**
**Core Value Proposition:**
- **Humble QBO-Only Dashboard**: Focus on bookkeeping tasks, not execution
- **Unified Client List**: Single view of all clients and their status
- **Digest Explanations**: Clear explanations of what needs attention
- **4/8/13-Week Forecasting**: Seasonal-adjusted look-ahead for cash calls (conversation starter, not statistical)
- **Backstage/Frontstage**: Advisor prep → Client deliverables
- **WWW Task Capture**: Who/What/When accountability for advisor-client interactions

**Target Customer:**
- CAS firms that don't yet use Ramp
- Facing lots of QBO hygiene issues
- Need help identifying which prep tasks are most valuable
- Want to demonstrate value to clients through deliverables

**Key Insight:**
QBO only exposes APIs for bookkeeping-style tasks (bills, invoices, payments, cash/balance), but NOT actual execution (sending money or invoices). The MVP focuses on the advisor experience of preparing for cash calls and generating client deliverables.

### **Hygiene Tray PRD Integration**
**What to Build:**
- Data quality control center for advisors
- Sync issues and data inconsistencies detection
- One-click cleanup suggestions
- QBO data hygiene fixes

**Key Features:**
- **Read Operations**: Bills, invoices, balances from QBO
- **Write Operations**: Fix vendor names, categorization, missing fields
- **Hygiene Detection**: Stale data, sync failures, data discrepancies
- **Cleanup Actions**: Update QBO data with corrected information

**Product Focus:**
- **Incomplete Records Only**: Only show bills/invoices with missing data, sync issues, inconsistencies
- **Filtered Data**: Get incomplete records from QBO API, not all records
- **Runway Impact**: Show how fixing each issue affects cash runway
- **Prep for Decision-Making**: Get data ready for Decision Console analysis

**Discovery Commands:**
```bash
# Find existing hygiene patterns
grep -r "hygiene" . --include="*.py" | head -20
grep -r "data.*quality" . --include="*.py" | head -20
grep -r "cleanup" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing hygiene detection patterns
- Check for data quality scoring logic
- Verify cleanup action patterns

### **Digest PRD Integration**
**What to Build:**
- Advisor overview dashboard
- Portfolio health summary
- Critical issues and KPIs
- Runway insights and recommendations

**Key Features:**
- **Read-Only**: Financial overview and insights
- **Data Sources**: Bills, invoices, balances from QBO
- **Calculations**: Cash position, AP/AR totals, runway days
- **Recommendations**: Data quality and business insights

**Product Focus:**
- **Consumes Tray + Console**: No direct QBO calls, uses outputs from Hygiene Tray and Decision Console
- **Client Deliverables**: Generate branded summaries for client delivery
- **Portfolio Overview**: Single view of all clients and their status
- **Conversation Starters**: 4/8/13-week forecasting for cash calls (not statistical forecasting)
- **WWW Capture**: Who/What/When task accountability for advisor-client interactions

**Discovery Commands:**
```bash
# Find existing digest patterns
grep -r "digest" . --include="*.py" | head -20
grep -r "overview" . --include="*.py" | head -20
grep -r "dashboard" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing digest calculation patterns
- Check for KPI calculation logic
- Verify recommendation generation patterns

### **Decision Console PRD Integration**
**What to Build:**
- Insights and recommendations console
- Runway impact analysis
- "Ready for Ramp" status for bills
- No payment actions (until Ramp integration)

**Key Features:**
- **Read-Only**: Insights and recommendations
- **Data Sources**: Bills, invoices, balances from QBO
- **Analysis**: Runway impact, payment readiness
- **Status**: "Ready for Ramp" indicators

**Product Focus:**
- **Complete Records Only**: Only show bills/invoices with complete, validated data
- **Filtered Data**: Get decision-ready records from QBO API, not all records
- **Analysis & Recommendations**: Focus on insights, not execution
- **Prep for Future Rails**: Mark items as "ready for Ramp" when execution capabilities are added
- **Advisor Decision Support**: Help advisors make informed decisions for client cash calls

**Discovery Commands:**
```bash
# Find existing console patterns
grep -r "console" . --include="*.py" | head -20
grep -r "decision" . --include="*.py" | head -20
grep -r "insights" . --include="*.py" | head -20
```

**Contamination Check:**
- Review existing console calculation patterns
- Check for runway impact analysis logic
- Verify recommendation generation patterns

### **Architectural Problems & Correct Approach**

**Current Problems:**
1. **Indiscriminate Data Pulling**: All three services pull ALL bills/invoices instead of filtered data
2. **Wrong Filtering Strategy**: Filtering done in runway instead of at API level
3. **QBO Execution Assumptions**: Code assumes QBO can execute payments (it can't)
4. **Missing Product Focus**: Architecture doesn't reflect humble QBO-only dashboard vision

**Correct Architecture:**
```
Hygiene Tray → BillsGateway.list_incomplete() → QBO API (filtered)
Decision Console → BillsGateway.list_decision_ready() → QBO API (filtered)
Digest → Consumes Tray + Console outputs → No direct QBO calls
```

**Domain Gateway Filtering Methods:**
```python
# domains/ap/gateways.py
class BillsGateway(Protocol):
    def list_incomplete(self, query: ListBillsQuery) -> List[Bill]:
        """For Hygiene Tray: Only bills with missing data"""
        ...
    
    def list_decision_ready(self, query: ListBillsQuery) -> List[Bill]:
        """For Decision Console: Only bills ready for decision-making"""
        ...
    
    def list_all(self, query: ListBillsQuery) -> List[Bill]:
        """For Digest: All bills (when needed)"""
        ...
```

**Service Architecture:**
- **Keep**: Existing calculators (pure business logic)
- **Keep**: Existing experiences (UI services)
- **Replace**: Data orchestrators with domain gateways
- **Create**: Wiring layer to connect experiences → domain gateways

## **6. Recursive Discovery Pattern**

### **Contamination Check Process**
**For Each File to Port:**
1. **Read the file** to understand its current purpose
2. **Identify patterns** that should be preserved
3. **Check for dependencies** that need to be removed
4. **Verify architectural alignment** with new patterns
5. **Sanitize and refactor** before porting to `_clean/`

**Discovery Commands for Each Step:**
```bash
# Find all occurrences of the pattern
grep -r "pattern_name" . --include="*.py"

# Read the broader context around each occurrence
# Understand what the method/service/route is doing
# Determine if it needs simple replacement, contextual update, or complete overhaul
# Plan comprehensive updates
# Handle dependencies
# Verify the fix
```

**Contamination Check Template:**
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

### **Whitelist Pattern Enforcement**
**Allowed Imports:**
- `_clean/mvp/domains/*/gateways.py` - Domain interfaces
- `_clean/mvp/infra/*/` - Infrastructure implementations
- `_clean/mvp/runway/*/` - Runway services

**Blocked Imports:**
- `runway/services/data_orchestrators/` - Deprecated pattern
- `domains/*/services/` - Contains architectural rot
- `infra/qbo/` - Legacy paths outside MVP
- `infra/jobs/` - Job scheduler, job storage
- `plaid/`, `ramp/`, `stripe/` - Future rails

**Discovery Commands:**
```bash
# Check for blocked imports
grep -r "from runway.services.data_orchestrators" . --include="*.py"
grep -r "from domains.*services" . --include="*.py"
grep -r "from infra.qbo" . --include="*.py"
grep -r "from infra.jobs" . --include="*.py"
grep -r "from plaid" . --include="*.py"
grep -r "from ramp" . --include="*.py"
grep -r "from stripe" . --include="*.py"
```

## **7. Migration Manifest Integration**

### **File-by-File Porting Instructions**
**Use the migration manifest for specific file mappings:**
- **ADD**: Net-new files (tiny & focused)
- **PORT**: Copy from legacy and cleanse (keep only what MVP needs)
- **ADAPT**: Thin wrapper around existing code (keep logic, expose new interface)
- **REF**: Refactor in place (light edits, same file)
- **DROP**: Leave out for MVP

**Discovery Commands:**
```bash
# Find files mentioned in migration manifest
grep -r "infra/qbo/client.py" . --include="*.py"
grep -r "domains/core/services/transaction_log_service.py" . --include="*.py"
grep -r "infra/jobs/base_sync_service.py" . --include="*.py"
```

**Contamination Check:**
- Review each file mentioned in migration manifest
- Check for patterns that should be preserved
- Verify architectural alignment
- Sanitize before porting

## **8. Success Criteria**

### **Architecture Validation**
- ✅ **Dependency Direction**: `runway/ → domains/ → infra/` (no back edges)
- ✅ **Smart Sync Pattern**: Policy-driven facade with proper log → mirror ordering
- ✅ **Domain Separation**: Clean interfaces with no infrastructure dependencies
- ✅ **Transaction Log**: Append-only audit trail for all operations
- ✅ **State Mirror**: Mutable database for fast reads

### **Product Validation**
- ✅ **Hygiene Tray**: Read/write data quality control
- ✅ **Digest**: Read-only advisor overview
- ✅ **Console**: Read-only insights and recommendations
- ✅ **QBO Integration**: Real API calls with proper error handling
- ✅ **Advisor-First**: `advisor_id` → `business_id` relationship

### **Technical Validation**
- ✅ **Database**: SQLite with proper schema
- ✅ **Sync Orchestrator**: Policy-driven with entity TTLs
- ✅ **QBO Client**: Real API calls with authentication
- ✅ **Error Handling**: Proper hygiene flag mapping
- ✅ **Testing**: 5 required tests passing

## **9. Next Steps**

1. **Execute Recovery Build Plan** with this PRD as context
2. **Follow Recursive Discovery Pattern** for each step
3. **Check Contamination** before porting any file
4. **Validate Architecture** after each step
5. **Update Documentation** as patterns are discovered

This PRD provides the comprehensive context needed to execute the recovery build plan without requiring repeated explanations or assumptions.
