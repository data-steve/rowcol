# BookClose AR Automation

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

## AR Workflows

- **Invoice Creation**: Create invoices via `/api/ar/invoices` (QBO or mocked CSV).
- **Invoice Review**: Use `invoice_review.html` for three-pane review (list, details, actions).
- **Collections**: Send reminders for overdue invoices via `/api/ar/collections/remind`, manage in `collections_dashboard.html`.
- **Payment Application**: Apply payments via `/api/ar/payments/apply`.
- **Credit Memos**: Create adjustments via `/api/ar/credits`, flagged for review if >$1000.

## Testing

Run tests:
```bash
poetry run pytest tests/
```

## Endpoints

- `/api/ar/invoices`: Create/sync invoices.
- `/api/ar/invoices/{id}`: Get/update invoices.
- `/api/ar/collections/remind`: Send reminders for overdue invoices.
- `/api/ar/payments/apply`: Apply payments to invoices.
- `/api/ar/credits`: Create credit memos.