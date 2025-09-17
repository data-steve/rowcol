 # Story of the Code: Oodaloo Architecture Guide

**A comprehensive guide to understanding Oodaloo's codebase, architecture, and development philosophy.**

---

## **🎯 What is Oodaloo?**

Oodaloo is a **cash runway management platform** for small businesses. Think of it as a "CFO-in-a-box" that connects to QuickBooks Online (QBO) and helps business owners understand:

- **How long their cash will last** (runway calculation)
- **What actions to take today** (Prep Tray with prioritized tasks)
- **Weekly financial health updates** (digest emails)

### **The Core Value Proposition**

**Problem**: Small business owners are flying blind financially - they know their bank balance but not their cash runway or what actions to prioritize.

**Solution**: Oodaloo becomes the "single pane of glass" for business finances, using QBO as the data source and providing actionable insights.

---

## **🏗️ Architecture Philosophy**

### **The Great Separation: `domains/` vs `runway/`**

Oodaloo's architecture is built around a key principle documented in **ADR-001**:

```
domains/     # QBO-facing primitives (what IS)
├── ap/      # Accounts Payable data and operations  
├── ar/      # Accounts Receivable data and operations
├── bank/    # Bank account and transaction data
└── core/    # Shared business entities (Business, User, Integration)

runway/      # Product orchestration (what SHOULD BE)
├── services/    # Business logic and workflows
├── routes/      # User-facing API endpoints  
├── tray/        # Prep Tray functionality
├── reserves/    # Runway Reserve management
├── jobs/        # Background job processing
└── middleware/  # Authentication, logging, CORS
```

### **Why This Separation Matters**

**`domains/`** contains **QBO-facing primitives**:
- Models that mirror QBO data structures
- Services that sync with QBO APIs
- Raw financial data operations
- **Think**: "This is what exists in QuickBooks"

**`runway/`** contains **product orchestration**:
- Business logic that creates value from domain data
- User-facing features and workflows  
- Oodaloo-specific concepts (Prep Tray, Runway Reserves)
- **Think**: "This is what Oodaloo does with that data"

### **Example of the Separation**

```python
# domains/ap/models/bill.py - Raw QBO data
class Bill(Base):
    qbo_bill_id = Column(String)  # From QBO
    vendor_name = Column(String)  # From QBO
    amount = Column(Numeric)      # From QBO
    due_date = Column(Date)       # From QBO

# runway/tray/models/tray_item.py - Oodaloo value-add
class TrayItem(Base):
    source_bill_id = Column(String, ForeignKey("bills.bill_id"))
    priority_score = Column(Integer)    # Oodaloo calculation
    runway_impact = Column(JSON)        # Oodaloo analysis
    recommended_action = Column(String) # Oodaloo intelligence
```

---

## **🧩 Key Components Explained**

### **1. FastAPI Application (`main.py`)**

The heart of the application - sets up routes, middleware, and database.

```python
# What it does:
- Initializes FastAPI app with CORS, authentication, logging
- Registers all API routes (auth, businesses, tray, digest)
- Sets up database connection and creates tables on startup
- Configures middleware stack for production readiness
```

**Key files**: `main.py`, `runway/middleware/`

### **2. Database Layer (`db/`)**

Centralized database management with SQLAlchemy.

```python
# What it does:
- Provides database session management
- Transaction context managers for atomic operations  
- Base models and tenant-aware mixins
- Migration support (future Alembic integration)
```

**Key files**: `db/base.py`, `db/session.py`, `db/transaction.py`

**Important**: All models inherit from `TenantMixin` to ensure business-level data isolation.

### **3. Domain Models (`domains/*/models/`)**

The foundation - represents real-world financial entities.

#### **Core Domain (`domains/core/`)**
- **`Business`**: The main tenant entity (maps to QBO Company)
- **`User`**: Business owners and staff members
- **`Integration`**: QBO connection details and OAuth tokens

#### **AP Domain (`domains/ap/`)**  
- **`Bill`**: Vendor bills from QBO
- **`Payment`**: Bill payments and schedules

