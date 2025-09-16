from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use in-memory SQLite for tests, file-based for dev
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///bookclose.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
                cursor.executescript("""
                    INSERT INTO clients (client_id, name, qbo_id, industry)
                    VALUES (1, 'Test Agency', 'test123', 'agency');
                    INSERT INTO balances (business_id, qbo_account_id, current_balance, available_balance, snapshot_date, account_type)
                    VALUES (1, '123', 6000.0, 5500.0, '2025-09-15T00:00:00', 'checking');
                    INSERT INTO bills (business_id, qbo_id, vendor_id, amount, due_date, status)
                    VALUES (1, 'bill_001', 'vendor_001', 5000.0, '2025-09-22', 'open');
                    INSERT INTO invoices (business_id, qbo_id, customer_id, total, due_date, status)
                    VALUES (1, 'inv_009', 'customer_001', 1983.34, '2025-08-01', 'open');
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