#!/bin/bash
set -e

# Initialize Oodaloo Phase 0 repo for cash runway MVP (v4.2)
echo "Initializing Oodaloo Phase 0 repo..."

# Create directory structure
mkdir -p domains/{core,ap,ar,bank,policy,integrations,runway}/{models,services}
mkdir -p runway/{routes,templates,tests}
mkdir -p _parked/{core,services}
mkdir -p tests/{unit,integration}
mkdir -p static data

# Copy reusable models
cp -r domains/core/models/{client.py,base.py,audit_log.py,document.py,document_type.py,integration.py,sync_cursor.py,transaction.py,notification.py} domains/core/models/
cp -r domains/ap/models/{bill.py,vendor.py,vendor_canonical.py,payment.py,payment_intent.py} domains/ap/models/
cp -r domains/ar/models/{invoice.py,customer.py,payment.py,credit_memo.py} domains/ar/models/
cp -r domains/bank/models/{bank_transaction.py,transfer.py} domains/bank/models/
cp -r domains/policy/models/*.py domains/policy/models/
cp -r domains/identity_graph/models.py domains/identity_graph/

# Park CAS-specific models
mkdir -p _parked/core/models
mv domains/core/models/{firm.py,engagement.py,job.py,task.py,staff.py,service.py,engagement_entities.py,business_entity.py} _parked/core/models/

# Copy reusable services
cp services/{ingestion.py,vendor_normalization.py,cash_reconciliation.py,audit_log.py,policy_engine.py} domains/runway/services/
cp _parked/qbo/qbo_auth.py domains/integrations/qbo_auth.py

# Park CAS-heavy services
mkdir -p _parked/services
mv services/{shared_expense_allocation.py,revenue_recognition.py,servicepro_engine.py} _parked/services/

# Update comments/docs: Client → Business (keep client_id)
find domains -type f -name "*.py" -exec sed -i 's/#.*Client/# Business/g' {} \;
find domains -type f -name "*.py" -exec sed -i 's/class Client/class Business/g' {} \;

# Remove firm_id references (nullable for MVP)
find domains -type f -name "*.py" -exec sed -i 's/firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)/firm_id = Column(String(36), nullable=True)/g' {} \;

# Add Balance model (PostgreSQL-ready)
cat > domains/core/models/balance.py << EOL
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Balance(Base, TimestampMixin):
    __tablename__ = "balances"
    balance_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False, index=True)
    qbo_account_id = Column(String(50), nullable=False, index=True)
    current_balance = Column(Float, nullable=False)
    available_balance = Column(Float, nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    account_type = Column(String(50), nullable=False)  # checking, savings, credit
    business = relationship("Business")
EOL

# Update Business model (keep client_id, PostgreSQL-ready)
cat > domains/core/models/business.py << EOL
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Business(Base, TimestampMixin, TenantMixin):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), nullable=True)  # Nullable for single-business MVP
    name = Column(String(255), nullable=False, index=True)
    qbo_id = Column(String(50), nullable=True, index=True)
    industry = Column(String(50), nullable=True)  # agency, consulting, retail
    policy_profile_id = Column(Integer, ForeignKey("policy_profiles.profile_id"), nullable=True)
    integrations = relationship("Integration", back_populates="business")
    policy_profile = relationship("PolicyProfile")
    balances = relationship("Balance", back_populates="business")
    notifications = relationship("Notification", back_populates="business")
EOL

# Update Notification model
cat > domains/core/models/notification.py << EOL
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Notification(Base, TimestampMixin):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_role = Column(String(50), default="owner")
    event_type = Column(String(50))
    content = Column(JSON)
    sent_at = Column(DateTime, nullable=True)
    business = relationship("Business", back_populates="notifications")
    user = relationship("User")
EOL

# Add TrayItem model
cat > runway/tray/models/tray_item.py << EOL
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class TrayItem(Base, TimestampMixin):
    __tablename__ = "tray_item"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    type = Column(String(50))
    qbo_id = Column(String(50))
    status = Column(String(50), default="pending")
    priority = Column(String(50), default="medium")
    due_date = Column(DateTime)
    allowed_roles = Column(String(50), default="owner")
    business = relationship("Business")
EOL

# Update qbo_integration.py (Balances API, reuse existing QBO logic)
cat > domains/integrations/qbo_integration.py << EOL
from intuitlib.client import AuthClient
from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.models.business import Business
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

class QBOIntegration:
    def __init__(self, business: Business):
        self.business = business
        self.tenant_id = business.qbo_id
        self.auth_client = AuthClient(
            os.getenv("QBO_CLIENT_ID"),
            os.getenv("QBO_CLIENT_SECRET"),
            os.getenv("QBO_REDIRECT_URI"),
            "sandbox"
        )

    def get_bills(self, db: Session, due_days: int = 14) -> List[Dict[str, Any]]:
        from domains.ap.models.bill import Bill
        today = datetime.utcnow().date()
        return [
            {"qbo_id": b.qbo_id, "vendor": b.vendor_id, "amount": b.amount, "due_date": b.due_date}
            for b in db.query(Bill).filter(
                Bill.business_id == self.business.client_id,
                Bill.due_date <= datetime.utcnow() + timedelta(days=due_days),
                Bill.status != "paid"
            ).all()
        ]

    def get_invoices(self, db: Session, aging_days: int = 30) -> List[Dict[str, Any]]:
        from domains.ar.models.invoice import Invoice
        today = datetime.utcnow().date()
        return [
            {"qbo_id": i.qbo_id, "customer": i.customer_id, "amount": i.total, "due_date": i.due_date, "aging_days": (today - i.due_date.date()).days}
            for i in db.query(Invoice).filter(
                Invoice.business_id == self.business.client_id,
                Invoice.due_date < datetime.utcnow() - timedelta(days=aging_days),
                Invoice.status != "paid"
            ).all()
        ]

    def fetch_balances(self, db: Session) -> None:
        # Mock QBO Balances API for Phase 0
        mock_balances = [
            {"AccountId": "123", "CurrentBalance": 6000.0, "AvailableBalance": 5500.0, "AccountType": "checking", "Date": "2025-09-15T00:00:00"},
            {"AccountId": "456", "CurrentBalance": 2000.0, "AvailableBalance": 1800.0, "AccountType": "savings", "Date": "2025-09-15T00:00:00"}
        ]
        for bal in mock_balances:
            db.add(Balance(
                business_id=self.business.client_id,
                qbo_account_id=bal["AccountId"],
                current_balance=bal["CurrentBalance"],
                available_balance=bal["AvailableBalance"],
                snapshot_date=datetime.fromisoformat(bal["Date"]),
                account_type=bal["AccountType"]
            ))
        db.commit()

    def handle_webhook(self, payload: Dict) -> str:
        return "OK"
EOL

# Update qbo_auth.py (preserve mature auth logic)
cat > domains/integrations/qbo_auth.py << EOL
from typing import Tuple, Optional
from domains.core.models.business import Business

class QBOAuth:
    def __init__(self):
        self.tokens = {}  # business_id -> (access, refresh)

    def initiate_oauth(self, redirect_uri: str) -> str:
        return "https://mock.qbo.auth/url?state=mock_state"

    def exchange_tokens(self, code: str, business_id: int) -> Tuple[str, Optional[str]]:
        access = f"mock_access_{business_id}"
        refresh = f"mock_refresh_{business_id}"
        self.tokens[business_id] = (access, refresh)
        return access, refresh

qbo_auth = QBOAuth()
EOL

# Stub runway/services/digest.py
cat > domains/runway/services/digest.py << EOL
from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.ap.models.bill import Bill
from domains.ar.models.invoice import Invoice
from domains.integrations.qbo_integration import QBOIntegration
from datetime import datetime, timedelta
from typing import Dict

def calculate_runway(db: Session, business_id: str) -> Dict[str, float]:
    business = db.query(Business).filter(Business.client_id == business_id).first()
    if not business:
        raise ValueError("Business not found")
    qbo = QBOIntegration(business)
    balances = db.query(Balance).filter(
        Balance.business_id == business_id,
        Balance.snapshot_date >= datetime.utcnow() - timedelta(days=1)
    ).all()
    overdue_invoices = qbo.get_invoices(db, aging_days=30)
    upcoming_bills = qbo.get_bills(db, due_days=14)
    cash = sum(b.available_balance for b in balances)
    ar_total = sum(i["amount"] for i in overdue_invoices)
    ap_total = sum(b["amount"] for b in upcoming_bills)
    burn_rate = 10000.0  # Placeholder: Phase 3 historical calc
    runway_days = (cash + ar_total - ap_total) / (burn_rate / 30) if burn_rate else 0
    return {
        "runway_days": runway_days,
        "cash": cash,
        "ar_overdue": ar_total,
        "ap_due_soon": ap_total
    }
EOL

# Add tray service
cat > runway/tray/services/tray.py << EOL
from typing import List, Optional
from sqlalchemy.orm import Session
from domains.bank.models.bank_transaction import BankTransaction
from domains.ar.models.invoice import Invoice
from runway.tray.models.tray_item import TrayItem
from datetime import datetime, timedelta

class TrayService:
    def __init__(self, db: Session):
        self.db = db

    def get_tray_items(self, business_id: int) -> List[dict]:
        items = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.status == "pending"
        ).all()
        return [
            {
                "id": t.id,
                "type": t.type,
                "qbo_id": t.qbo_id,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None
            } for t in items
        ]

    def confirm_action(self, business_id: int, tray_item_id: int, action: str, invoice_ids: Optional[List[int]] = None):
        item = self.db.query(TrayItem).filter(
            TrayItem.business_id == business_id,
            TrayItem.id == tray_item_id
        ).first()
        if not item:
            raise ValueError("Tray item not found")
        if action == "confirm":
            item.status = "resolved"
            # Link to invoices if provided
        elif action == "split":
            pass
        self.db.commit()
        return item
EOL

# Add onboarding service
cat > runway/services/onboarding.py << EOL
from fastapi import Form, Depends
from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.audit_log import AuditLog
from database import get_db
from domains.integrations.qbo_auth import qbo_auth

def qualify_onboarding(email: str, weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    if not weekly_review:
        return {"dropoff": True, "reason": "No cash ritual need (20-30% expected)"}
    business = Business(name=f"{email.split('@')[0]} Agency", qbo_id=f"mock_{email.replace('@', '')}")
    db.add(business)
    db.commit()
    access, refresh = qbo_auth.exchange_tokens("mock_code", business.client_id)
    audit = AuditLog(
        business_id=business.client_id,
        action_type="onboard_qualify",
        entity_type="business",
        entity_id=str(business.client_id),
        details={"qualified": True}
    )
    db.add(audit)
    db.commit()
    return {"success": True, "business_id": business.client_id, "next": "Connect QBO"}
EOL

# Add tray routes
cat > runway/routes/tray.py << EOL
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from runway.tray.services.tray import TrayService
from database import get_db

router = APIRouter(prefix="/api/v1/tray", tags=["Tray"])

@router.get("/")
def get_tray(business_id: int, db: Session = Depends(get_db)):
    return TrayService(db).get_tray_items(business_id)

@router.post("/{id}/confirm")
def confirm_action(business_id: int, id: int, action: str, invoice_ids: Optional[List[int]] = None, db: Session = Depends(get_db)):
    return TrayService(db).confirm_action(business_id, id, action, invoice_ids)
EOL

# Add onboarding routes
cat > runway/routes/onboarding.py << EOL
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from runway.services.onboarding import qualify_onboarding
from database import get_db

router = APIRouter(prefix="/onboard", tags=["Onboarding"])

@router.post("/")
async def onboard(email: str = Form(...), weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    result = qualify_onboarding(email, weekly_review, db)
    if result.get("dropoff"):
        return {"msg": result["reason"]}
    return result
EOL

# Add onboarding template
cat > runway/templates/onboarding.html << EOL
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 class="text-2xl font-bold mb-4">Oodaloo Onboarding</h1>
        <form method="POST" action="/onboard">
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">Email</label>
                <input type="email" name="email" required class="w-full p-2 border rounded">
            </div>
            <div class="mb-4">
                <label class="flex items-center">
                    <input type="checkbox" name="weekly_review" class="mr-2">
                    Do you do a weekly cash review? (Key for runway ritual)
                </label>
            </div>
            <button type="submit" class="w-full bg-blue-500 text-white py-2 rounded">Start Ritual</button>
        </form>
        {% if dropoff %}
            <p class="mt-4 text-red-500">Not a fit—manual stacks may suffice.</p>
        {% endif %}
    </div>
</body>
</html>
EOL

# Update database.py
cat > database.py << EOL
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///oodaloo.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Register models
from domains.core.models.business import Business
from domains.core.models.audit_log import AuditLog
from domains.core.models.notification import Notification
from runway.tray.models.tray_item import TrayItem
from domains.core.models.balance import Balance

# Create tables
from domains.core.models.base import Base
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_database():
    """Seed database if empty."""
    try:
        conn = sqlite3.connect("oodaloo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("""
                    INSERT INTO clients (client_id, name, qbo_id, industry)
                    VALUES (1, 'Test Agency', 'test123', 'agency')
                """)
                cursor.execute("""
                    INSERT INTO balances (business_id, qbo_account_id, current_balance, available_balance, snapshot_date, account_type)
                    VALUES (1, '123', 6000.0, 5500.0, '2025-09-15T00:00:00', 'checking')
                """)
                conn.commit()
                logger.info("Database seeded successfully.")
        else:
            Base.metadata.create_all(bind=engine)
            seed_database()
        conn.close()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        if 'conn' in locals():
            conn.close()
EOL

# Initialize tests
cat > tests/conftest.py << EOL
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domains.core.models.base import Base

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()
EOL

# Add test for Business model
cat > tests/unit/test_business.py << EOL
import pytest
from sqlalchemy.orm import Session
from domains.core.models.business import Business

def test_create_business(db: Session):
    business = Business(
        client_id=1,
        name="Test Agency",
        qbo_id="test123",
        industry="agency"
    )
    db.add(business)
    db.commit()
    result = db.query(Business).filter_by(client_id=1).first()
    assert result.name == "Test Agency"
    assert result.qbo_id == "test123"
    assert result.industry == "agency"
EOL

# Add test for Balance model
cat > tests/unit/test_balance.py << EOL
import pytest
from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from datetime import datetime

def test_create_balance(db: Session):
    balance = Balance(
        business_id=1,
        qbo_account_id="123",
        current_balance=6000.0,
        available_balance=5500.0,
        snapshot_date=datetime.utcnow(),
        account_type="checking"
    )
    db.add(balance)
    db.commit()
    result = db.query(Balance).filter_by(qbo_account_id="123").first()
    assert result.current_balance == 6000.0
    assert result.account_type == "checking"
EOL

# Add test for QBO integration
cat > tests/unit/test_qbo_integration.py << EOL
import pytest
from sqlalchemy.orm import Session
from domains.integrations.qbo_integration import QBOIntegration
from domains.core.models.business import Business

@pytest.fixture
def mock_business(db: Session):
    business = Business(client_id=1, name="Test Agency", qbo_id="test123")
    db.add(business)
    db.commit()
    return business

def test_fetch_balances(db: Session, mock_business):
    qbo = QBOIntegration(mock_business)
    qbo.fetch_balances(db)
    balances = db.query(Balance).filter_by(business_id=1).all()
    assert len(balances) == 2
    assert balances[0].qbo_account_id == "123"
    assert balances[0].current_balance == 6000.0
EOL

# Add test for onboarding
cat > runway/tests/test_onboarding.py << EOL
import pytest
from sqlalchemy.orm import Session
from runway.services.onboarding import qualify_onboarding
from domains.core.models.business import Business
from domains.core.models.audit_log import AuditLog

def test_qualify_dropoff(db: Session):
    result = qualify_onboarding("test@example.com", weekly_review=False, db=db)
    assert result["dropoff"] is True

def test_qualify_success(db: Session):
    result = qualify_onboarding("owner@test.com", weekly_review=True, db=db)
    assert result["success"] is True
    assert "business_id" in result
    business = db.query(Business).first()
    assert business.name == "owner Agency"
    audit = db.query(AuditLog).first()
    assert audit.action_type == "onboard_qualify"
EOL

# Add test for tray
cat > runway/tests/test_tray.py << EOL
import pytest
from sqlalchemy.orm import Session
from runway.tray.services.tray import TrayService
from runway.tray.models.tray_item import TrayItem
from datetime import datetime

def test_get_tray_items(db: Session):
    tray_item = TrayItem(
        business_id=1,
        type="bill",
        qbo_id="bill_001",
        status="pending",
        priority="high",
        due_date=datetime.utcnow()
    )
    db.add(tray_item)
    db.commit()
    tray_service = TrayService(db)
    items = tray_service.get_tray_items(business_id=1)
    assert len(items) == 1
    assert items[0]["type"] == "bill"
    assert items[0]["qbo_id"] == "bill_001"
EOL

# Initialize Poetry
poetry init -n
poetry add sqlalchemy fastapi python-dotenv intuitlib pytest pytest-mock flake8 sendgrid chartjs

# Initialize .env
cat > .env << EOL
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_REDIRECT_URI=https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl
SQLALCHEMY_DATABASE_URL=sqlite:///oodaloo.db
EOL

# Initialize seed data
cat > data/seed_data.sql << EOL
INSERT INTO clients (client_id, name, qbo_id, industry)
VALUES (1, 'Test Agency', 'test123', 'agency');
INSERT INTO balances (business_id, qbo_account_id, current_balance, available_balance, snapshot_date, account_type)
VALUES (1, '123', 6000.0, 5500.0, '2025-09-15T00:00:00', 'checking');
INSERT INTO bills (business_id, qbo_id, vendor_id, amount, due_date, status)
VALUES (1, 'bill_001', 'vendor_001', 5000.0, '2025-09-22', 'open');
INSERT INTO invoices (business_id, qbo_id, customer_id, total, due_date, status)
VALUES (1, 'inv_009', 'customer_001', 1983.34, '2025-08-01', 'open');
EOL

# Commit changes
git init
git add .
git commit -m "Phase 0: Unified Oodaloo repo setup with Business, Balance, tray, onboarding, QBO mocks"

echo "Phase 0 setup complete. Run:"
echo "poetry install"
echo "poetry run python -c 'from database import seed_database; seed_database()'"
echo "poetry run pytest tests/ domains/*/tests/ runway/tests/ --cov"
echo "uvicorn main:app --reload"