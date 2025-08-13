# BookClose

A cloud-native bookkeeping platform for mid-size firms, supporting account reconciliation, payroll, and financial reporting with automation and Fulcrum-style UX.

## Phase 1, Stage 0: Engagements, Services, and Tasks

### Setup
1. **Install dependencies**:
   ```bash
   pip install fastapi sqlalchemy pydantic pytest jinja2 uvicorn pdfkit
   ```
2. **Install wkhtmltopdf (for PDF generation)**:
   - Download the macOS package:
     ```bash
     curl -L https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-2/wkhtmltox-0.12.6-2.macos-cocoa.pkg -O
     ```
   - Install to `/usr/local/bin`:
     ```bash
     sudo installer -pkg wkhtmltox-0.12.6-2.macos-cocoa.pkg -target /usr/local/bin
     ```
   - Verify: `wkhtmltopdf --version`.
3. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```
   - Automatically creates SQLite tables (`bookclose.db`) and seeds data if empty.
4. **Access UI**:
   - Engagements: `http://localhost:8000/templates/engagements.html`
   - Services: `http://localhost:8000/templates/services.html`
   - Engagement Letter: `http://localhost:8000/templates/engagement_letter.html`
   - Access UI: `http://localhost:8000/templates/rule_editor.html`
5. **Run tests**:
   ```bash
   pytest tests/
   ```
   - Uses in-memory SQLite, automatically creates tables, and seeds data via `conftest.py`.

### Features
- **Dynamic Service Bundling**: Tiered services (basic/pro/enterprise) with automation scores and task sequences.
- **Engagement Management**: E-signatures, QBO sync with retries, and compliance validation.
- **Task Orchestration**: Drag-and-drop tasks with blockers, priority scores, and automation eligibility for PBC and workflow management.
- **Engagement Letter**: PDF/HTML with interactive signatures and compliance clauses.
- **Fulcrum-Style UI**: Left nav, KPI bar (overdue, compliance, automation), breadcrumb chain, WebSocket updates, and Joyride tours.
- **Self-Healing**: QBO sync retries and compliance validation.
- **Scalability**: In-memory cache for dev; Redis prep for production.
- **Rules**: Manage categorization rules via `/api/automation/rules`.
- **Vendor Normalization**: Normalize vendors via `/api/automation/vendors/normalize`.
- **QBO Sync**: Sync QBO data via `/api/ingest/qbo`.
- **CSV Ingestion**: Upload/validate CSVs via `/api/csv/upload`, `/api/csv/validate`.
- **Document Management**: Upload/categorize documents via `/api/documents/upload`, `/api/documents/{id}`.
- **Review Queue**: Manage OCR/tagging reviews via `/api/review/documents`.
- **Tasks**: Assign/track tasks via `/api/tasks`.

## Testing
Run `pytest tests/` to execute unit and integration tests. Mock QBO/OCR used for now.

## KPIs
- % transactions with canonical vendor
- % auto-posted (confidence ≥0.9)
- Override rate, false-merge rate (<1%)
- Document processing time, CSV error rate

### Endpoints
- **GET/POST /api/engagements**: Create/list engagements.
- **PATCH /api/engagements/{id}**: Update status.
- **GET /api/engagements/{id}/letter**: Get letter (PDF/HTML).
- **POST /api/engagements/{id}/sign**: Submit e-signature.
- **POST /api/engagements/{id}/qbo-sync**: Trigger QBO sync.
- **GET/POST /api/services**: Create/list services, filter by `tier` or `preview`.
- **GET /api/services/{id}/preview**: View task/compliance details.
- **PATCH /api/tasks/{id}/assign**: Assign tasks.

### Dependencies
- Assumes `Entity`, `User` models (Phase 1, Stage 2).
- Uses `database.py` (SQLite for dev, in-memory for tests).
- Uses `wkhtmltopdf` for PDF generation.

### Database Management
- **Development**: `main.py` runs migrations (`Base.metadata.create_all`) and seeds `bookclose.db` if empty on startup.
- **Testing**: `conftest.py` uses in-memory SQLite, creates tables, and seeds data per test function.
- **Models**: Defined in `models/` with `TimestampMixin` for `created_at`/`updated_at`. Imported via `models/__init__.py` for unified migrations.
- **Seed Data**: `data/seed_data.sql` populates initial services, engagements, and tasks.
- **Future**: Transition to PostgreSQL with Alembic migrations in Phase 2 for production.

### Testing
- Unit tests: E-signatures, QBO sync, compliance validation, task prioritization.
- Integration tests: All endpoints, including `/sign`, `/qbo-sync`, `/assign`.
- Database setup: Handled by `conftest.py` with in-memory SQLite.

### Deployment
- Azure App Service with GitHub Actions CI/CD.
- PostgreSQL sharding prep for