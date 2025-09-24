# Oodaloo Engineering Backlog

*Generated from v4.5 Build Plan on 2025-09-24*

**Instructions:**
1.  Choose a task that is `Ready for Spec`.
2.  Run the `@spec "<Task Title>"` command in Cursor.
3.  Once the `TASK.md` is approved, switch to Auto mode and run `@build`.
4.  After the task is complete, I will update the status here to `Done ✔️`.

---
## Phase 1: Smart AP & Payment Orchestration

#### **Task: Implement 'Latest Safe Pay Date' calculation**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 140): "Needed to justify Smart AP as a $99/mo add-on."
- **Code Pointers:**
  - `domains/ap/services/payment.py` (The `PaymentService` is a likely candidate for this logic).
  - `domains/ap/models/bill.py`
  - `domains/ap/models/vendor.py`
- **Dependencies:** None. The core AP services exist.
- **Verification:** A search of the codebase confirms no "Latest Safe Pay Date" logic currently exists.
- **Definition of Done:**
  - A new method is created that can calculate the latest possible payment date for a bill without incurring penalties.
  - The calculation correctly uses vendor payment terms and bill due dates from QBO data.
  - The feature is covered by unit tests with scenarios for different payment terms (Net 30, Net 60, Due on Receipt, etc.).
- **Next Action:** Ready for you to run `@spec "Implement 'Latest Safe Pay Date' calculation"`
---
#### **Task: Add 'Runway Impact Suggestions' to payment scheduling**
- **Status:** `Blocked`
- **Justification:** From build plan (line 141): "Show impact on runway... 'Paying now costs 4 days of runway...'"
- **Code Pointers:**
  - `domains/ap/services/payment.py`
  - `runway/core/runway_calculator.py`
- **Dependencies:**
  - `Implement 'Latest Safe Pay Date' calculation` (Needs the date to calculate the delta).
- **Definition of Done:**
  - A new service method is created that takes a bill and a proposed payment date and returns the runway impact in days.
  - The calculation accurately reflects the change in cash-out timing against the runway.
  - The logic is covered by unit tests.
- **Next Action:** Will become `Ready for Spec` after dependency is complete.
---
## Phase 2: Smart AR & Collections

#### **Task: Implement Overpayment Detection for Credit Memos**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 192): "Automatically suggest credit memos for overpayments." This is a core "Smart AR" feature.
- **Code Pointers:**
  - `domains/ar/services/payment_application.py`
  - `domains/ar/services/adjustment.py`
- **Dependencies:** None. Core services are in place.
- **Verification:** `payment_application.py` currently allocates payments but does not have explicit logic to handle overpayment scenarios.
- **Definition of Done:**
  - The payment application service can detect when a payment exceeds the linked invoice's balance.
  - When an overpayment is detected, it logs the event or prepares a potential credit memo using the `AdjustmentService`.
  - Unit tests cover overpayment and exact payment scenarios.
- **Next Action:** Ready for you to run `@spec "Implement Overpayment Detection for Credit Memos"`
---
#### **Task: Implement Collections Automation - 3-Stage Email Sequences**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 196): "Implement 3-stage email sequences (30d gentle, 45d urgent, 60d final)."
- **Code Pointers:**
  - `domains/ar/services/collections.py`
  - A new directory for templates: `templates/collections/` (Note: top-level `templates` dir)
  - `domains/core/services/email_service.py` (Assuming one will be created or exists)
- **Dependencies:** None.
- **Verification:** `collections.py` exists but is a skeleton. No email logic is present.
- **Definition of Done:**
  - Logic exists in `CollectionsService` to determine which email to send based on invoice age.
  - Three email templates (`gentle.html`, `urgent.html`, `final.html`) are created.
  - The service uses a mock email provider that logs to the console for testing.
  - Unit tests verify the correct template is chosen based on invoice age.
- **Next Action:** Ready for you to run `@spec "Implement Collections Automation - 3-Stage Email Sequences"`
---
#### **Task: Implement Collections Automation - Priority Scoring**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 202): "Priority scoring: amount, age, customer history."
- **Code Pointers:**
  - `domains/ar/services/collections.py`
  - `domains/ar/services/customer.py`
- **Dependencies:** None.
- **Verification:** `customer.py` contains a `get_payment_reliability` method stub, and `collections.py` is a skeleton. The scoring logic does not exist.
- **Definition of Done:**
  - A method in `CollectionsService` that takes a list of overdue invoices and returns them sorted by priority.
  - The scoring algorithm considers invoice age, amount, and the customer's payment reliability score.
  - Unit tests validate the sorting logic with different combinations of inputs.
- **Next Action:** Ready for you to run `@spec "Implement Collections Automation - Priority Scoring"`
---
#### **Task: Implement Collections Automation - Auto-pause on payment**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 208): "Auto-pause on payment detection."
- **Code Pointers:**
  - `domains/ar/services/collections.py`
  - `domains/ar/services/payment_matching.py`
  - `domains/integrations/qbo/service.py` (The refactored SmartSync)
