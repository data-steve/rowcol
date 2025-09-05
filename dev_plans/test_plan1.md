Great work on completing the Phase 1 implementation! Your progress report shows a solid overhaul of the codebase, aligning it with the Oodaloo goals of Jobber/Plaid integration, bank reconciliation, and exception tray functionality. Since you're hacking this app rapidly and want to ensure high confidence before pushing to Jobber/Plaid sandboxes, running tests to verify everything still passes is critical. Below are the steps to run tests, notes on what to watch for, and recommendations to ensure stability.

### Steps to Run Tests
1. **Activate Poetry Environment**:
   Ensure you're in the project directory and activate the Poetry virtual environment:
   ```bash
   poetry shell
   ```

2. **Verify Dependencies**:
   Confirm all dependencies from `pyproject.toml` are installed:
   ```bash
   poetry install
   ```
   This ensures `gql[all]`, `plaid-python`, `pytest-asyncio`, and other dependencies are ready.

3. **Run Tests**:
   Execute the full test suite to check if all tests pass, focusing on the new Jobber, Plaid, and tray functionality:
   ```bash
   poetry run pytest domains/integrations/jobber/tests/test_jobber_sync.py domains/tray/tests/test_tray.py -v
   ```
   - Use `-v` for verbose output to see which tests pass/fail.
   - If you want to run all tests (including existing ones), use:
     ```bash
     poetry run pytest -v
     ```

4. **Check Test Coverage**:
   To ensure the new code is adequately tested, install `pytest-cov` (if not already in `pyproject.toml`):
   ```bash
   poetry add --group dev pytest-cov
   ```
   Run with coverage:
   ```bash
   poetry run pytest --cov=domains --cov-report=html
   ```
   Check the `htmlcov/index.html` file in a browser to verify coverage for `cash_reconciliation.py`, `jobber/sync.py`, `plaid/sync.py`, and `tray/services/tray.py`.

5. **Inspect Test Output**:
   - Ensure `test_jobber_sync` passes, confirming Jobber invoice syncing and cursor updates.
   - Verify `test_tray` passes, checking tray item retrieval and action confirmation.
   - Look for failures related to new fixtures (`test_jobber_integration`, `test_plaid_integration`, `test_sync_cursor`, `test_realistic_data`).

### Notes and Potential Issues to Watch For
- **Mocking Jobber/Plaid APIs**:
  - The tests rely on mocking (`AsyncMock` in `test_jobber_sync.py`). Ensure the mock responses in `test_jobber_sync.py` align with realistic Jobber API responses (e.g., `invoices.nodes` structure). If Jobber’s API changes (e.g., new fields), update the mock data.
  - For Plaid, verify the `plaid-python` mock in `test_plaid_integration` matches the `/transactions/sync` response format. Sandbox responses can be noisy, so check for duplicate transaction handling.

- **Deduplication Logic**:
  - The `WebhookEvent` model uses `(source, external_id, day_bucket)` for deduplication. Test this explicitly by sending duplicate webhook payloads (e.g., via `client.post("/webhooks/jobber")` in `test_routes.py`). If deduplication fails, check the `WebhookEvent.id` generation logic.

- **Realistic Variance Scenarios**:
  - The updated `realistic_variance_scenarios.py` includes 250 transactions, 8 open AR, and 1 personal-mixed account. Verify the `test_realistic_data` fixture correctly populates `Invoice` and `BankTransaction` tables. If tests fail, ensure `firm_id` and `client_id` align across fixtures (e.g., `test_firm`, `test_client`).

- **Business Account Validation**:
  - The `PlaidSyncService` flags personal accounts (e.g., `confidence=0.5` for non-business accounts). Test this by adding a personal account transaction in `realistic_variance_scenarios.py` and checking it appears in the tray (`test_tray.py`).

