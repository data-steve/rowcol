# RowCol Phase 2: Smart Tier Features - Detailed Build Plan

**Version**: 1.1  
**Date**: 2025-10-02  
**Target**: Tier 2 "Smart Runway Controls" features (~72h)  
**Pricing**: $150/client/month (3x Tier 1)  
**Timeline**: Build offline while Phase 1 is in production being user-tested

---

## Overview

Phase 2 adds intelligent features to save advisors 2-3 hours per client per week through automation and decision support, justifying 3x pricing. Features are gated with `smart_features_enabled` and build on Phase 1’s foundation.

### Value Proposition
- **Tier 1** ($50): Spreadsheet replacement - visibility and basic decisions
- **Tier 2** ($150): Smart controls - planning, automation, intelligence

### Success Criteria
- 60%+ Phase 1 users upgrade to Tier 2
- Advisors save 2-3h/client/week
- 70%+ collection response rate
- Runway impact calculations: <100ms latency
- Payment matching accuracy: >80%
- Collection sequence delivery: >95%

### Phase 2 Features (Priority Order)
1. **Earmarking / Reserved Bill Pay** (P2-2.1, 14h) - Reserve funds for critical bills
2. **Runway Impact Calculator** (P2-2.2, 8h) - Show decision impacts
3. **3-Stage Collection Workflows** (P2-2.3, 15h) - Automate invoice follow-ups
4. **Bulk Payment Matching** (P2-2.4, 15h) - Reconcile e-commerce payments
5. **Vacation Mode Planning** (P2-2.5, 10h) - Automate during absences
6. **Smart Hygiene Prioritization** (P2-2.6, 12h) - Prioritize critical fixes
7. **Variance Alerts** (P2-2.7, 8h) - Proactive notifications
8. **Testing and Compliance** (P2-2.8, 10h) - Ensure reliability, compliance

**Total Phase 2**: ~72 hours (3-4 weeks part-time)

---

## Feature 1: Earmarking / Reserved Bill Pay (P2-2.1, 14h)

### Problem Statement
Advisors need to reserve funds for must-pay bills to avoid cash crunches, as QBO scheduled payments don’t adjust available balance.

### User Story
"As an advisor, I want to earmark my client's $5k rent payment for Oct 1st, so the system knows that money is reserved and shows me only the remaining available balance when I'm approving other bills."

### Solution Overview
Extend bill model and services to support earmarking, updating runway calculations. Services first, unit tests.

### Tasks

#### Task P2-2.1.1: Extend Bill Model (S, 2h) - **Execution-Ready**
- **File**: `domains/ap/models/bill.py`
- [ ] Add fields: earmarked_amount, earmark_date, earmark_reason.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P1-1.1  
**Validation**: Unit test: Model validates earmark fields (`tests/domains/unit/test_bill.py`).  

#### Task P2-2.1.2: Implement RunwayReserveService (M, 8h) - **Execution-Ready**
- **File**: `runway/services/0_data_orchestrators/reserve_runway.py`
- [ ] Enable `smart_features_enabled`, calculate available balance (current - earmarked).
- [ ] Integrate with `runway_calculator.py`.
**References**: `1_BUILD_PLAN_PHASE2_SMART_TIER.md`, `domains/core/services/runway_calculator.py`  
**Dependencies**: P1-1.3, P1-1.6  
**Validation**: Unit test: Balance updates correctly (`tests/runway/unit/test_reserve_runway.py`).  

#### Task P2-2.1.3: Create Earmark Routes (S, 2h) - **Execution-Ready**
- **File**: `runway/routes/reserve_runway.py`, `runway/schemas/reserve_runway.py`
- [ ] POST/DELETE /advisor/{advisor_id}/clients/{client_id}/reserve.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P2-2.1.2  
**Validation**: Unit test: Routes process earmarks (`tests/runway/unit/test_routes.py`).  

