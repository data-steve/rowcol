# RowCol MVP Recovery - Next Thread Handover

## **🎯 Current Status: QBO Foundation COMPLETE + All Tests Passing**

The QBO foundation has been **fully recovered, validated, and tested**. All 18 tests passing with **ZERO mocks** - everything hits real QBO API.

---

## **✅ What Was Accomplished This Thread**

### **QBO Foundation Recovery (100% Complete)**
- **QBO Authentication**: OAuth 2.0 with automatic token refresh ✅
- **QBO Client**: ADR-005 compliant with raw HTTP methods ✅
- **Database**: Single source of truth at `_clean/rowcol.db` ✅
- **Security**: No sensitive data in logs (`.cursorrules` enforced) ✅
- **Test Infrastructure**: Proper `conftest.py` with fixtures ✅

### **Critical Fixes Applied**
1. **Auth Service Bug**: Fixed unreachable `return None` in `get_valid_access_token()`
2. **Token Refresh**: Fixed field names (`access_token`/`refresh_token`)
3. **Database Path**: Centralized in `conftest.py` - single source of truth
4. **Token Save**: Fixed `_save_system_tokens()` to handle INSERT and UPDATE
5. **Mock Elimination**: Removed ALL mocks - enforced real API testing

### **Test Suite: 18/18 Passing ✅**

```bash
cd _clean/mvp && poetry run pytest tests/ -v

# All tests passing:
✅ test_qbo_simple.py (3 tests)        - Basic API connectivity
✅ test_qbo_auto_refresh.py (3 tests)  - Token refresh mechanism  
✅ test_qbo_throttling.py (3 tests)    - Rate limiting behavior
✅ test_smart_sync.py (4 tests)        - Smart Sync pattern
✅ test_stale_mirror.py (4 tests)      - Cache staleness detection
✅ test_system_tokens.py (1 test)      - Database token management

Total: 18 tests, 0 failures, 0 mocks
```

### **Testing Principles Established**
- ✅ **NO MOCKS ALLOWED** - Added to `.cursorrules`
- ✅ **CLEANSE AND FIX** over deleting - Never delete failing tests
- ✅ **Real API Only** - All tests hit QBO sandbox
- ✅ **Proper Fixtures** - `conftest.py` provides database and QBO fixtures

---

## **📁 Current File Structure**

```
_clean/
├── rowcol.db                    # ✅ Single source of truth database
├── .cursorrules                 # ✅ Testing + security rules enforced
└── mvp/
    ├── infra/
    │   ├── rails/qbo/          # ✅ QBO client with auto-refresh working
    │   │   ├── auth.py         # ✅ Fixed token refresh
    │   │   ├── client.py       # ✅ Raw HTTP methods
    │   │   └── config.py       # ✅ QBO configuration
    │   ├── gateways/qbo/       # ✅ Gateway implementations
    │   ├── db/                 # ✅ Database session management
    │   │   └── session.py      # ✅ Centralized DB config
    │   └── sync/               # ✅ Sync orchestrator
    ├── domains/                # ✅ Gateway interfaces
    │   ├── ap/                 # ✅ Bills gateway
    │   ├── ar/                 # ✅ Invoices gateway
    │   └── bank/               # ✅ Balances gateway
    ├── runway/                 # ✅ Product services
    │   └── services/           # ✅ Tray, console, digest services
    └── tests/                  # ✅ ALL 18 TESTS PASSING
        ├── conftest.py         # ✅ Proper test infrastructure
        ├── test_qbo_simple.py
        ├── test_qbo_auto_refresh.py
        ├── test_qbo_throttling.py
        ├── test_smart_sync.py
        ├── test_stale_mirror.py
        └── test_system_tokens.py
```

---

## **🧪 How to Run Tests**

```bash
# Run all tests
cd _clean/mvp && poetry run pytest tests/ -v

# Run specific test file
poetry run pytest tests/test_qbo_simple.py -v

# Run with output
poetry run pytest tests/ -v -s

# Run only QBO integration tests
poetry run pytest tests/ -v -m qbo_real_api
```