#### **AR Domain (`domains/ar/`)**
- **`Invoice`**: Customer invoices from QBO  
- **`CreditMemo`**: Credit memos and adjustments

#### **Bank Domain (`domains/bank/`)**
- **`BankAccount`**: Bank accounts from QBO
- **`Transaction`**: Bank transactions and categorization

### **4. Runway Services (`runway/services/`)**

The business logic layer - where Oodaloo's intelligence lives.

#### **DigestService** (`runway/services/digest.py`)
```python
# What it does:
- Calculates cash runway based on bank balance and burn rate
- Generates weekly digest emails with financial insights
- Manages email delivery with provider fallback
- Tracks engagement and delivery metrics
```

#### **OnboardingService** (`runway/services/onboarding.py`)  
```python
# What it does:
- Handles new business registration and setup
- Manages QBO OAuth connection flow
- Creates initial business configuration
- Sets up default settings and preferences
```

### **5. Prep Tray System (`runway/tray/`)**

Oodaloo's signature feature - actionable financial tasks.

#### **TrayService** (`runway/tray/services/tray.py`)
```python
# What it does:
- Analyzes financial data to identify action items
- Calculates priority scores based on urgency and impact
- Provides runway impact analysis for each action
- Generates QBO deep-links for one-click actions
```

#### **TrayItem Model** (`runway/tray/models/tray_item.py`)
```python
# What it represents:
- Actionable tasks derived from financial data
- Priority scoring (1-100, with 80+ being urgent)
- Runway impact analysis (cash and days impact)
- Status tracking (pending, in_progress, completed)
```

**Tray Item Types**:
- `overdue_bill` - Bills past due date
- `large_payment` - Significant outgoing payments
- `overdue_invoice` - Unpaid customer invoices
- `low_balance` - Bank account balance warnings
- `upcoming_payment` - Bills due soon

### **6. Runway Reserves (`runway/reserves/`)**

Oodaloo's cash earmarking system (not a QBO feature).

#### **RunwayReserve Model** (`runway/reserves/models/runway_reserve.py`)
```python
# What it represents:
- Cash earmarked for specific purposes (tax, payroll, emergency)
- Target amounts and current allocation status
- Transaction history for reserve funding
- Business rules for reserve recommendations
```

**Reserve Types**:
- `TAX` - Tax obligation reserves
- `PAYROLL` - Payroll funding reserves  
- `OPERATING_EXPENSES` - Operating expense buffers
- `EMERGENCY` - Emergency fund reserves
- `DEBT_SERVICE` - Loan payment reserves

### **7. Background Jobs (`runway/jobs/`)**

Asynchronous task processing for digest emails and data sync.

#### **JobRunner** (`runway/jobs/job_runner.py`)
```python
# What it does:
- Schedules and executes background tasks
- Provides retry logic and error handling
- Supports both in-memory (dev) and Redis (prod) storage
- Handles job idempotency and status tracking
```

#### **Digest Jobs** (`runway/jobs/digest_jobs.py`)
```python
# What it does:  
- Schedules weekly digest emails for all businesses
- Manages job scheduling with configurable timing
- Handles business-specific digest preferences
```

### **8. Provider Pattern (Mock-First Development)**

A key architectural pattern throughout Oodaloo - documented in **ADR-002**.

#### **The Pattern**
```python
# Abstract base class
class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, message: EmailMessage) -> EmailResult:
        pass

# Mock implementation (development)
class MockEmailProvider(EmailProvider):
    def send_email(self, message: EmailMessage) -> EmailResult:
        return EmailResult(status="sent", message_id="mock_123")

# Real implementation (production)  
class SendGridProvider(EmailProvider):
    def send_email(self, message: EmailMessage) -> EmailResult:
        # Real SendGrid API call
        pass
```

#### **Provider Examples in Codebase**:
- **Email**: `MockEmailProvider`, `SendGridProvider`, `SESProvider`
- **QBO Data**: `MockDataProvider`, `QBODataProvider`
- **Tray Data**: `MockTrayDataProvider`, `ProductionTrayDataProvider`
- **Hash**: `MockHashProvider`, `SHA256HashProvider`
- **Jobs**: `InMemoryJobStorageProvider`, `RedisJobStorageProvider`