#### Task P2-2.1.4: Update Digest UI (S, 2h) - **Execution-Ready**
- **File**: `runway/web/templates/digest.html`
- [ ] Display "Available: $X (Current: $Y, Earmarked: $Z)".
- [ ] Narrative copy: "Data shows available balance."
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P1-1.3  
**Validation**: Manual test: UI reflects earmarks, WCAG AA compliant.  

---

## Feature 2: Runway Impact Calculator (P2-2.2, 8h)

### Problem Statement
Advisors need to see how decisions affect runway to optimize cash flow.

### User Story
"As an advisor, I want to see runway deltas from decisions, so I can optimize cash flow."

### Solution Overview
Implement calculator to show deltas (e.g., "Delay to Oct 6 → +3 days"). Services first, unit tests.

### Tasks

#### Task P2-2.2.1: Assess and Implement ImpactCalculator (S, 4h) - **Solutioning**
- **File**: `runway/services/1_calculators/impact_calculator.py`
- [ ] Enable `smart_features_enabled`, calculate deltas for bill/invoice actions.
- [ ] Assess partial implementation, document gaps.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P1-1.3, P1-1.5  
**Validation**: Unit test: Deltas accurate (`tests/runway/unit/test_impact_calculator.py`).  

#### Task P2-2.2.2: Update Console UI (S, 4h) - **Execution-Ready**
- **File**: `runway/web/templates/console.html`
- [ ] Show deltas in VarianceChip (green/red).
- [ ] Narrative copy: "Data shows impact of X."
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P2-2.2.1  
**Validation**: Manual test: UI displays deltas, <100ms latency.  

---

## Feature 3: 3-Stage Collection Workflows (P2-2.3, 15h)

### Problem Statement
Advisors need automated follow-ups for overdue invoices to improve cash inflows.

### User Story
"As an advisor, I want automated collections for overdue invoices, so I can improve cash inflows."

### Solution Overview
Implement service for reminder, follow-up, and escalation emails. Services first, unit tests, SendGrid integration.

### Tasks

#### Task P2-2.3.1: Implement CollectionsService (L, 10h) - **Execution-Ready**
- **File**: `runway/services/0_data_orchestrators/collections.py`
- [ ] Enable `smart_features_enabled`, define 3-stage logic (e.g., reminder at 7 days, escalation at 21 days).
- [ ] Integrate with `invoice_service.py`.
**References**: `1_BUILD_PLAN_PHASE2_SMART_TIER.md`, `domains/ar/services/invoice_service.py`  
**Dependencies**: P1-1.5, P1-1.8  
**Validation**: Unit test: Stages trigger correctly (`tests/runway/unit/test_collections.py`).  

#### Task P2-2.3.2: Create Collections Route (S, 3h) - **Execution-Ready**
- **File**: `runway/routes/collections.py`, `runway/schemas/collections.py`
- [ ] POST /advisor/{advisor_id}/clients/{client_id}/collections.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P2-2.3.1  
**Validation**: Unit test: Route triggers emails (`tests/runway/unit/test_routes.py`).  

#### Task P2-2.3.3: Update Console UI (S, 2h) - **Execution-Ready**
- **File**: `runway/web/templates/console.html`
- [ ] Add collection status indicators.
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P2-2.3.2  
**Validation**: Manual test: UI shows status, WCAG AA compliant.  

---

## Feature 4: Bulk Payment Matching (P2-2.4, 15h)

### Problem Statement
Advisors need to reconcile bulk payments efficiently for e-commerce clients.

### User Story
"As an advisor, I want to match bulk payments to invoices, so I can reconcile accounts efficiently."

### Solution Overview
Implement service for suggested payment matches with manual override. Services first, unit tests.

### Tasks

#### Task P2-2.4.1: Implement PaymentMatchingService (L, 10h) - **Execution-Ready**
- **File**: `runway/services/0_data_orchestrators/payment_matching.py`
- [ ] Enable `smart_features_enabled`, suggest matches (>80% accuracy).
- [ ] Integrate with `invoice_service.py`.
**References**: `2_SMART_FEATURES_REFERENCE.md`, `domains/ar/services/invoice_service.py`  
**Dependencies**: P1-1.4, P1-1.6  
**Validation**: Unit test: Matches achieve >80% accuracy (`tests/runway/unit/test_payment_matching.py`).  