---

## **🔧 What Needs to Be Done Next**

### **🚨 CRITICAL DISCOVERY: Config Consolidation Issue**

**Problem**: We have **TWO** QBO config implementations:
1. **MVP**: `_clean/mvp/infra/rails/qbo/config.py` (QBOConfig) - simpler, working
2. **Legacy**: `infra/config/rail_configs.py` (QBOSettings) - more comprehensive

**Differences**:
- **MVP QBOConfig**: Basic OAuth + API URLs (60 lines)
- **Legacy QBOSettings**: OAuth + API URLs + Retry config + Sync config + Feature flags (97 lines)

**Decision Needed** (for Task 11):
- ✅ **RECOMMENDED**: Keep `infra/rails/{rail}/config.py` pattern (each rail owns its config)
- ❌ **NOT RECOMMENDED**: Move to centralized `infra/config/rail_configs.py` (legacy pattern)

**Action for Task 11**:
1. Extract additional settings from legacy `QBOSettings`:
   - `token_refresh_buffer_minutes`
   - `max_api_retries`, `api_timeout_seconds`, `rate_limit_delay_seconds`
   - `sync_batch_size`, `sync_retry_attempts`, `sync_retry_delay_seconds`
   - Entity-specific feature flags (bills, invoices, customers, vendors)
2. Merge into MVP `_clean/mvp/infra/rails/qbo/config.py`
3. Keep rail-specific pattern for consistency

### **Phase 1: Port Business Rules (Task 11)**
**CRITICAL for product features** - Must do before building tray/console:

1. **`infra/config/core_thresholds.py`** (P0 Critical)
   - RunwayThresholds: CRITICAL_DAYS=7, WARNING_DAYS=30, HEALTHY_DAYS=90
   - TrayPriorities: URGENT_SCORE=80, TYPE_WEIGHTS
   - Required for runway calculations and tray priority scoring

2. **`infra/config/feature_gates.py`** (P0 Critical)
   - FeatureGateSettings: QBO-only mode detection
   - Already using this pattern in architecture

3. **`infra/config/exceptions.py`** (P1 High)
   - IntegrationError, ValidationError, BusinessNotFoundError
   - **Already ported**: `_clean/mvp/infra/config/exceptions.py` exists ✅

4. **`infra/utils/validation.py`** (P1 High)
   - Data validation for tray hygiene
   - Field-level error reporting

### **Phase 2: Build Product Experiences**
Once Task 11 complete:

**NOTE**: Most of this is already done! Just needs testing:

1. **✅ Gateway Filtering - DONE**
   - `list_incomplete()` - Bills/invoices with missing data (Hygiene Tray)
   - `list_payment_ready()` - Bills ready for payment scheduling (Decision Console)
   - **Location**: `_clean/mvp/infra/gateways/qbo/bills_gateway.py` (lines 57, 75)

2. **✅ Wiring Layer - DONE**
   - Full composition root in `_clean/mvp/runway/wiring.py`
   - Factory methods: `create_bills_gateway()`, `create_tray_service()`, `create_console_service()`
   - Proper dependency injection with singleton repos
   - **Status**: 270 lines of production-ready wiring code

3. **✅ Experience Services - DONE**
   - **TrayService**: `_clean/mvp/runway/services/tray_service.py` (uses `list_incomplete()`)
   - **ConsoleService**: `_clean/mvp/runway/services/console_service.py` (uses `list_payment_ready()`)
   - **DigestService**: Consumes Tray + Console outputs (no direct QBO calls)

**What's Missing**: Integration tests to prove the full stack works end-to-end!

---

## **🚨 Critical Rules for Next Thread**

### **Database Path - SINGLE SOURCE OF TRUTH**
```python
# ✅ ALWAYS use:
from conftest import get_database_engine, get_database_url

# ❌ NEVER hardcode:
database_url = 'sqlite:///../../_clean/rowcol.db'  # DON'T DO THIS
```

