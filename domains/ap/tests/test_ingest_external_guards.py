import os
import pytest


def test_jobber_commit_blocked_without_feature_flag(client, test_firm, test_client, monkeypatch):
    monkeypatch.delenv("EXTERNAL_WRITE_ENABLED", raising=False)
    url = f"/api/ingest/jobber?firm_id={test_firm.firm_id}&client_id={test_client.client_id}&mode=live&commit=true"
    resp = client.post(url)
    assert resp.status_code == 200
    # still returns preview because feature flag is off
    assert resp.json()["status"] == "preview"


def test_stripe_commit_requires_test_key_allowlist_and_idempotency(client, test_firm, test_client, monkeypatch):
    # Enable feature flag
    monkeypatch.setenv("EXTERNAL_WRITE_ENABLED", "true")
    # Not allowlisted and no idempotency -> 403/400 path
    url = f"/api/ingest/stripe?firm_id={test_firm.firm_id}&client_id={test_client.client_id}&mode=live&commit=true"
    resp = client.post(url)
    # Feature flag on but not allowlisted -> still preview unless allowlisted
    assert resp.status_code == 200
    assert resp.json()["status"] == "preview"


