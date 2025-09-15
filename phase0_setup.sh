#!/bin/bash
set -e
echo "Setting up Phase 0 Week 1-2 for Oodaloo v4.2..."

# Create runway/ structure
mkdir -p runway/{models,services,routes,templates,tests}
touch runway/__init__.py runway/tests/conftest.py

# Write runway/__init__.py
cat > runway/__init__.py << 'EOF'
__version__ = "4.2.0"
EOF

# Write runway/tests/conftest.py
cat > runway/tests/conftest.py << 'EOF'
# Empty; use top-level tests/conftest.py for common fixtures
import pytest
EOF

# Move and refactor QBO files
mkdir -p domains/integrations/tests
mv _parked/qbo/qbo_auth.py domains/integrations/qbo_auth.py
cat > domains/integrations/qbo_auth.py << 'EOF'
from typing import Tuple, Optional
# Mocked OAuth for Phase 0

class QBOAuth:
    def __init__(self):
        self.tokens = {}  # firm_id -> (access, refresh)

    def initiate_oauth(self, redirect_uri: str) -> str:
        return "https://mock.qbo.auth/url?state=mock_state"

    def exchange_tokens(self, code: str, firm_id: int) -> Tuple[str, Optional[str]]:
        access = f"mock_access_{firm_id}"
        refresh = f"mock_refresh_{firm_id}"
        self.tokens[firm_id] = (access, refresh)
        return access, refresh

qbo_auth = QBOAuth()
EOF

cat > domains/integrations/__init__.py << 'EOF'
from .qbo_auth import qbo_auth
from .qbo_integration import QBOIntegration
from .webhooks import handle_webhook
__all__ = ['qbo_auth', 'QBOIntegration', 'handle_webhook']
EOF

cat > domains/integrations/qbo_integration.py << 'EOF'
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from domains.core.models import Firm

# Load mocks
with open('static/qbo_mock_data.json', 'r') as f:
    MOCK_BASE = json.load(f)

# Adapt from realistic_test_data.json
MOCK_DATA = MOCK_BASE.copy()
MOCK_DATA['invoices'] = [
    {"qbo_id": "inv_009", "customer": "Pine Valley HOA", "amount": 1983.34, "due_date": "2025-08-01", "aging_days": 42}
]
MOCK_DATA['bills'] = [
    {"qbo_id": "bill_001", "vendor": "Rent LLC", "amount": 5000.0, "due_date": "2025-09-22"}
]
MOCK_DATA['accounts'] = [{"id": "checking", "current_balance": 6000.0}]

class QBOIntegration:
    def __init__(self, firm: Firm):
        self.firm = firm
        self.tenant_id = firm.qbo_tenant_id

    def get_bills(self, due_days: int = 14) -> List[Dict[str, Any]]:
        today = datetime.now().date()
        return [b for b in MOCK_DATA['bills'] if (today - datetime.strptime(b['due_date'], '%Y-%m-%d').date()).days <= due_days]

    def get_invoices(self, aging_days: int = 30) -> List[Dict[str, Any]]:
        return [i for i in MOCK_DATA['invoices'] if i.get('aging_days', 0) > aging_days]

    def get_account_balance(self) -> float:
        return MOCK_DATA['accounts'][0]['current_balance']

def handle_webhook(payload: Dict) -> str:
    return "OK"
EOF

cat > static/qbo_mock_data.json << 'EOF'
{
  "bills": [
    {"qbo_id": "bill_001", "vendor": "Rent LLC", "amount": 5000.0, "due_date": "2025-09-22"}
  ],
  "invoices": [
    {"qbo_id": "inv_009", "customer": "Pine Valley HOA", "amount": 1983.34, "due_date": "2025-08-01", "aging_days": 42}
  ],
  "accounts": [
    {"id": "checking", "current_balance": 6000.0}
  ]
}
EOF

