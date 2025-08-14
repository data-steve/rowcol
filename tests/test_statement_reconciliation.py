import pytest
from services.statement_reconciliation import StatementReconciliationService
from models.vendor_statement import VendorStatement as VendorStatementModel
from datetime import date
from unittest.mock import patch, MagicMock

@patch('services.statement_reconciliation.QuickBooks')
def test_reconcile_statement(mock_qb, db, test_firm, test_client, test_vendor):
    # Mock QBO client to return empty list for query
    mock_qb_instance = MagicMock()
    mock_qb_instance.query.return_value = []
    mock_qb.return_value = mock_qb_instance
    
    service = StatementReconciliationService(db)
    statement = service.reconcile_statement(test_firm.firm_id, test_vendor.vendor_id, "stmt_001.pdf", date(2025, 8, 1), test_client.client_id)
    assert statement.firm_id == test_firm.firm_id
    assert statement.vendor_id == test_vendor.vendor_id

@patch('services.statement_reconciliation.QuickBooks')
def test_reconcile_statement_endpoint(mock_qb, client, test_firm, test_client, test_vendor):
    # Mock QBO client to return empty list for query
    mock_qb_instance = MagicMock()
    mock_qb_instance.query.return_value = []
    mock_qb.return_value = mock_qb_instance
    
    response = client.post(
        f"/api/ingest/ap/statements/reconcile?firm_id={test_firm.firm_id}&client_id={test_client.client_id}",
        json={"vendor_id": test_vendor.vendor_id, "file_ref": "stmt_001.pdf", "period": "2025-08-01"}
    )
    assert response.status_code == 200
    assert response.json()["parsed_invoices"] is not None