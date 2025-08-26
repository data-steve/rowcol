from database import SessionLocal
from sqlalchemy import text


def test_seed_data_loaded_minimal():
    db = SessionLocal()
    try:
        # Check firms
        count_firms = db.execute(text("SELECT COUNT(*) FROM firms")).scalar() or 0
        assert count_firms >= 1

        # Check clients
        count_clients = db.execute(text("SELECT COUNT(*) FROM clients")).scalar() or 0
        assert count_clients >= 1

        # Check vendor_categories exist (used by categorization)
        count_vendor_cats = db.execute(text("SELECT COUNT(*) FROM vendor_categories")).scalar() or 0
        assert count_vendor_cats >= 1

        # Check at least one COA template row (used by mapping)
        count_coa = db.execute(text("SELECT COUNT(*) FROM coa_templates")).scalar() or 0
        assert count_coa >= 1

        # Check that invoices table exists (AR flow)
        db.execute(text("SELECT 1 FROM invoices LIMIT 1"))
    finally:
        db.close()