### **9. API Routes (`runway/routes/`)**

User-facing REST API endpoints.

#### **Authentication Routes** (`runway/routes/auth.py`)
- `POST /runway/auth/login` - User login with JWT
- `POST /runway/auth/register` - New user registration
- `POST /runway/auth/refresh` - Token refresh
- `POST /runway/auth/password-reset` - Password reset flow

#### **Tray Routes** (`runway/routes/tray.py`)
- `GET /runway/tray/items` - Get prioritized action items
- `GET /runway/tray/summary` - Tray overview and stats
- `POST /runway/tray/items/{id}/confirm` - Mark item completed
- `GET /runway/tray/items/{id}/actions` - Get available actions

#### **Digest Routes** (`runway/routes/digest.py`)
- `POST /runway/digest/generate` - Trigger digest generation
- `POST /runway/digest/send-all` - Send to all businesses
- `GET /runway/digest/preview` - Preview digest content

---

## **🔧 Development Patterns**

### **1. Mock-First Development**

Every external dependency has a mock provider for development:

```python
# Environment-based provider selection
def get_email_provider() -> EmailProvider:
    if os.getenv("USE_MOCK_EMAIL") == "true":
        return MockEmailProvider()
    elif os.getenv("SENDGRID_API_KEY"):
        return SendGridProvider()
    else:
        return SESProvider()
```

**Benefits**:
- Fast development without external dependencies
- Predictable test data and behavior
- Easy switching between mock and real providers
- Cost control (no accidental API charges)

### **2. Tenant-Aware Architecture**

Every piece of data belongs to a business (tenant):

```python
# All models include business_id
class TrayItem(TenantMixin, Base):
    business_id = Column(String(36), ForeignKey("businesses.business_id"))

# All services filter by business
class TrayService:
    def __init__(self, db: Session, business_id: str):
        self.business_id = business_id
    
    def get_items(self):
        return self.db.query(TrayItem).filter(
            TrayItem.business_id == self.business_id
        ).all()

# All routes verify tenant access
@router.get("/tray/items")
async def get_items(business_id: str = Depends(get_current_business_id)):
    # business_id automatically verified against current user
```

### **3. Configuration-Driven Development**

No magic numbers or hardcoded values:

```python
# config/business_rules.py
class TrayPriorities:
    URGENT_THRESHOLD = 80
    HIGH_THRESHOLD = 60
    OVERDUE_PENALTY = 20

class DigestSettings:
    DEFAULT_BURN_RATE_MONTHLY = 10000.0
    EMAIL_RETRY_ATTEMPTS = 3
```

### **4. Clean Exception Handling**

Custom exceptions with proper context:

```python
# common/exceptions.py
class TrayItemNotFoundError(OodalooError):
    """Raised when a tray item cannot be found."""
    pass

# Usage in services
def get_tray_item(self, item_id: str) -> TrayItem:
    item = self.db.query(TrayItem).filter(
        TrayItem.id == item_id,
        TrayItem.business_id == self.business_id
    ).first()
    
    if not item:
        raise TrayItemNotFoundError(f"Tray item {item_id} not found")
    
    return item
```

### **5. Database Transaction Management**

Atomic operations with context managers:

```python
# db/transaction.py
@contextmanager
def db_transaction(db: Session):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# Usage in services
def create_business_with_user(self, business_data, user_data):
    with db_transaction(self.db):
        business = Business(**business_data)
        self.db.add(business)
        self.db.flush()  # Get ID without committing
        
        user_data["business_id"] = business.business_id
        user = User(**user_data)
        self.db.add(user)
        # Both saved together or both fail
```

---

## **📊 Data Flow Examples**

### **Weekly Digest Generation Flow**

1. **Trigger**: Background job runs weekly
2. **Data Collection**: `DigestService` queries business financial data
3. **Calculation**: Calculate runway based on bank balance and burn rate
4. **Email Generation**: Create HTML email with insights
5. **Delivery**: Send via email provider with fallback
6. **Tracking**: Log delivery status and engagement metrics

