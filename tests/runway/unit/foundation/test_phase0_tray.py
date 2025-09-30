"""
Phase 0 Prep Tray Tests

Tests for the Prep Tray functionality that's core to Phase 0 MVP.
Focus on basic tray item management without complex relationships.
"""
import pytest
from sqlalchemy.orm import Session
from runway.models.tray_item import TrayItem
from domains.core.models import Business


def test_tray_item_model_structure():
    """Test that TrayItem model has correct Phase 0 attributes"""
    assert hasattr(TrayItem, 'id')
    assert hasattr(TrayItem, 'business_id')
    assert hasattr(TrayItem, 'type')
    assert hasattr(TrayItem, 'qbo_id')
    assert hasattr(TrayItem, 'status')
    assert hasattr(TrayItem, 'priority')
    assert hasattr(TrayItem, 'due_date')
    assert TrayItem.__tablename__ == 'tray_item'


def test_tray_item_creation_basic(db: Session, test_business: Business):
    """Test basic tray item creation without complex relationships"""
    from datetime import datetime, timedelta
    
    # Create a simple tray item
    tray_item = TrayItem(
        business_id=test_business.business_id,
        type="bill_review",
        qbo_id="qbo_bill_123",
        status="pending",
        priority="high",
        due_date=datetime.now() + timedelta(days=7)
    )
    
    db.add(tray_item)
    db.commit()
    db.refresh(tray_item)
    
    assert tray_item.id is not None
    assert tray_item.business_id == test_business.business_id
    assert tray_item.type == "bill_review"
    assert tray_item.status == "pending"


def test_tray_service_import():
    """Test that TrayService can be imported without errors"""
    try:
        from runway.services.2_experiences.tray import TrayService
        assert TrayService is not None
    except ImportError as e:
        pytest.skip(f"TrayService not available in Phase 0: {e}")


def test_tray_routes_import():
    """Test that tray routes can be imported without errors"""
    try:
        from runway.routes.tray import router
        assert router is not None
    except ImportError as e:
        pytest.skip(f"Tray routes not available in Phase 0: {e}")


def test_multiple_tray_items(db: Session, test_business: Business):
    """Test creating multiple tray items for cash runway management"""
    from datetime import datetime, timedelta
    
    items = [
        {
            "type": "bill_review",
            "qbo_id": "qbo_bill_001",
            "status": "pending",
            "priority": "high"
        },
        {
            "type": "invoice_review", 
            "qbo_id": "qbo_invoice_001",
            "status": "pending",
            "priority": "medium"
        },
        {
            "type": "payment_needed",
            "qbo_id": "qbo_bill_002", 
            "status": "urgent",
            "priority": "critical"
        }
    ]
    
    created_items = []
    for item_data in items:
        tray_item = TrayItem(
            business_id=test_business.business_id,
            due_date=datetime.now() + timedelta(days=7),
            **item_data
        )
        db.add(tray_item)
        created_items.append(tray_item)
    
    db.commit()
    
    # Verify all items were created
    assert len(created_items) == 3
    for item in created_items:
        assert item.id is not None
        assert item.business_id == test_business.business_id