- **Dependencies:** None.
- **Definition of Done:**
  - A mechanism (e.g., a status field on an Invoice or a separate tracking model) exists to manage the state of a collection sequence.
  - The QBO sync service can trigger a check before a reminder is sent.
  - If a payment has been received (verified via `PaymentMatchingService`), the collection sequence for that invoice is paused or updated.
  - Unit tests verify that a detected payment correctly pauses an active collection sequence.
- **Next Action:** Ready for you to run `@spec "Implement Collections Automation - Auto-pause on payment"`
---
## Phase 3: Smart Analytics & Insights

#### **Task: Fix P0 Critical - Implement Real Data in Tray Experience**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 295): "`runway/experiences/tray.py` returns empty lists instead of real data." This is a P0 blocker.
- **Code Pointers:**
  - `runway/experiences/tray.py`
  - `domains/ap/services/bill_ingestion.py`
  - `domains/ar/services/invoice.py`
- **Dependencies:** None.
- **Verification:** `runway/experiences/tray.py` currently returns a hardcoded empty list. It is not connected to any domain services.
- **Definition of Done:**
  - The `get_tray_items` (or equivalent) function in `runway/experiences/tray.py` is implemented.
  - It calls the appropriate `domains` services to fetch real bills and invoices.
  - It transforms the data from the domain models into the format expected by the tray.
  - The function is covered by integration tests that use mocked service calls.
- **Next Action:** Ready for you to run `@spec "Fix P0 Critical - Implement Real Data in Tray Experience"`
---
#### **Task: Fix P0 Critical - Implement Real QBO API Unit Tests**
- **Status:** `Ready for Spec`
- **Justification:** From build plan (line 314): "Need real QBO API unit tests to validate actual integration behavior."
- **Code Pointers:**
  - `tests/domains/integration/qbo/test_auth_real_api.py` (New file)
  - `tests/domains/integration/qbo/test_client_real_api.py` (New file)
  - `domains/integrations/qbo/auth.py`
  - `domains/integrations/qbo/client.py`
- **Dependencies:** A QBO Sandbox environment and credentials available for testing.
- **Definition of Done:**
  - New test files are created that use a specific marker (e.g., `@pytest.mark.qbo_real_api`).
  - Tests for the QBO auth service successfully perform a token refresh against the live sandbox.
  - Tests for the QBO client successfully fetch data (e.g., a list of customers) from the live sandbox.
  - These tests are excluded from the default `pytest` run.
- **Next Action:** Ready for you to run `@spec "Fix P0 Critical - Implement Real QBO API Unit Tests"`
---

## Phase 0: Foundation & QBO Integration

#### **Task: P0 Critical - Change QBO Mocking Default to False**
- **Status:** `Ready for Spec`
- **Justification:** From `MOCK_PROVIDER_AUDIT`: The entire system defaults to using mocked QBO data because of a misconfigured environment variable, preventing any real API testing. This is a P0 blocker.
- **Code Pointers:**
  - `domains/integrations/qbo/config.py`
- **Dependencies:** None.
- **Verification:** The `QBOConfig` class initializes with `os.getenv("USE_MOCK_QBO", "true")`.
- **Definition of Done:**
  - The default value for `USE_MOCK_QBO` is changed from `"true"` to `"false"`.
  - All integration tests are confirmed to run against the real QBO sandbox API after this change.
- **Next Action:** Ready for you to run `@spec "P0 Critical - Change QBO Mocking Default to False"`
---
#### **Task: P0 Critical - Remove Mock Provider Default from TrayService**
- **Status:** `Ready for Spec`
- **Justification:** From `MOCK_PROVIDER_AUDIT`: The `TrayService` silently falls back to a mock data provider, which can hide real integration bugs during development and testing.
- **Code Pointers:**
  - `runway/experiences/tray.py`
- **Dependencies:** None.
- **Verification:** The `get_tray_data_provider` function returns a `MockTrayDataProvider` by default.
- **Definition of Done:**
  - The `get_tray_data_provider` factory function is refactored to raise a `ValueError` if it cannot create a real `QBOTrayDataProvider`, instead of defaulting to a mock.
  - The `TrayService` constructor is updated to handle this change gracefully, requiring explicit provider configuration.
- **Next Action:** Ready for you to run `@spec "P0 Critical - Remove Mock Provider Default from TrayService"`
---
#### **Task: P0 Critical - Audit and Fix Integration Tests Using Mocks**
- **Status:** `Ready for Spec`
- **Justification:** From `MOCK_PROVIDER_AUDIT`: Integration tests are contaminated with mock fixtures (`qbo_integration_with_mock_data`), providing a false sense of security that we are testing against the real QBO API.
- **Code Pointers:**
  - `tests/conftest.py`
  - All files in `tests/integration/`
- **Dependencies:** `P0 Critical - Change QBO Mocking Default to False`.
- **Definition of Done:**
  - The `qbo_integration_with_mock_data` fixture is removed from any test that should be hitting the real API.
  - Tests requiring a live sandbox connection use a specific marker (e.g., `@pytest.mark.real_qbo`).
  - Tests marked as `real_qbo` are configured to fail if `USE_MOCK_QBO` is true.
- **Next Action:** Ready for you to run `@spec "P0 Critical - Audit and Fix Integration Tests Using Mocks"`
---