```python
# Simplified flow
def generate_weekly_digest(business_id: str):
    # 1. Get business data
    business = get_business(business_id)
    
    # 2. Calculate runway
    runway_data = calculate_runway(business_id)
    
    # 3. Generate email content  
    email_content = create_digest_email(business, runway_data)
    
    # 4. Send email
    result = email_service.send_digest(business.owner_email, email_content)
    
    # 5. Track delivery
    log_digest_delivery(business_id, result)
```

### **Prep Tray Item Creation Flow**

1. **Data Sync**: QBO data synced to local database
2. **Analysis**: `TrayService` analyzes data for action items
3. **Prioritization**: Calculate priority scores based on business rules
4. **Impact Analysis**: Calculate runway impact for each item
5. **Presentation**: API returns prioritized list to frontend

```python
# Simplified flow
def refresh_tray_items(business_id: str):
    # 1. Get recent financial data
    bills = get_overdue_bills(business_id)
    invoices = get_overdue_invoices(business_id)
    
    # 2. Create tray items
    items = []
    for bill in bills:
        priority = calculate_priority(bill)
        impact = calculate_runway_impact(bill)
        
        item = TrayItem(
            type="overdue_bill",
            priority_score=priority,
            runway_impact=impact,
            business_id=business_id
        )
        items.append(item)
    
    # 3. Save to database
    save_tray_items(items)
```

### **QBO Data Synchronization Flow**

1. **Authentication**: Verify QBO OAuth tokens
2. **API Calls**: Fetch data from QBO APIs
3. **Transformation**: Convert QBO data to Oodaloo models
4. **Storage**: Save to local database with tenant isolation
5. **Analysis**: Trigger tray and runway recalculations

```python
# Simplified flow  
def sync_qbo_data(business_id: str):
    # 1. Get QBO integration
    integration = get_qbo_integration(business_id)
    
    # 2. Fetch data from QBO
    qbo_data = qbo_client.fetch_transactions(integration.access_token)
    
    # 3. Transform and store
    with db_transaction(db):
        for txn_data in qbo_data:
            transaction = Transaction(
                business_id=business_id,
                qbo_txn_id=txn_data["id"],
                amount=txn_data["amount"],
                # ... other fields
            )
            db.add(transaction)
    
    # 4. Trigger analysis
    refresh_tray_items(business_id)
    recalculate_runway(business_id)
```

---

## **🧪 Testing Philosophy**

### **Phase-Focused Testing**

Tests are organized by development phase to avoid testing parked features:

```python
# pytest markers
@pytest.mark.phase0  # Current active features
@pytest.mark.parked  # Parked features (skipped by default)
@pytest.mark.qbo    # Requires real QBO sandbox
```

### **Mock-First Testing**

All external dependencies are mocked in unit tests:

```python
def test_digest_generation(mock_email_provider):
    digest_service = DigestService(
        db=test_db,
        email_provider=mock_email_provider  # Injected mock
    )
    
    result = digest_service.generate_digest("test_business")
    
    assert result["status"] == "success"
    assert mock_email_provider.send_email.called
```

### **Realistic Test Data**

Test scenarios mirror real business complexity:

```python
# tests/fixtures/business_scenarios.py
MARKETING_AGENCY_SCENARIO = {
    "monthly_revenue": 50000,
    "employee_count": 8,
    "recurring_bills": [
        {"vendor": "HubSpot", "amount": 1200, "frequency": "monthly"},
        {"vendor": "Slack", "amount": 96, "frequency": "monthly"}
    ],
    "outstanding_invoices": [
        {"client": "TechStart Inc", "amount": 8000, "overdue_days": 0},
        {"client": "Healthcare Practice", "amount": 15000, "overdue_days": 5}
    ]
}
```

---

## **🚀 Deployment Strategy**

### **Environment Progression**

**Development** → **Staging** → **Production**

