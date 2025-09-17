from db.session import SessionLocal
from sqlalchemy import text


def test_seed_data_loaded_minimal():
    db = SessionLocal()
    try:
        # Check businesses
        count_businesses = db.execute(text("SELECT COUNT(*) FROM businesses")).scalar() or 0
        assert count_businesses > 0

        # Check users
        count_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        assert count_users > 0

    finally:
        db.close()