### **Testing Rules (in `.cursorrules`)**
- **NEVER use mocks** - all tests must hit real QBO API
- **NEVER delete tests** - always fix/cleanse instead
- **Principle: CLEANSE AND FIX over DELETING**
- Use `conftest.py` fixtures for database and QBO access

### **Security Rules**
- **NEVER print tokens** in logs or context  
- **Use conftest fixtures** - they handle token access safely
- **Follow `.cursorrules`** - all edits within `_clean/` only

### **Architecture Compliance**
- **Strangler-Fig**: Only work within `_clean/` boundaries
- **Three-Layer**: `runway/ → domains/ → infra/`
- **No Legacy Imports**: Don't reference code outside `_clean/`

---

## **📋 Task Status Summary (Tasks 1-11)**

### **✅ Infrastructure Foundation (Tasks 1-8) - COMPLETE**
| Task | Status | Notes |
|------|--------|-------|
| Task 1: Bootstrap MVP Nucleus | ✅ Complete | Foundation structure created |
| Task 2: Copy QBO Infrastructure | ✅ Complete | QBO client with auto-refresh working |
| Task 3: Database Schema | ✅ Complete | SQLite schema + ORM operational |
| Task 4: Sync Orchestrator | ✅ Complete | Smart Sync pattern implemented |
| Task 5: Domain Gateways | ✅ Complete | Rail-agnostic interfaces created |
| Task 6: Infra Gateways | ✅ Complete | QBO implementations working |
| Task 7: Bridge to Runway | ✅ Complete | Services created, need wiring |
| Task 8: Test & Validate | ✅ Complete | **18/18 tests passing, all real QBO API** |

**Note**: Tasks 1-8 focused on **QBO foundation only**. All critical issues resolved:
- ✅ Database centralized with SQLAlchemy ORM
- ✅ OAuth 2.0 with automatic token refresh
- ✅ Real API testing (no mocks)
- ✅ Smart Sync pattern working
- ✅ Security rules enforced

### **📋 New Infrastructure Tasks (Tasks 9-11) - PLANNED**
| Task | Status | Notes |
|------|--------|-------|
| Task 9: API Infrastructure | 📋 Planned | Rate limiting, retry, circuit breaker (deferred - not urgent) |
| Task 10: Utils & Validation | 📋 Planned | Validation, error handling, enums (some overlap with MVP) |
| Task 11: Business Rules & Config | 📋 Planned | **CRITICAL for product features** - thresholds, feature gates, domain rules |

**Note**: Tasks 9-11 are **new additions** discovered after Tasks 1-8 were complete. They port additional infrastructure from legacy code that will be needed for product features.

---

## **🎯 Success Criteria Met**

✅ **QBO API Working**: Real sandbox connectivity validated  
✅ **Token Refresh**: Automatic refresh working correctly  
✅ **Database Consistency**: Single database, all components aligned  
✅ **Test Coverage**: 18 tests, all passing, zero mocks  
✅ **Security Compliance**: No sensitive data exposure  
✅ **Architecture Compliance**: Clean three-layer separation  

---

## **🔗 Key Files Reference**

- **Database**: `_clean/rowcol.db` (working tokens)
- **Auth Service**: `_clean/mvp/infra/rails/qbo/auth.py` (auto-refresh working)
- **QBO Client**: `_clean/mvp/infra/rails/qbo/client.py` (raw HTTP methods)
- **Test Config**: `_clean/mvp/tests/conftest.py` (fixtures for all tests)
- **Test Files**: `_clean/mvp/tests/*.py` (all 18 tests passing)

---

## **💡 Next Thread Should Focus On**

**Priority 1: Port Business Rules (Task 11 - CRITICAL)**
Before testing product features, we need:
1. **`infra/config/core_thresholds.py`** - Runway thresholds, tray priorities (CRITICAL)
2. **`infra/config/feature_gates.py`** - QBO-only mode detection (CRITICAL)
3. **`infra/utils/validation.py`** - Data validation for tray hygiene (HIGH VALUE)
4. **`infra/config/exceptions.py`** - Already done ✅, but verify imports work