```bash
# Development: All mocks enabled
USE_MOCK_EMAIL=true
USE_MOCK_QBO=true
DATABASE_URL=sqlite:///oodaloo.db

# Staging: Mixed real/mock services
USE_MOCK_EMAIL=false  # Real email for testing
USE_MOCK_QBO=true     # Keep QBO mocked for cost control
DATABASE_URL=postgresql://staging-db/oodaloo

# Production: All real services
USE_MOCK_EMAIL=false
USE_MOCK_QBO=false
DATABASE_URL=postgresql://prod-db/oodaloo
```

### **Container Strategy**

Docker containers with health checks and proper security:

```dockerfile
# Multi-stage build for production optimization
FROM python:3.11-slim as production

# Non-root user for security
RUN useradd --create-home --shell /bin/bash oodaloo
USER oodaloo

# Health check for load balancer
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
```

---

## **🔮 Future Architecture Considerations**

### **Phase 1: AP & Payments**
- Enhanced bill management and payment scheduling
- Integration with payment providers (Stripe, bank ACH)
- Vendor management and normalization

### **Phase 2: AR & Collections**  
- Invoice tracking and collections workflows
- Customer communication automation
- Cash flow forecasting improvements

### **Phase 3: RowCol Multi-Tenancy**
- CAS firm management of multiple businesses
- Role-based access control (RBAC)
- Cross-business reporting and analytics

### **Phase 4: Productionalization**
- Real QBO integration validation and optimization
- Production infrastructure (PostgreSQL, Redis, monitoring)
- CI/CD pipeline and deployment automation

---

## **🤔 Key Architectural Decisions**

### **Why SQLAlchemy over Django ORM?**
- More explicit control over database operations
- Better performance for financial data processing
- Cleaner separation of concerns with FastAPI

### **Why FastAPI over Django/Flask?**
- Native async support for better performance
- Automatic API documentation with OpenAPI
- Modern Python type hints and validation
- Lightweight and focused on API development

### **Why Mock-First Development?**
- Faster development cycles without external dependencies
- Cost control (no accidental API charges during development)
- Predictable test behavior and data
- Easy environment switching

### **Why Business-Level Tenancy?**
- Simpler initial implementation vs. database-per-tenant
- Natural alignment with QBO's company-centric model
- Clear data isolation boundaries
- Easy migration path to more complex tenancy models

---

## **📚 Key Documentation References**

- **[ADR-001](docs/architecture/ADR-001-domains-runway-separation.md)**: Domains vs Runway separation
- **[ADR-002](docs/architecture/ADR-002-mock-first-development.md)**: Mock-First Development Strategy  
- **[ADR-003](docs/architecture/ADR-003-multi-tenancy-strategy.md)**: Multi-Tenancy Strategy
- **[QBO Integration Guide](docs/integrations/qbo/README.md)**: Complete QBO setup and troubleshooting
- **[Testing Strategy](docs/testing/README.md)**: Phase-focused testing with mock patterns
- **[Deployment Guide](docs/deployment/README.md)**: Dev → Staging → Production deployment
- **[Build Plan v4.3](dev_plans/Oodaloo_v4.3_Build_Plan.md)**: Complete development roadmap

---

## **🎓 For New Developers**

### **Getting Started Checklist**
1. **Read this guide** to understand the architecture
2. **Review ADR-001** to understand domains/ vs runway/ separation
3. **Set up development environment** with mocked services
4. **Run the test suite** to understand testing patterns
5. **Make a small change** to understand the development workflow

### **Common Gotchas**
- **Always include `business_id`** in new models and queries
- **Use provider patterns** instead of hardcoded external dependencies  
- **Follow tenant isolation** - never query across businesses
- **Use configuration constants** instead of magic numbers
- **Implement proper exception handling** with custom exception classes

### **When You're Stuck**
1. Check if there's an existing provider pattern to follow
2. Look for similar functionality in other services
3. Review the test files to understand expected behavior
4. Check the ADRs for architectural guidance
5. Look at the build plan for context on future direction

---

**Remember**: Oodaloo is built to be **maintainable by junior/mid-level developers**. If something seems overly complex, it probably needs to be simplified. The architecture prioritizes **clarity, consistency, and changeability** over cleverness.

---

*Last Updated: 2025-09-17*  
*Next Review: After Phase 1 completion*
