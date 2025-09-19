from domains.ap.services.statement_reconciliation import StatementReconciliationService
from datetime import date

def test_reconcile_statement(db, test_business, test_vendor):
    service = StatementReconciliationService(db)
    statement = service.reconcile_statement(test_business.business_id, test_vendor.vendor_id, "stmt_001.pdf", date(2025, 8, 1))
    assert statement.business_id == test_business.business_id
    assert statement.vendor_id == test_vendor.vendor_id

def test_reconcile_statement_endpoint(client, test_business, test_vendor):
    
    response = client.post(
        f"/api/ingest/ap/statements/reconcile?business_id={test_business.business_id}",
        json={"vendor_id": test_vendor.vendor_id, "file_ref": "stmt_001.pdf", "period": "2025-08-01"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "reconciled"