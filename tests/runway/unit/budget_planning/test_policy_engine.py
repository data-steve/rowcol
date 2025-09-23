import pytest
from domains.policy.services.policy_engine import PolicyEngineService
from domains.policy.models.rule import Rule as RuleModel
from domains.policy.models.policy_profile import PolicyProfile

@pytest.mark.skip(reason="Phase 5+ functionality - categorize_transaction is part of Smart Automation Engine")
def test_categorize_transaction(db):
    # Create a policy profile first
    profile = PolicyProfile(
        business_id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Profile",
        description="Test policy profile",
        thresholds={"posting": 100, "variance": 50, "capitalization": 1000, "manual_jes": 0, "ocr_review": 0}
    )
    db.add(profile)
    db.flush()  # Get the profile_id
    
    # Create a test rule
    rule = RuleModel(
        business_id="550e8400-e29b-41d4-a716-446655440000",
        policy_profile_id=profile.profile_id,
        field="description",
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
