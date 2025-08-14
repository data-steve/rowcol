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
        conn = sqlite3.connect("bookclose.db")
        # Check if tables exist and have data
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engagements'")
        if cursor.fetchone():
            # Table exists, check if it has data
            cursor.execute("SELECT COUNT(*) FROM engagements")
            count = cursor.fetchone()[0]
            if count == 0:  # Only seed if empty
                with open("data/seed_data.sql", "r") as f:
                    conn.executescript(f.read())
                conn.commit()
                logger.info("Database seeded successfully.")
        else:
            # Table doesn't exist, seed it
            with open("data/seed_data.sql", "r") as f:
                conn.executescript(f.read())
            conn.commit()
            logger.info("Database seeded successfully.")
        conn.close()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        conn.close()