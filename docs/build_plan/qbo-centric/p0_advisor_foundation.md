# RowCol Phase 0: Advisor Foundation - Detailed Build Plan

**Version**: 1.0  
**Date**: 2025-10-02  
**Target**: Foundational architecture ready for Phase 1 in 1-2 weeks (~40h)  
**Goal**: Retrofit the existing codebase to support the multi-product, advisor-first architecture.

## ⚠️ **CRITICAL BUILD PLAN REALITY CHECK**

This is a foundational, architectural phase. All tasks are prerequisites for subsequent product development. Missteps here will have cascading effects.

### **What This Build Plan Is:**
- An explicit, developer-level plan to implement the foundational architecture described in `ADVISOR_FIRST_ARCHITECTURE.md`.
- A set of atomic, verifiable tasks intended for agent-led or hands-free execution.
- The required "healing process" to align the codebase with the strategic vision before building features.

### **Core Demands**:
- Establish a new `advisor/` layer for shared, cross-product logic.
- Implement a robust multi-tenancy model scoped by `advisor_id`.
- Migrate the database and authentication systems to be advisor-centric.
- Create a flexible feature gating system to support tiered pricing.

---

## Overview

Phase 0 is the essential prerequisite for all `runway/` product development. It establishes the `advisor/` layer, refactors core services for secure multi-tenancy using `advisor_id` scoping, and implements a feature gating system. This phase addresses critical architectural gaps, ensuring that all future work is built on a scalable and secure foundation aligned with the multi-product vision.

### Success Criteria
- ✅ `advisor/` directory and core models (`Advisor`, `Client`) are created and fully unit-tested.
- ✅ All data-accessing services inherit from a `ScopedService` that strictly enforces `advisor_id` filtering.
- ✅ Database schema is successfully migrated to use `advisor_id` instead of `firm_id`.
- ✅ JWTs contain and use `advisor_id` for all authenticated endpoints.
- ✅ Feature gating service can successfully protect routes based on an advisor's subscription tier.
- ✅ Integration tests prove zero data leakage is possible between different advisors.
- ✅ 100% of Phase 0 tasks are complete and validated before Phase 1 begins.

---

## Feature 1: Establish `advisor/` Layer (P0-1, 12h)

### Problem Statement
The codebase lacks a dedicated layer for cross-product advisor logic, risking entanglement between core domains (`domains/`) and specific products (`runway/`).

### User Story
"As a developer, I need a dedicated `advisor/` layer to house all cross-product advisor workflow logic, separating it from `domains/` and `runway/`."

### Solution Overview
Create the directory structure, SQLAlchemy models, and foundational services for managing advisors and their client relationships, complete with unit tests.

### Tasks

#### Task P0-1.1: Create Advisor & Client Models (M, 6h) - **Execution-Ready**
- **Files**: `advisor/client_management/models/advisor.py`, `advisor/client_management/models/client.py`
- [ ] Create directory `advisor/client_management/models/`.
- [ ] In `advisor.py`, define the `Advisor` SQLAlchemy model with fields: `advisor_id` (String, primary_key), `email` (String, unique), `name` (String). Inherit from `Base` and `TimestampMixin`.
- [ ] In `client.py`, define the `Client` model to map advisors to businesses: `id` (Integer, pk), `advisor_id` (String, FK to `advisors.advisor_id`), `business_id` (String, FK to `businesses.business_id`).
**References**: `ADVISOR_FIRST_ARCHITECTURE.md`, `infra/database/models.py`
**Dependencies**: None
**Validation**: Unit tests in `tests/advisor/unit/test_models.py` confirm model creation, relationships, and serialization.

#### Task P0-1.2: Implement ClientService (M, 6h) - **Execution-Ready**
- **File**: `advisor/client_management/services/client_service.py`
- [ ] Create directory `advisor/client_management/services/`.
- [ ] Implement `ClientService` with methods: `add_client_to_advisor(advisor_id, business_id)`, `list_clients_for_advisor(advisor_id)`, and `remove_client_from_advisor(advisor_id, business_id)`.
**References**: `domains/core/services/base_service.py`
**Dependencies**: P0-1.1
**Validation**: Unit tests in `tests/advisor/unit/test_client_service.py` prove service methods correctly manipulate the `Client` model and respect `advisor_id`.

---

## Feature 2: Implement Multi-Tenancy & Scoping (P0-2, 16h)

### Problem Statement
The current tenancy model is `business_id`-centric and does not support an advisor securely managing a portfolio of multiple, distinct clients.

### User Story
"As a developer, I need to refactor core services to be `advisor_id`-aware, ensuring all data access is securely scoped and preventing any possibility of data leakage."

