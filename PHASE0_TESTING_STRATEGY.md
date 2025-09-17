# Phase 0 Testing Strategy

## Overview
We're in an "in-between" state where parked features (payments, jobs, advanced reconciliation, etc.) cause SQLAlchemy relationship errors that prevent even core model instantiation. Rather than fix every parked feature relationship, we use **targeted testing** for Phase 0 only.

## Phase 0 Core Components (Must Work)
Based on `docs/Oodaloo_v4.2_Build_Plan.md`, Phase 0 includes:

- ✅ **Business Model** - Single business MVP (replaces Client/Firm)
- ✅ **User Model** - Single user per business  
- ✅ **QBO Integration** - Basic connection (initially mocked)
- ✅ **Prep Tray** - Cash runway management interface
- ✅ **Core Database** - SQLite with basic seeding
- ✅ **FastAPI App** - Basic API structure with uvicorn

## Testing Approach

### ✅ DO: Targeted Testing
```bash
# Test only Phase 0 core functionality
poetry run pytest tests/test_phase0_core.py -v -s --disable-warnings

# Test specific Phase 0 components
poetry run pytest runway/tray/tests/ -v -s --disable-warnings
poetry run pytest tests/test_database.py::test_seed_business -v -s --disable-warnings
```

### ❌ DON'T: Broadcast Testing (Until Later Phases)
```bash
# Avoid these until Phase 1+
poetry run pytest  # Will fail due to parked feature relationships
poetry run pytest domains/  # Will hit payment/job/reconciliation errors
```

## Known Issues (Will Fix in Later Phases)

### Phase 1+ Features (Currently Parked)
- **Payment Processing** (`domains/ap/models/payment.py`, `domains/ar/models/payment.py`)
  - Missing customer_id foreign keys
  - Relationship errors with Customer/Invoice models
- **Job Costing** (All job-related models/services)
  - Job model relationships commented out
  - Transaction.job_id parked
- **Advanced Reconciliation** (`domains/bank/services/cash_reconciliation.py`)
  - Complex identity_graph dependencies
- **Policy Corrections** (`domains/policy/models/correction.py`)
  - AmbiguousForeignKeysError with User relationships

### SQLAlchemy Relationship Issues
The core issue is that SQLAlchemy tries to configure **ALL** relationships when **ANY** model is instantiated, even if we're only testing core models. Parked features have broken relationships that prevent the entire ORM from initializing.

## Success Criteria for Phase 0
- ✅ `uvicorn main:app --reload` starts without errors
- ✅ Core imports work (`from domains.core.models import Business, User`)
- ✅ Business and User models can be created and persisted
- ✅ Basic database seeding works
- ✅ Prep Tray functionality works
- ✅ QBO integration service can be instantiated (even if mocked)

## Future Phase Testing
- **Phase 1**: Add payment processing tests back
- **Phase 2**: Add job costing and advanced reconciliation tests  
- **Phase 3**: Full test suite with `poetry run pytest`