#### Task P2-2.4.2: Create Payment Matching Route (S, 3h) - **Execution-Ready**
- **File**: `runway/routes/payments.py`, `runway/schemas/payments.py`
- [ ] POST /advisor/{advisor_id}/clients/{client_id}/payment_matching.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P2-2.4.1  
**Validation**: Unit test: Route processes matches (`tests/runway/unit/test_routes.py`).  

#### Task P2-2.4.3: Update Hygiene UI (S, 2h) - **Execution-Ready**
- **File**: `runway/web/templates/tray.html`
- [ ] Display suggested matches, allow override.
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P2-2.4.2  
**Validation**: Manual test: UI shows matches, no data corruption.  

---

## Feature 5: Vacation Mode Planning (P2-2.5, 10h)

### Problem Statement
Advisors need to automate bill earmarking during absences.

### User Story
"As an advisor, I want to earmark bills for vacation periods, so I can ensure stability."

### Solution Overview
Extend earmarking for date ranges. Services first, unit tests.

### Tasks

#### Task P2-2.5.1: Extend RunwayReserveService (M, 6h) - **Execution-Ready**
- **File**: `runway/services/0_data_orchestrators/reserve_runway.py`
- [ ] Add vacation mode logic for date-range earmarking.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P2-2.1, P1-1.3  
**Validation**: Unit test: Earmarks apply for range (`tests/runway/unit/test_reserve_runway.py`).  

#### Task P2-2.5.2: Create Vacation Mode Route (S, 2h) - **Execution-Ready**
- **File**: `runway/routes/reserve_runway.py`, `runway/schemas/vacation_mode.py`
- [ ] POST /advisor/{advisor_id}/clients/{client_id}/vacation_mode.
**References**: `COMPREHENSIVE_ARCHITECTURE.md`  
**Dependencies**: P2-2.5.1  
**Validation**: Unit test: Route processes vacation mode (`tests/runway/unit/test_routes.py`).  

#### Task P2-2.5.3: Update Digest UI (S, 2h) - **Execution-Ready**
- **File**: `runway/web/templates/digest.html`
- [ ] Show vacation mode status.
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P2-2.5.2  
**Validation**: Manual test: UI reflects status, <100ms latency.  

---

## Feature 6: Smart Hygiene Prioritization (P2-2.6, 12h)

### Problem Statement
Advisors need prioritized data quality fixes based on runway impact.

### User Story
"As an advisor, I want to prioritize hygiene issues by runway impact, so I can focus on critical fixes."

### Solution Overview
Implement prioritization logic for Flowband. Services first, unit tests.

### Tasks

#### Task P2-2.6.1: Assess PriorityCalculator (S, 4h) - **Solutioning**
- **File**: `runway/services/1_calculators/priority_calculator.py`
- [ ] Assess partial implementation, document gaps.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P1-1.4  
**Validation**: Document gaps in `docs/runway/priority_calculator_gaps.md`.  

#### Task P2-2.6.2: Implement PriorityCalculator (M, 6h) - **Execution-Ready**
- **File**: `runway/services/1_calculators/priority_calculator.py`
- [ ] Enable `smart_features_enabled`, sort issues by impact (e.g., "+8 days").
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P2-2.6.1, P2-2.2  
**Validation**: Unit test: Issues sorted by impact (`tests/runway/unit/test_priority_calculator.py`).  

#### Task P2-2.6.3: Update Hygiene UI (S, 2h) - **Execution-Ready**
- **File**: `runway/web/templates/tray.html`
- [ ] Update Flowband to reflect prioritized issues.
**References**: `ui/PLAYBOOK.md`  
**Dependencies**: P2-2.6.2  
**Validation**: Manual test: UI shows prioritized issues, WCAG AA compliant.  

---

## Feature 7: Variance Alerts (P2-2.7, 8h)

### Problem Statement
Advisors need proactive alerts for significant runway changes.