### Solution Overview
Refactor the base service to enforce `advisor_id` scoping across all database queries, migrate the database schema to reflect the advisor-centric model, and update the authentication system to use `advisor_id` in JWTs.

### Tasks

#### Task P0-2.1: Refactor TenantAwareService to ScopedService (M, 8h) - **Execution-Ready**
- **File**: `domains/core/services/base_service.py`
- [ ] Rename `TenantAwareService` to `ScopedService`.
- [ ] Refactor its constructor to accept an `advisor_id`.
- [ ] Modify its internal query-building methods to automatically join from the target model through the `Client` mapping table to filter all results by the service's `advisor_id`.
**References**: `ADVISOR_FIRST_ARCHITECTURE.md`
**Dependencies**: P0-1.1
**Validation**: Unit tests in `tests/domains/unit/core/test_base_service.py` confirm that any service inheriting from `ScopedService` automatically and correctly filters results by the provided `advisor_id`.

#### Task P0-2.2: Create Database Migration for Advisor Model (S, 4h) - **Execution-Ready**
- **File**: `alembic/versions/xxxx_rename_firm_to_advisor.py`
- [ ] Use `alembic revision` to generate a new migration file.
- [ ] Write the `upgrade` function to rename the `firms` table to `advisors` and the `firm_id` column to `advisor_id`. Also, add a foreign key from `businesses` to `advisors` if it was modeled that way previously.
- [ ] Write the corresponding `downgrade` function.
**References**: Alembic documentation, `ADVISOR_FIRST_ARCHITECTURE.md`
**Dependencies**: P0-1.1
**Validation**: The migration runs successfully up and down on a test database. The schema changes are verified using a DB tool.

#### Task P0-2.3: Update Authentication to use advisor_id (S, 4h) - **Execution-Ready**
- **File**: `infra/auth/auth.py`
- [ ] Update the JWT creation logic to include `advisor_id` in the token's subject or payload.
- [ ] Create a new FastAPI dependency injector (e.g., `get_current_advisor_id`) that extracts the `advisor_id` from the request's validated JWT.
**References**: FastAPI security documentation.
**Dependencies**: P0-2.1
**Validation**: Unit tests for JWT creation confirm the `advisor_id` is present. Integration tests for a protected route confirm the dependency injector correctly provides the `advisor_id`.

---

## Feature 3: Implement Feature Gating System (P0-3, 12h)

### Problem Statement
The platform needs a mechanism to enable or disable features based on an advisor's subscription tier to support the multi-tiered pricing model.

### User Story
"As a developer, I need a feature gating system to control access to different product tiers (e.g., `basic_ritual_only`, `smart_features_enabled`)."

### Solution Overview
Enhance the `Advisor` model with subscription fields. Create a reusable service to check feature access and a FastAPI dependency to protect routes.

### Tasks

#### Task P0-3.1: Enhance Advisor Model for Subscriptions (S, 2h) - **Execution-Ready**
- **File**: `advisor/client_management/models/advisor.py`
- [ ] Add `runway_tier` (String, default='basic') and `feature_flags` (JSONB, nullable=True) columns to the `Advisor` model.
- [ ] Create a new Alembic migration for this schema change.
**Dependencies**: P0-1.1
**Validation**: Migration runs successfully. Model reflects new fields.

#### Task P0-3.2: Implement FeatureService (M, 6h) - **Execution-Ready**
- **File**: `advisor/subscriptions/feature_service.py`
- [ ] Create directories `advisor/subscriptions/`.
- [ ] Implement `FeatureService` with a method `can_use_feature(advisor: Advisor, feature_name: str) -> bool`.
- [ ] The logic should check the advisor's `runway_tier` against a predefined map of features per tier, and then check for any overrides in the `feature_flags` JSON.
**References**: `2_SMART_FEATURES_REFERENCE.md` for tier definitions.
**Dependencies**: P0-3.1
**Validation**: Unit tests in `tests/advisor/unit/test_feature_service.py` cover various scenarios: basic tier access, premium tier access, and feature flag overrides.

#### Task P0-3.3: Create Feature Gating Decorator (S, 4h) - **Execution-Ready**
- **File**: `advisor/subscriptions/dependencies.py`
- [ ] Create a FastAPI dependency function, `require_feature(feature_name: str)`, that can be used on routes.
- [ ] This dependency should use the `FeatureService` and the current advisor to check for access, raising an `HTTPException` with status code 403 if access is denied.
**Dependencies**: P0-3.2, P0-2.3
**Validation**: An integration test in `tests/advisor/integration/test_feature_gating.py` shows the dependency correctly protects a sample route and allows access for authorized advisors.

---

**Total Estimated Effort**: ~40 hours (1 week full-time)

**Next Steps**: Once Phase 0 is complete and fully validated, development on the Phase 1 MVP can begin.
