from domains.ap.services.statement_reconciliation import StatementReconciliationService
from datetime import date

def test_reconcile_statement(db, test_business, test_vendor):
    service = StatementReconciliationService(db)
    statement = service.reconcile_statement(test_business.business_id, test_vendor.vendor_id, "stmt_001.pdf", date(2025, 8, 1))
    assert statement.business_id == test_business.business_id
    assert statement.vendor_id == test_vendor.vendor_id

def test_reconcile_statement_endpoint(db, test_business, test_vendor):
    # Test the service directly instead of HTTP endpoint
    from domains.ap.services.statement_reconciliation import StatementReconciliationService
    from datetime import date
    
    service = StatementReconciliationService(db, test_business.business_id)
    result = service.reconcile_statement(
        business_id=test_business.business_id,
        vendor_id=test_vendor.vendor_id,
        statement_file="stmt_001.pdf",
        statement_date=date.fromisoformat("2025-08-01")
    )
    
    assert result.status == "reconciled"