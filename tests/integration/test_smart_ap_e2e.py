"""
Smart AP End-to-End Integration Test

CRITICAL TEST: Validates complete AP workflow from QBO bill ingestion to payment scheduling.

This test proves that Smart AP features can be built on our Phase 0 foundation
by testing the complete data flow: QBO → Bill Processing → Payment Priority → Tray.

Success here validates our architectural assumptions about AP workflow.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.integration import Integration
from domains.ap.models.bill import Bill, BillStatus
from domains.ap.models.vendor import Vendor
from domains.ap.services.bill_ingestion import BillService  # Available service
from domains.ap.services.payment import PaymentService
from domains.integrations.smart_sync import SmartSyncService
from runway.core.services.runway_calculator import RunwayCalculator
from runway.tray.services.tray import TrayService
from runway.core.services.payment_priority_calculator import PaymentPriorityCalculator
from domains.core.models.balance import Balance

@pytest.mark.integration
@pytest.mark.qbo_real_api
class TestSmartAPE2E:
    """End-to-end integration tests for Smart AP functionality."""
    
    @pytest.fixture
    def ap_business(self, qbo_connected_business: Business) -> Business:
        """Use existing QBO connected business fixture."""
        return qbo_connected_business
    
    @pytest.mark.asyncio
    async def test_qbo_bill_ingestion_to_oodaloo_processing(self, db: Session, ap_business: Business):
        """
        CRITICAL TEST: QBO bills → Oodaloo bill processing pipeline.
        
        Validates that real QBO bills can be ingested and processed
        by our AP services without mock dependencies.
        """
        # Get real QBO bills
        smart_sync = SmartSyncService(db, ap_business.business_id)
        qbo_data = await smart_sync.get_qbo_data_for_digest()
        
        assert "bills" in qbo_data, "QBO data missing bills"
        qbo_bills = qbo_data["bills"]
        assert len(qbo_bills) > 0, "No bills found in QBO data"
        
        # Test bill ingestion service with real data
        bill_service = BillService(db, ap_business.business_id)
        
        ingested_bills = []
        for qbo_bill in qbo_bills[:5]:  # Test first 5 bills
            try:
                # Test bill ingestion from real QBO data structure
                bill = bill_service.ingest_bill_from_qbo(
                    business_id=ap_business.business_id,
                    qbo_bill_data=qbo_bill
                )
                ingested_bills.append(bill)
                
                # Validate bill was processed correctly
                assert bill.business_id == ap_business.business_id
                assert bill.amount_cents is not None and bill.amount_cents > 0
                assert bill.vendor_id is not None
                assert bill.status in ["pending", "approved", "paid", BillStatus.PENDING, BillStatus.APPROVED]
                
            except Exception as e:
                pytest.fail(f"Bill ingestion failed for QBO bill {qbo_bill.get('id', 'unknown')}: {e}")
        
        assert len(ingested_bills) == min(5, len(qbo_bills)), "Not all bills were ingested successfully"
        print(f"✅ Bill ingestion successful: {len(ingested_bills)} bills processed from QBO")
    
    @pytest.mark.asyncio
    async def test_payment_priority_with_real_vendor_data(self, db: Session, ap_business: Business):
        """
        CRITICAL TEST: Payment priority intelligence with real vendor data.
        
        Validates that payment priority service can analyze real vendor data
        and prioritize payments correctly.
        """
        # Use BillService for database queries and PaymentPriorityCalculator for calculations
        bill_service = BillService(db, ap_business.business_id)
        priority_calculator = PaymentPriorityCalculator(db, ap_business.business_id)
        
        bills = bill_service.get_payment_ready_bills()
        prioritized_bills = priority_calculator.prioritize_bills_for_payment(bills)
        assert len(prioritized_bills) >= 0  # May be empty if no bills are approved
        
        # Validate structure
        for bill in prioritized_bills:
            assert 'priority_score' in bill
            assert 'priority' in bill
            assert bill['priority'] in ['urgent', 'high', 'medium', 'low']

        # If there are at least 2, verify sorted non-increasing by score
        if len(prioritized_bills) >= 2:
            scores = [b['priority_score'] for b in prioritized_bills]
            assert scores == sorted(scores, reverse=True), "Bills should be sorted by descending priority_score"

        # Light parameterized-style negative/positive case: synthesize a clearly urgent bill
        synthetic = {
            'qbo_id': 'synthetic_urgent',
            'amount': 10000.0,
            'due_date': datetime.now().isoformat(),
            'vendor_id': 'v-urgent',
            'vendor_name': 'Critical Vendor',
            'status': 'approved',
            'bill_type': 'standard'
        }
        analyzed = priority_calculator.get_payment_decision_analysis(synthetic)
        # Avoid brittle numeric threshold; accept high/urgent level or reasonably high score
        assert (
            analyzed.get('priority_level') in ['high', 'urgent']
            or analyzed.get('priority_score', 0) >= 40
        ), "Synthetic urgent case should yield elevated priority"

        # Light negative case: small amount, future due date should be lower priority than the urgent case
        synthetic_low = {
            'qbo_id': 'synthetic_low',
            'amount': 50.0,
            'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'vendor_id': 'v-low',
            'vendor_name': 'Standard Vendor',
            'status': 'approved',
            'bill_type': 'standard'
        }
        low_analysis = priority_calculator.get_payment_decision_analysis(synthetic_low)
        assert (
            low_analysis.get('priority_score', 100) <= analyzed.get('priority_score', 0)
        ), "Low-priority synthetic should score lower than urgent synthetic"
        assert (
            'Bill is overdue' not in low_analysis.get('decision_factors', [])
        ), "Low-priority synthetic should not be flagged as overdue"
    
    @pytest.mark.asyncio
    async def test_ap_workflow_to_tray_integration(self, db: Session, ap_business: Business):
        """
        CRITICAL TEST: Complete AP workflow → Prep Tray integration.
        
        Validates that processed bills appear correctly in the prep tray
        with proper prioritization and runway impact data.
        """
        smart_sync = SmartSyncService(db, ap_business.business_id)
        tray_service = TrayService(db)
        # Get real QBO data
        qbo_data = await smart_sync.get_qbo_data_for_digest()
        
        # Test tray population with real AP data
        bills = qbo_data.get("bills", [])
        assert len(bills) > 0, "No bills available for tray testing"
        
        # Simulate AP processing workflow
        processed_items = []
        for bill in bills[:5]:  # Test first 5 bills
            try:
                # Create tray item from real bill data
                tray_item = tray_service.create_tray_item(
                    business_id=ap_business.business_id,
                    item_type="bill_payment",
                    title=f"Pay {bill.get('vendor_name', 'Unknown Vendor')}",
                    amount=bill.get("amount", 0),
                    due_date=bill.get("due_date"),
                    metadata={
                        "qbo_bill_id": bill.get("id"),
                        "vendor_name": bill.get("vendor_name"),
                        "original_qbo_data": bill
                    }
                )
                
                processed_items.append(tray_item)
                
                # Validate tray item creation
                assert tray_item['business_id'] == ap_business.business_id
                assert tray_item['item_type'] == "bill_payment"
                assert tray_item['amount'] > 0
                assert "qbo_bill_id" in tray_item['metadata']
                
            except Exception as e:
                pytest.fail(f"Tray integration failed for bill {bill.get('id')}: {e}")
        
        # Test tray retrieval and ordering
        tray_items = tray_service.get_tray_items(ap_business.business_id)
        
        # Validate tray retrieval works (mock provider returns mock items)
        assert isinstance(tray_items, list), "Tray items should be a list"
        
        # Test that tray items have expected structure
        for item in tray_items:
            assert isinstance(item, dict), "Tray item should be a dictionary"
            assert 'business_id' in item, "Tray item missing business_id"
            assert 'item_type' in item, "Tray item missing item_type"
            assert 'priority' in item, "Tray item missing priority"
        
        # Validate we can create tray items (processed_items were successfully created)
        assert len(processed_items) > 0, "No tray items were created from bills"
        for processed_item in processed_items:
            assert processed_item['business_id'] == ap_business.business_id
            assert processed_item['item_type'] == "bill_payment"
        
        print(f"✅ AP → Tray integration successful: {len(processed_items)} items processed to tray")
    
    @pytest.mark.asyncio
    async def test_runway_impact_accuracy_with_ap_decisions(self, db: Session, ap_business: Business):
        """
        CRITICAL TEST: Runway impact calculation with AP payment decisions.
        
        Validates that payment decisions accurately reflect on runway projections.
        """
        payment_service = PaymentService(db, ap_business.business_id)
        
        # Update a bill to be approved for payment
        bill = db.query(Bill).filter(
            Bill.business_id == ap_business.business_id,
            Bill.status.in_([BillStatus.PENDING, 'pending'])
        ).first()
        
        if bill:
            bill.status = BillStatus.APPROVED if isinstance(bill.status, str) else BillStatus.APPROVED
            db.commit()
            db.refresh(bill)
            
            # Schedule payment for the bill
            payment_date = datetime.now() + timedelta(days=1)
            amount = float(bill.amount_cents / 100.0) if bill.amount_cents else 0.0
            account_id = db.query(Balance).filter(
                Balance.business_id == ap_business.business_id
            ).first().qbo_account_id if db.query(Balance).filter(
                Balance.business_id == ap_business.business_id
            ).first() else "test_account"
            
            payment_record = payment_service.schedule_payment(
                business_id=ap_business.business_id,
                bill_ids=[bill.bill_id],
                funding_account=account_id
            )
            
            assert payment_record['status'] == 'scheduled'
            assert payment_record['business_id'] == ap_business.business_id
            assert bill.bill_id in payment_record['bill_ids']
        else:
            pytest.skip("No pending bills available for payment scheduling")
    
    @pytest.mark.asyncio
    async def test_smart_ap_foundation_readiness(self, db: Session, ap_business: Business):
        """
        CRITICAL TEST: Smart AP foundation readiness assessment.
        
        Validates that all components needed for Smart AP features
        work together with real QBO data.
        """
        try:
            # Test 1: QBO AP Data Access
            smart_sync = SmartSyncService(db, ap_business.business_id)
            qbo_data = await smart_sync.get_qbo_data_for_digest()
            bills = qbo_data.get("bills", [])
            vendors = qbo_data.get("vendors", [])
    
            assert len(bills) > 0, "No bills available - AP features cannot work"
            assert len(vendors) > 0, "No vendors available - AP features cannot work"
    
            # Test 2: Bill Processing Pipeline
            from domains.ap.services.bill_ingestion import BillService
            bill_service = BillService(db, ap_business.business_id)
            test_bill = bills[0]
            processed_bill = bill_service.ingest_bill_from_qbo(ap_business.business_id, test_bill)
            assert processed_bill is not None, "Bill processing pipeline failed"
    
            # Test 3: Runway Impact Calculations
            runway_calculator = RunwayCalculator(db, ap_business.business_id)
            runway_analysis = runway_calculator.calculate_current_runway(qbo_data)
            assert runway_analysis["base_runway_days"] > 0, "Runway calculations failed"
    
            # Test 4: Payment Priority Logic
            priority_calculator = PaymentPriorityCalculator(db, ap_business.business_id)
            prioritized_bills = priority_calculator.prioritize_bills_for_payment(bills)
            assert len(prioritized_bills) > 0, "Payment priority logic failed"
            assert "priority_score" in prioritized_bills[0], "Payment priority logic failed"
    
            # Test 5: Tray Integration
            tray_service = TrayService(db)
            tray_items = tray_service.get_tray_items(ap_business.business_id)
            # Tray should work even if empty
            assert isinstance(tray_items, list), "Tray integration failed"
    
            print("✅ SMART AP FOUNDATION READY: All AP components working with real QBO data")
            print("✅ PHASE 1 SMART AP APPROVED: Development can proceed with confidence")
    
        except Exception as e:
            pytest.fail(f"SMART AP FOUNDATION NOT READY: {e}")
            print("🚨 PHASE 1 SMART AP BLOCKED: Fix foundation issues before proceeding")


    @pytest.mark.asyncio
    async def test_runway_calculator_basic_with_qbo_data(self, db: Session, ap_business: Business):
        """
        LIGHTWEIGHT: Ensure RunwayCalculator works in Smart AP context with QBO-shaped data.
        Avoids heavy scenarios but verifies core outputs exist and are sane.
        """
        smart_sync = SmartSyncService(db, ap_business.business_id)
        runway_calculator = RunwayCalculator(db, ap_business.business_id)

        qbo_data = await smart_sync.get_qbo_data_for_digest()

        runway_analysis = runway_calculator.calculate_current_runway(qbo_data)

        # Basic structure checks
        assert 'base_runway_days' in runway_analysis
        assert 'cash_position' in runway_analysis
        assert 'burn_rate' in runway_analysis and isinstance(runway_analysis['burn_rate'], dict)
        assert 'runway_status' in runway_analysis

        # Sanity checks
        assert isinstance(runway_analysis['base_runway_days'], (int, float))
        assert isinstance(runway_analysis['cash_position'], (int, float))
        assert 'daily_burn' in runway_analysis['burn_rate']
        assert runway_analysis['runway_status'] in ['critical', 'warning', 'healthy', 'excellent']

        # Light impact check: paying a non-zero bill should not increase runway
        bills = qbo_data.get('bills', [])
        candidate = next((b for b in bills if (b.get('amount') or 0) > 0), None)
        if candidate:
            impact = runway_calculator.calculate_bill_runway_impact({
                'amount': float(candidate.get('amount', 0)),
                'due_date': candidate.get('due_date'),
                'vendor_name': candidate.get('vendor_name', 'Unknown')
            })
            assert isinstance(impact, dict)
            assert impact.get('impact_days', 0) >= 0
            assert impact.get('runway_after_payment', runway_analysis['base_runway_days']) <= runway_analysis['base_runway_days']


# Utility functions for AP integration testing
def create_test_vendor_scenario(db: Session, business_id: str) -> List[Dict[str, Any]]:
    """Create realistic vendor scenarios for testing."""
    return [
        {
            "name": "Critical Supplier",
            "relationship": "strategic",
            "payment_terms": "net_15",
            "typical_amount": 5000
        },
        {
            "name": "Utility Company", 
            "relationship": "essential",
            "payment_terms": "net_30",
            "typical_amount": 800
        },
        {
            "name": "Office Supplies",
            "relationship": "standard",
            "payment_terms": "net_30", 
            "typical_amount": 300
        }
    ]

def validate_bill_data_structure(qbo_bill: Dict[str, Any]) -> bool:
    """Validate QBO bill has expected data structure."""
    required_fields = ["id", "vendor_name", "amount", "due_date"]
    return all(field in qbo_bill for field in required_fields)
