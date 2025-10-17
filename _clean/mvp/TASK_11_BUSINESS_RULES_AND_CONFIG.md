# Task 11: Port Business Rules and Configuration

- **Status:** `[📋]` **CRITICAL FOR PRODUCT**
- **Priority:** P0 Critical
- **Justification:** Core product logic depends on these business rules - needed before building product features
- **Execution Status:** **Execution-Ready**

## Task Checklist:
- [ ] Port `infra/config/core_thresholds.py` → `_clean/mvp/infra/config/core_thresholds.py`
- [ ] Port `infra/config/feature_gates.py` → `_clean/mvp/infra/config/feature_gates.py`
- [ ] Port `infra/config/collections_rules.py` → `_clean/mvp/infra/config/collections_rules.py`
- [ ] Port `infra/config/payment_rules.py` → `_clean/mvp/infra/config/payment_rules.py`
- [ ] Port `infra/config/risk_assessment_rules.py` → `_clean/mvp/infra/config/risk_assessment_rules.py`
- [ ] Port `infra/config/exceptions.py` → `_clean/mvp/infra/config/exceptions.py`
- [ ] Port `infra/config/rail_configs.py` → `_clean/mvp/infra/config/rail_configs.py` (QBO portions)
- [ ] Update imports in existing MVP code
- [ ] All files can be imported without errors
- [ ] Tests pass with new configuration
- [ ] All files properly documented

## Problem Statement
Need to port business rules, thresholds, and configuration from legacy codebase to support product features:
- **Runway calculations** depend on thresholds (CRITICAL_DAYS, WARNING_DAYS)
- **Tray priority scoring** depends on weights and scoring rules
- **Feature gates** control QBO-only mode and multi-rail functionality
- **Collections/Payment rules** define business logic for AP/AR
- **Risk assessment** provides scoring algorithms

## User Story
"As a developer, I need centralized business rules and configuration so that product features use consistent thresholds and logic across the application."

## Solution Overview
Port business rules and configuration from legacy `infra/config/` to MVP, maintaining clear documentation and ownership:

```python
# infra/config/core_thresholds.py → _clean/mvp/infra/config/core_thresholds.py
- RunwayThresholds: CRITICAL_DAYS=7, WARNING_DAYS=30, HEALTHY_DAYS=90
- TrayPriorities: URGENT_SCORE=80, MEDIUM_SCORE=60, TYPE_WEIGHTS
- DigestSettings: LOOKBACK_DAYS=90, FORECAST_DAYS=30
- RunwayAnalysisSettings: AP_OPTIMIZATION_EFFICIENCY, AR_COLLECTION_EFFICIENCY
- Status: CRITICAL - Core product logic depends on these

# infra/config/feature_gates.py → _clean/mvp/infra/config/feature_gates.py
- IntegrationRail enum (QBO, RAMP, PLAID, STRIPE)
- FeatureGateSettings class
- is_rail_enabled(), can_use_feature()
- QBO-only mode detection
- Status: CRITICAL - Already using this pattern in architecture

# infra/config/collections_rules.py → _clean/mvp/infra/config/collections_rules.py
- AR collections business logic
- Customer risk scoring
- Payment reliability thresholds
- Status: NEEDED FOR AR - Port when building collections console

# infra/config/payment_rules.py → _clean/mvp/infra/config/payment_rules.py
- AP payment business logic
- Vendor risk scoring
- Payment timing optimization
- Status: NEEDED FOR AP - Port when building payment scheduling

# infra/config/risk_assessment_rules.py → _clean/mvp/infra/config/risk_assessment_rules.py
- Customer & vendor risk scoring algorithms
- Risk threshold definitions
- Status: NEEDED FOR DECISIONS - Port when building decision console

# infra/config/exceptions.py → _clean/mvp/infra/config/exceptions.py
- IntegrationError, ValidationError, BusinessNotFoundError
- Custom exception hierarchy
- Status: HIGH VALUE - Consistent error handling

# infra/config/rail_configs.py → _clean/mvp/infra/config/rail_configs.py
- QBO-specific configuration (extract QBO portions)
- API endpoints, rate limits, sync frequencies
- Status: NEEDED - Consolidate existing QBO config here
```

## Architecture Note:
The `infra/config/` folder follows a clear pattern:
- **Domain-specific rule files** (collections, payment, risk)
- **Documented business logic** with industry standards
- **Configurable by business** (marked for future per-tenant customization)
- **Version controlled** (all changes tracked in git)

## Dependencies: 
Task 10 (Infrastructure Utilities) - validation and exceptions used by config

## Verification:
- Run `ls -la _clean/mvp/infra/config/` - should show config files
- Run `python -c "from infra.config.core_thresholds import RunwayThresholds; print(f'Critical days: {RunwayThresholds.CRITICAL_DAYS}')"`
- Run `python -c "from infra.config.feature_gates import FeatureGateSettings; print('Feature gates imported')"`
- Run `python -c "from infra.config.exceptions import ValidationError; print('Exceptions imported')"`
- Run `pytest _clean/mvp/tests/ -v` - all tests should pass

## Definition of Done:
- [ ] All config files ported to MVP
- [ ] Business logic properly documented with industry standards
- [ ] Existing code updated to use config where appropriate
- [ ] All tests pass
- [ ] All files properly documented
- [ ] README.md in config/ folder explaining architecture

## Git Commit:
- `git add _clean/mvp/infra/config/`
- `git commit -m "feat: port business rules and configuration (thresholds, feature gates, domain rules)"`