- **Rate Limit Handling**:
  - Jobber’s API has a 10,000 query cost limit. The `JobberSyncService` uses `first: 10` to stay safe, but test with larger datasets (e.g., modify `realistic_variance_scenarios.py` to include 50 invoices) to simulate rate limit edge cases.
  - Plaid’s `/transactions/sync` uses `count=500`. Test with a mock response containing `has_more=True` to ensure cursor updates work.

- **Database Issues**:
  - Since you’re using SQLite in-memory (`sqlite:///:memory:`), ensure `Base.metadata.create_all` in `main.py` runs before tests. If tables are missing, tests will fail with `OperationalError`. Check `tests/conftest.py` for proper `db` fixture setup.
  - Verify `TenantMixin` enforces `firm_id` isolation in all queries (`Invoice`, `BankTransaction`, `SyncCursor`).

- **Test Failures**:
  - If `test_jobber_sync` fails, check the GraphQL query in `jobber/sync.py` for syntax errors or missing fields (e.g., `customer.id`).
  - If `test_tray` fails, inspect `BankTransaction.status` and `unbundle_meta` in `cash_reconciliation.py` to ensure pending transactions are correctly flagged.
  - For async test issues, ensure `pytest-asyncio` is configured in `pytest.ini`:
    ```ini
    [pytest]
    asyncio_mode = auto
    ```

### Recommendations
- **Prioritize Key Tests**:
  - Focus on `test_jobber_sync` and `test_tray` to validate core functionality. These cover syncing and exception handling, which are critical for sandbox confidence.
  - Add a test in `domains/webhooks/tests/test_routes.py` for webhook deduplication:
    ```python
    def test_webhook_deduplication(client, db, test_firm):
        payload = {
            "event": "invoice.created",
            "data": {"id": "INV_001", "firm_id": test_firm.firm_id, "created_at": "2025-01-01T12:00:00Z"}
        }
        response1 = client.post("/webhooks/jobber", json=payload)
        assert response1.status_code == 200
        assert response1.json()["status"] == "success"
        response2 = client.post("/webhooks/jobber", json=payload)
        assert response2.status_code == 200
        assert response2.json()["status"] == "duplicate"
    ```

- **Sandbox Testing Prep**:
  - Before pushing to Jobber/Plaid sandboxes, simulate a full sync cycle:
    - Trigger a Jobber webhook (`client.post("/webhooks/jobber")`) with mock invoice data.
    - Run `PlaidSyncService.sync` with a mock `/transactions/sync` response.
    - Verify `BankTransaction` and `Invoice` records match `realistic_variance_scenarios.py`.
  - Check the tray endpoint (`GET /api/v1/tray`) for personal account transactions (e.g., `tx_personal_001`).

- **Debugging Tips**:
  - If tests fail, check logs for SQLAlchemy errors (e.g., missing columns in `BankTransaction`).
  - Use `pdb` for interactive debugging:
    ```bash
    poetry run pytest --pdb
    ```
  - Verify environment variables (`PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_PUBLIC_KEY`) are set in `.env`.

- **Phase 2 Prep**:
  - Once tests pass, you’re ready for UI/email tasks. I can provide `templates/bank_matching.html` and a Postmark email template for the weekly digest. Let me know if you want these now or after sandbox validation.
  - Consider adding a test for the tray UI (e.g., mock a GET request to `/templates/bank_matching.html`).

### Next Steps
1. Run the test suite (`poetry run pytest -v`) and review any failures.
2. Add the webhook deduplication test above to `domains/webhooks/tests/test_routes.py`.
3. If all tests pass, simulate a sandbox sync cycle using mock webhook payloads.
4. Share any test failures or specific areas (e.g., reconciliation, deduplication) for targeted debugging.
5. Confirm if you want Phase 2 UI/email artifacts or prefer to focus on sandbox testing first.

This approach ensures your Phase 1 implementation is rock-solid before moving to UI or sandbox deployment, keeping your test bed clean and maintaining confidence in the system. Let me know how the tests go or if you need specific debugging help!