# Tests

## File: tests/test_policy_engine.py
**Status**: New

```python
import pytest
from services.policy_engine import PolicyEngineService
from models.rule import Rule as RuleModel
from schemas.suggestion import Suggestion

def test_categorize_transaction(db_session):
    service = PolicyEngineService(db_session)
    txn = {"txn_id": "txn_001", "description": "Starbucks", "amount": 10.50}
    suggestion = service.categorize_transaction(txn, "550e8400-e29b-41d4-a716-446655440000")
    assert suggestion.txn_id == "txn_001"
    assert len(suggestion.top_k) > 0
```

## File: tests/test_vendor_normalization.py
**Status**: New

```python
import pytest
from services.vendor_normalization import VendorNormalizationService
from schemas.vendor_canonical import VendorCanonical

def test_normalize_vendor(db_session):
    service = VendorNormalizationService(db_session)
    vendor = service.normalize_vendor("Starbucks1234", "550e8400-e29b-41d4-a716-446655440000")
    assert vendor.canonical_name == "Starbucks"
    assert vendor.confidence > 0
```

## File: tests/test_integration.py
**Status**: New

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_automation_routes(db_session):
    response = client.post("/api/automation/vendors/normalize", json={
        "raw_name": "Starbucks1234",
        "firm_id": "550e8400-e29b-41d4-a716-446655440000"
    })
    assert response.status_code == 200
    assert response.json()["canonical_name"] == "Starbucks"

    response = client.post("/api/automation/categorize", json={
        "txn_id": "txn_001",
        "description": "Starbucks",
        "amount": 10.50,
        "firm_id": "550e8400-e29b-41d4-a716-446655440000"
    })
    assert response.status_code == 200
    assert response.json()["txn_id"] == "txn_001"
```