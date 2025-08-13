# BookClose

## Setup
1. Install dependencies: `poetry install`
2. Run migrations: `poetry run python -m database`
3. Seed database: `poetry run python -m main`
4. Start server: `poetry run uvicorn main:app --reload`
5. Access UI: `http://localhost:8000/templates/rule_editor.html`

## Features
- **Rules**: Manage categorization rules via `/api/automation/rules`.
- **Vendor Normalization**: Normalize vendors via `/api/automation/vendors/normalize`.
- **QBO Sync**: Sync QBO data via `/api/ingest/qbo`.
- **CSV Ingestion**: Upload/validate CSVs via `/api/csv/upload`, `/api/csv/validate`.
- **Document Management**: Upload/categorize documents via `/api/documents/upload`, `/api/documents/{id}`.
- **Review Queue**: Manage OCR/tagging reviews via `/api/review/documents`.
- **Tasks**: Assign/track tasks via `/api/tasks`.

## Testing
Run `poetry run pytest tests/` to execute unit and integration tests. Mock QBO/OCR used for now.

## KPIs
- % transactions with canonical vendor
- % auto-posted (confidence ≥0.9)
- Override rate, false-merge rate (<1%)
- Document processing time, CSV error rate
- OCR review completion time, task completion rate