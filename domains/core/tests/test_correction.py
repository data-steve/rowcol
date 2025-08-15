import pytest
from fastapi.testclient import TestClient
from main import app
from domains.core.services.correction import CorrectionService
from domains.core.models.correction import Correction as CorrectionModel

client = TestClient(app)

def test_apply_correction(db, test_firm, test_bill):
    service = CorrectionService(db)
    correction = service.apply_correction(test_firm.firm_id, test_bill.bill_id, "6000-Expenses")
    assert correction.firm_id == test_firm.firm_id
    assert correction.final["account"] == "6000-Expenses"

def test_update_bill_endpoint(test_firm, test_bill):
    response = client.patch(
        f"/api/ingest/ap/bills/{test_bill.bill_id}?firm_id={test_firm.firm_id}&gl_account=6000-Expenses"
    )
    assert response.status_code == 200
    assert response.json()["gl_account"] == "6000-Expenses"