**Priority 2: Integration Testing**
Once business rules ported:
1. **Test Full Stack End-to-End**
   - TrayService → Gateway → Sync → QBO → Mirror → Domain objects
   - Verify filtering works (`list_incomplete()`, `list_payment_ready()`)
   - Test with real QBO data

2. **Test Wiring Layer**
   - Verify `create_tray_service()` creates working service
   - Verify dependency injection works correctly
   - Test with multiple advisor/business combinations

3. **Build API Endpoints** (Optional)
   - `/api/tray/{business_id}` - Hygiene tray
   - `/api/console/{business_id}` - Decision console
   - Prove HTTP → Service → Gateway → QBO flow works

---

## **📋 Task 9: Port Production-Grade API Infrastructure (DEFERRED)**

**Status**: 📋 Planned (not urgent)  
**Priority**: P1 High (but deferred)  
**Why Deferred**: Current simple client works for MVP, not hitting rate limits yet

### **What This Task Does:**
Ports production-grade patterns from `infra/api/base_client.py`:
- Rate limiting with configurable limits
- Exponential backoff retry logic
- Circuit breaker pattern
- Response caching with TTL
- Typed error hierarchy

### **When You'll Need It:**
- Before production launch
- Multi-user/high-volume scenarios
- When hitting QBO rate limits (30 req/min sandbox, 500 req/min production)

### **Quick Implementation:**
1. Port `infra/api/base_client.py` → `_clean/mvp/infra/api/base_client.py`
2. Update `QBORawClient` to extend `BaseAPIClient`
3. Add retry logic to `QBOAuthService` for token refresh
4. Test with `test_qbo_throttling.py` (already exists)

**Decision**: Skip for now, implement when needed.

---

## **📋 Task 10: Port Infrastructure Utilities (OPTIONAL)**

**Status**: 📋 Planned (some overlap with MVP)  
**Priority**: P1 High  

### **What This Task Does:**
Ports utilities from `infra/utils/`:
- **validation.py**: Data validation (HIGH VALUE for tray hygiene)
- **error_handling.py**: Centralized error management decorators
- **enums.py**: ⚠️ PARTIAL - `FreshnessHint` already exists in MVP

### **What's Already in MVP:**
- ✅ `FreshnessHint` in `_clean/mvp/infra/sync/entity_policy.py`
- ✅ Basic error handling in gateways

### **What's Useful to Port:**
1. **validation.py** (HIGH VALUE)
   - `ValidationResult`, `ValidationRule` dataclasses
   - Business data validation for runway calculations
   - Field-level error reporting for tray hygiene

2. **error_handling.py** (HIGH VALUE)
   - `@handle_integration_errors` decorator
   - `@retry_with_backoff` decorator
   - Eliminates duplicate try/catch patterns

### **Quick Implementation:**
1. Port `infra/utils/validation.py` → `_clean/mvp/infra/utils/validation.py`
2. Port `infra/utils/error_handling.py` → `_clean/mvp/infra/utils/error_handling.py`
3. Skip `enums.py` - already have what we need

**Decision**: Port validation.py when building tray hygiene features.

---

## **📋 Task 11: Port Business Rules & Configuration (CRITICAL)**

**Status**: 📋 Planned  
**Priority**: P0 Critical - **DO THIS BEFORE PRODUCT FEATURES**  

### **⚠️ Config Consolidation Required:**

**Problem**: QBO config exists in two places:
- **MVP**: `_clean/mvp/infra/rails/qbo/config.py` (60 lines, working)
- **Legacy**: `infra/config/rail_configs.py::QBOSettings` (97 lines, comprehensive)

**Action**: Merge additional settings into MVP config:
```python
# Add to _clean/mvp/infra/rails/qbo/config.py:
- token_refresh_buffer_minutes
- max_api_retries, api_timeout_seconds, rate_limit_delay_seconds  
- sync_batch_size, sync_retry_attempts, sync_retry_delay_seconds
- Entity-specific feature flags (bills, invoices, customers, vendors)
```

