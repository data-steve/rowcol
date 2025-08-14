# BookClose AP Automation

## Setup

1. **Install Dependencies**:
   ```bash
   poetry install
   poetry add intuit-oauth python-quickbooks pandas rapidfuzz
   ```

2. **Configure QBO**:
   - Set up a QBO sandbox app at [developer.intuit.com](https://developer.intuit.com).
   - Add to `.env`:
     ```
     QBO_CLIENT_ID=your_client_id
     QBO_CLIENT_SECRET=your_client_secret
     QBO_REDIRECT_URI=http://localhost:8000/callback
     QBO_ACCESS_TOKEN=your_access_token
     QBO_REFRESH_TOKEN=your_refresh_token
     QBO_REALM_ID=your_realm_id
     ```
   - Run OAuth script to obtain tokens (see `scripts/qbo_auth.py`).

3. **Run Migrations**:
   ```bash
   poetry run python create_tables.py
   ```

4. **Seed Data**:
   ```bash
   poetry run psql -d bookclose -f data/seed_data.sql
   ```

## AP Workflows

- **Bill Ingestion**: Upload bills via `/api/ingest/ap/bills/upload` (OCR mocked with PaddleOCR adapter).
- **Bill Review**: Use `bill_review.html` for three-pane review (list, details, actions).
- **Payment Scheduling**: Schedule payments via `/api/ingest/ap/payments` and approve in `payment_schedule.html`.
- **Statement Reconciliation**: Reconcile statements via `/api/ingest/ap/statements/reconcile` (mocked).
- **Vendor Management**: Sync and deduplicate vendors via `/api/ingest/ap/vendors/{id}`.

## Testing

Run tests:
```bash
poetry run pytest tests/
```

## Endpoints

- `/api/ingest/ap/bills`: Sync QBO bills.
- `/api/ingest/ap/bills/upload`: Ingest bills (OCR/CSV).
- `/api/ingest/ap/bills/{id}`: Get/update bills.
- `/api/ingest/ap/bills/categorize`: Categorize bills.
- `/api/ingest/ap/payments`: Schedule payments.
- `/api/ingest/ap/statements/reconcile`: Reconcile statements.
- `/api/ingest/ap/vendors/{id}`: Manage vendors.