# Update database.py
cat > database.py << 'EOF'
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///bookclose.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Register models
from domains.core.models.firm import Firm
from domains.core.models.user import User
from domains.core.models.audit_log import AuditLog
from domains.tray.models.tray_item import TrayItem
from domains.core.models.notification import Notification

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
        conn = sqlite3.connect("bookclose.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='firm'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM firm")
            count = cursor.fetchone()[0]
            if count == 0:
                with open("data/seed_data.sql", "r") as f:
                    conn.executescript(f.read())
                cursor.execute("""
                    INSERT INTO firm (id, name, qbo_tenant_id, current_balance, reserved_balance)
                    VALUES (1, 'Test Agency', 'test123', 6000.0, 0.0)
                """)
                cursor.execute("""
                    INSERT INTO user (id, firm_id, email, role, qbo_access_token, qbo_refresh_token)
                    VALUES (1, 1, 'owner@test.com', 'owner', 'mock_access', 'mock_refresh')
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
EOF

# Update core models
cat > domains/core/models/firm.py << 'EOF'
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Firm(Base, TimestampMixin):
    __tablename__ = "firm"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    qbo_tenant_id = Column(String, unique=True, index=True)
    current_balance = Column(Float, default=0.0)
    reserved_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    users = relationship("User", back_populates="firm")
    tray_items = relationship("TrayItem", back_populates="firm")
    notifications = relationship("Notification", back_populates="firm")
EOF

cat > domains/core/models/user.py << 'EOF'
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class User(Base, TimestampMixin, TenantMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firm.id"))
    email = Column(String, unique=True, index=True)
    role = Column(String, default="owner")
    qbo_access_token = Column(String)
    qbo_refresh_token = Column(String)
    firm = relationship("Firm", back_populates="users")
EOF

cat > domains/core/models/audit_log.py << 'EOF'
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin
from enum import Enum

class AuditSource(Enum):
    USER = "user"

class AuditAction(Enum):
    APPROVE_BILL = "approve_bill"

class EntityType(Enum):
    BILL = "bill"

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firm.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    action_type = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    firm = relationship("Firm")
    user = relationship("User")
EOF

cat > domains/core/models/notification.py << 'EOF'
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class Notification(Base, TimestampMixin):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firm.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    recipient_role = Column(String, default="owner")
    event_type = Column(String)
    content = Column(JSON)
    sent_at = Column(DateTime, nullable=True)
    firm = relationship("Firm", back_populates="notifications")
    user = relationship("User")
EOF

# Move and refactor tray to runway
mv domains/tray runway/tray
mkdir -p runway/tray/models
cat > runway/tray/models/tray_item.py << 'EOF'
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class TrayItem(Base, TimestampMixin):
    __tablename__ = "tray_item"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firm.id"))
    type = Column(String)
    qbo_id = Column(String)
    status = Column(String, default="pending")
    priority = Column(String, default="medium")
    due_date = Column(DateTime)
    allowed_roles = Column(String, default="owner")
    firm = relationship("Firm", back_populates="tray_items")
EOF

cat > runway/tray/services/tray.py << 'EOF'
from typing import List, Optional
from sqlalchemy.orm import Session
from domains.bank.models.bank_transaction import BankTransaction
from domains.ar.models.invoice import Invoice
from ..models.tray_item import TrayItem

class TrayService:
    def __init__(self, db: Session):
        self.db = db

    def get_tray_items(self, firm_id: int) -> List[dict]:
        items = self.db.query(TrayItem).filter(
            TrayItem.firm_id == firm_id,
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

    def confirm_action(self, firm_id: int, tray_item_id: int, action: str, invoice_ids: Optional[List[int]] = None):
        item = self.db.query(TrayItem).filter(
            TrayItem.firm_id == firm_id,
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
EOF

cat > runway/tray/routes/tray.py << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services.tray import TrayService
from database import get_db

router = APIRouter(prefix="/api/v1/tray", tags=["Tray"])

@router.get("/")
def get_tray(firm_id: int, db: Session = Depends(get_db)):
    return TrayService(db).get_tray_items(firm_id)

@router.post("/{id}/confirm")
def confirm_action(firm_id: int, id: int, action: str, invoice_ids: Optional[List[int]] = None, db: Session = Depends(get_db)):
    return TrayService(db).confirm_action(firm_id, id, action, invoice_ids)
EOF

# Onboarding
cat > runway/services/onboarding.py << 'EOF'
from fastapi import Form, Depends
from sqlalchemy.orm import Session
from domains.core.models import Firm, User, AuditLog
from database import get_db
from domains.integrations.qbo_auth import qbo_auth

def qualify_onboarding(email: str, weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    if not weekly_review:
        return {"dropoff": True, "reason": "No cash ritual need (20-30% expected)"}
    firm = Firm(name=f"{email.split('@')[0]} Agency", qbo_tenant_id=f"mock_{email.replace('@', '')}")
    db.add(firm)
    db.commit()
    user = User(firm_id=firm.id, email=email, role="owner")
    db.add(user)
    db.commit()
    access, refresh = qbo_auth.exchange_tokens("mock_code", firm.id)
    user.qbo_access_token = access
    user.qbo_refresh_token = refresh
    db.commit()
    audit = AuditLog(
        firm_id=firm.id, user_id=user.id, action_type="onboard_qualify",
        entity_type="firm", entity_id=str(firm.id), details={"qualified": True}
    )
    db.add(audit)
    db.commit()
    return {"success": True, "firm_id": firm.id, "next": "Connect QBO"}
EOF

cat > runway/templates/onboarding.html << 'EOF'
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
EOF

cat > runway/routes/onboarding.py << 'EOF'
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from ..services.onboarding import qualify_onboarding
from database import get_db

router = APIRouter(prefix="/onboard", tags=["Onboarding"])

@router.post("/")
async def onboard(email: str = Form(...), weekly_review: bool = Form(False), db: Session = Depends(get_db)):
    result = qualify_onboarding(email, weekly_review, db)
    if result.get("dropoff"):
        return {"msg": result["reason"]}
    return result
EOF

# Tests
cat > domains/integrations/tests/test_qbo_integration.py << 'EOF'
import pytest
from domains.integrations.qbo_integration import QBOIntegration
from domains.core.models import Firm

@pytest.fixture
def mock_firm():
    return Firm(id=1, name="Test", qbo_tenant_id="test123", current_balance=6000.0)

def test_get_bills(mock_firm):
    qbo = QBOIntegration(mock_firm)
    bills = qbo.get_bills(14)
    assert len(bills) >= 1
    assert bills[0]['amount'] == 5000.0

def test_get_invoices(mock_firm):
    qbo = QBOIntegration(mock_firm)
    invoices = qbo.get_invoices(30)
    assert len(invoices) == 1
    assert invoices[0]['aging_days'] > 30
EOF

cat > runway/tests/test_onboarding.py << 'EOF'
import pytest
from runway.services.onboarding import qualify_onboarding
from domains.core.models import Firm, AuditLog

def test_qualify_dropoff(db_session):
    result = qualify_onboarding("test@example.com", weekly_review=False, db=db_session)
    assert result["dropoff"] is True

def test_qualify_success(db_session):
    result = qualify_onboarding("owner@test.com", weekly_review=True, db=db_session)
    assert result["success"] is True
    assert "firm_id" in result
    firm = db_session.query(Firm).first()
    assert firm.name == "owner Agency"
    audit = db_session.query(AuditLog).first()
    assert audit.action_type == "onboard_qualify"
EOF

cat > tests/test_database.py << 'EOF'
import pytest
from sqlalchemy.orm import Session
from database import get_db, Firm, User

@pytest.fixture
def db_session():
    db = next(get_db())
    yield db
    db.rollback()

def test_create_firm(db_session: Session):
    firm = Firm(name="Test Agency", qbo_tenant_id="test123", current_balance=6000.0)
    db_session.add(firm)
    db_session.commit()
    db_session.refresh(firm)
    assert firm.id is not None
    assert firm.current_balance == 6000.0
EOF

# Update domains/__init__.py
cat > domains/__init__.py << 'EOF'
from .core.models import Firm, User, AuditLog, Notification
from .tray.models import TrayItem
from .integrations import qbo_auth, QBOIntegration, handle_webhook
__all__ = ['Firm', 'User', 'AuditLog', 'Notification', 'TrayItem', 'qbo_auth', 'QBOIntegration', 'handle_webhook']
EOF

# Update pyproject.toml (append sendgrid, chartjs if not present)
if ! grep -q "sendgrid" pyproject.toml; then
    sed -i '/\[tool.poetry.dependencies\]/a sendgrid = "^6.10.0"\nchartjs = {version = "^3.0.0", optional = true}' pyproject.toml
fi

echo "Setup complete! Run:"
echo "poetry run python -c 'from database import seed_database; seed_database()'"
echo "poetry run pytest tests/ domains/*/tests/ runway/tests/ --cov"
echo "uvicorn main:app --reload"
echo "Check /onboard/docs for Swagger."