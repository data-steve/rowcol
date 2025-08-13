import pytest
from services.policy_engine import PolicyEngineService
from models.rule import Rule as RuleModel
from schemas.suggestion import Suggestion

def test_categorize_transaction(db):
    # Create a test rule first
    rule = RuleModel(
        firm_id="550e8400-e29b-41d4-a716-446655440000",
        client_id=None,
        priority=10,
        match_type="contains",
        pattern="Starbucks",
        output={"account": "6000", "class": "Food", "memo": "Coffee", "confidence": 0.9},
        scope="global"
    )
    db.add(rule)
    db.commit()
    
    service = PolicyEngineService(db)
    txn = {"txn_id": "txn_001", "description": "Starbucks", "amount": 10.50}
    suggestion = service.categorize_transaction(txn, "550e8400-e29b-41d4-a716-446655440000")
    assert suggestion.txn_id == "txn_001"
    assert len(suggestion.top_k) > 0