### **What This Task Does:**

#### **1. Core Thresholds (P0 CRITICAL)**
Port `infra/config/core_thresholds.py` → `_clean/mvp/infra/config/core_thresholds.py`

**Why Critical**: Runway calculations and tray priority scoring depend on these:
```python
# RunwayThresholds
CRITICAL_DAYS = 7      # Less than 1 week = critical alert
WARNING_DAYS = 30      # Less than 1 month = warning
HEALTHY_DAYS = 90      # More than 3 months = healthy

# TrayPriorities  
URGENT_SCORE = 80      # Requires immediate attention
MEDIUM_SCORE = 60      # Should be handled today
TYPE_WEIGHTS = {
    "overdue_bill": 35,
    "upcoming_payroll": 40,
    "overdue_invoice": 30,
    ...
}

# DigestSettings
LOOKBACK_DAYS = 90
FORECAST_DAYS = 30

# RunwayAnalysisSettings
AP_OPTIMIZATION_EFFICIENCY = 0.1   # 10% of overdue AP can be optimized
AR_COLLECTION_EFFICIENCY = 0.3     # 30% collection efficiency
```

#### **2. Feature Gates (P0 CRITICAL)**
Port `infra/config/feature_gates.py` → `_clean/mvp/infra/config/feature_gates.py`

**Why Critical**: Already using this architecture pattern:
```python
class FeatureGateSettings:
    enable_qbo = os.getenv("ENABLE_QBO_INTEGRATION", "true")
    enable_ramp = os.getenv("ENABLE_RAMP_INTEGRATION", "false")
    
    # QBO-only mode detection
    is_qbo_only_mode = enable_qbo and not any([enable_ramp, enable_plaid, enable_stripe])
    
    # Product capabilities
    enable_payment_execution = enable_ramp  # Requires Ramp
    enable_reserve_management = enable_ramp
```

#### **3. Exceptions (P1 HIGH)**
**Already done** ✅: `_clean/mvp/infra/config/exceptions.py` exists  
**Action**: Just verify imports work

#### **4. Domain Rules (NEEDED FOR FEATURES)**

Port when building respective features:
- `collections_rules.py` → AR collections logic (for collections console)
- `payment_rules.py` → AP payment logic (for payment scheduling)
- `risk_assessment_rules.py` → Risk scoring (for decision console)

### **Quick Implementation Checklist:**

**Step 1: Consolidate QBO Config**
- [ ] Open `_clean/mvp/infra/rails/qbo/config.py`
- [ ] Add settings from `infra/config/rail_configs.py::QBOSettings`
- [ ] Test that existing code still works

**Step 2: Port Core Thresholds**
- [ ] Copy `infra/config/core_thresholds.py` → `_clean/mvp/infra/config/core_thresholds.py`
- [ ] Keep all thresholds exactly as-is (they're battle-tested)
- [ ] Verify imports work

**Step 3: Port Feature Gates**
- [ ] Copy `infra/config/feature_gates.py` → `_clean/mvp/infra/config/feature_gates.py`
- [ ] Verify QBO-only mode detection works
- [ ] Test feature flag checks

**Step 4: Verify Exceptions**
- [ ] Confirm `_clean/mvp/infra/config/exceptions.py` works
- [ ] Update imports in gateways if needed

**Step 5: Test Everything**
```bash
# Verify imports work
python -c "from infra.config.core_thresholds import RunwayThresholds; print(RunwayThresholds.CRITICAL_DAYS)"
python -c "from infra.config.feature_gates import FeatureGateSettings; print('OK')"
python -c "from infra.config.exceptions import IntegrationError; print('OK')"

# Run existing tests - should still pass
poetry run pytest tests/ -v
```

---

**The QBO foundation is rock solid. All tests passing. Port business rules (Task 11), then ready to test product experiences.**
