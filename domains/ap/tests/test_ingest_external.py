import pytest


def test_ingest_jobber_preview(client, test_firm, test_client):
    url = f"/api/ingest/jobber?firm_id={test_firm.firm_id}&client_id={test_client.client_id}&mode=mock"
    resp = client.post(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "preview"
    assert data["platform"] == "jobber"
    result = data["result"]
    assert "jobs" in result and isinstance(result["jobs"], list)
    assert "invoices" in result and isinstance(result["invoices"], list)


def test_ingest_stripe_preview(client, test_firm, test_client):
    url = f"/api/ingest/stripe?firm_id={test_firm.firm_id}&client_id={test_client.client_id}&mode=mock"
    resp = client.post(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "preview"
    assert data["platform"] == "stripe"
    result = data["result"]
    assert "charges" in result and isinstance(result["charges"], list)
    assert "payouts" in result and isinstance(result["payouts"], list)