### User Story
"As an advisor, I want alerts for runway changes, so I can act proactively."

### Solution Overview
Implement snapshot-based alerts via email. Services first, unit tests.

### Tasks

#### Task P2-2.7.1: Implement Snapshot Job (S, 3h) - **Execution-Ready**
- **File**: `infra/jobs/job_scheduler.py`
- [ ] Schedule daily runway snapshots.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P1-1.3  
**Validation**: Unit test: Snapshots saved (`tests/infra/unit/test_jobs.py`).  

#### Task P2-2.7.2: Implement VarianceService (S, 3h) - **Execution-Ready**
- **File**: `runway/services/1_calculators/insight_calculator.py`
- [ ] Enable `smart_features_enabled`, detect >5-day changes.
**References**: `2_SMART_FEATURES_REFERENCE.md`  
**Dependencies**: P2-2.7.1  
**Validation**: Unit test: Alerts triggered (`tests/runway/unit/test_insight_calculator.py`).  

#### Task P2-2.7.3: Create Alert Email Template (S, 2h) - **Execution-Ready**
- **File**: `infra/email/templates/variance_alert.html`
- [ ] Email with change details ("Runway dropped 8 days").
**References**: `build_plan_v5.md`  
**Dependencies**: P2-2.7.2  
**Validation**: Manual test: Email renders, >95% delivery rate.  

---

## Feature 8: Testing and Compliance (P2-2.8, 10h)

### Problem Statement
Developers need tests to ensure smart feature reliability and compliance.

### User Story
"As a developer, I want tests for smart features, so I can ensure reliability."

### Solution Overview
Add tests for smart features, ensure no financial advice language.

### Tasks

#### Task P2-2.8.1: Write Unit Tests for Smart Features (M, 6h) - **Execution-Ready**
- **File**: `tests/runway/unit/test_smart_features.py`
- [ ] Test earmarking, collections, payment matching, etc.
**References**: `1_BUILD_PLAN_PHASE2_SMART_TIER.md`  
**Dependencies**: P2-2.1–P2-2.7  
**Validation**: Run pytest; 80%+ coverage (`tests/coverage.py`).  

#### Task P2-2.8.2: Update Compliance Doc (S, 4h) - **Execution-Ready**
- **File**: `docs/runway/compliance.md`
- [ ] Document no-advice language, GDPR adherence.
**References**: `PRODUCTION_READINESS_CHECKLIST.md`  
**Dependencies**: P2-2.8.1  
**Validation**: Manual review: Compliance doc complete.  

---

## Dependencies & Risks

### Dependencies
- **External**: SendGrid for emails, QBO API write access
- **Internal**: Phase 1 deployed, Redis for caching

### Risks & Mitigations
- **Risk**: Earmarking confuses advisors
  - **Mitigation**: Clear UI labels, onboarding tutorial (P2-2.1.4)
- **Risk**: Collection emails marked as spam
  - **Mitigation**: SPF/DKIM, professional templates (P2-2.3.1)
- **Risk**: Payment matching inaccurate
  - **Mitigation**: Manual override, iterative algorithm (P2-2.4.1)
- **Risk**: Calculator gives wrong deltas
  - **Mitigation**: Extensive unit tests (P2-2.2.1)

---

## Success Metrics

### Must-Have Metrics
- ✅ 80%+ advisors use earmarking
- ✅ 2-3h saved per client/week
- ✅ 70%+ collection email response rate
- ✅ 85%+ payment matching accuracy

### Nice-to-Have Metrics
- 🎯 Runway impact calculations: <100ms
- 🎯 Collection delivery rate: >95%
- 🎯 Zero data corruption from bulk operations
- 🎯 NPS score: >50

---

**Total Estimated Effort**: 72 hours (3-4 weeks part-time)

**Files Created/Modified**: ~40 files across `runway/`, `domains/`, `infra/`, `tests/`

**Lines of Code**: ~8,000-10,000 (including tests)

**Next Steps**: Build Phase 3 after Phase 2 validation.