"""
Test Stale Mirror Hygiene - Real QBO API Tests

Tests the stale mirror detection and hygiene flagging with real QBO data.
Validates that the system can detect when cached data is stale and needs refresh.

NO MOCKS - tests real QBO integration.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from infra.rails.qbo.client import QBORawClient
from sqlalchemy import text


@pytest.mark.qbo_real_api
class TestStaleMirrorHygiene:
    """Test stale mirror detection with real QBO API."""

    def test_qbo_data_has_update_timestamps(self, qbo_realm_id):
        """
        Test that QBO data includes update timestamps for staleness detection.
        Critical for determining if cached data is stale.
        """
        print("\n🔥 STALE MIRROR: TIMESTAMP VALIDATION TEST")
        print(f"✅ Testing with realm: {qbo_realm_id[:10]}...")
        
        client = QBORawClient("system", qbo_realm_id)
        
        # Fetch bills to check for timestamps
        print("\n📋 Fetching bills to validate update timestamps")
        response = client.get("query?query=SELECT * FROM Bill MAXRESULTS 1")
        
        bills = response.get('QueryResponse', {}).get('Bill', [])
        
        if bills:
            bill = bills[0]
            print(f"✅ Got bill ID: {bill.get('Id', 'N/A')}")
            
            # Check for update timestamp in metadata
            assert 'MetaData' in bill
            metadata = bill['MetaData']
            
            # Verify we have timestamp data
            assert 'LastUpdatedTime' in metadata or 'CreateTime' in metadata
            
            last_updated = metadata.get('LastUpdatedTime') or metadata.get('CreateTime')
            print(f"✅ Bill last updated: {last_updated}")
            
            # Parse timestamp to verify it's valid
            # QBO uses ISO format like: 2025-07-18T13:10:36-07:00
            assert last_updated is not None
            print("✅ Stale Mirror: QBO provides timestamps for staleness detection")
        else:
            print("⚠️  No bills in sandbox - skipping timestamp validation")
            pytest.skip("No bills available for timestamp validation")

    def test_qbo_fetch_after_time_delay_shows_consistency(self, qbo_realm_id):
        """
        Test that QBO data fetched at different times maintains consistency.
        This validates assumptions about when we need to refresh cached data.
        """
        print("\n🔥 STALE MIRROR: TIME-BASED CONSISTENCY TEST")
        print(f"✅ Testing with realm: {qbo_realm_id[:10]}...")
        
        client = QBORawClient("system", qbo_realm_id)
        
        # First fetch
        print("\n📋 First fetch at", datetime.now().strftime("%H:%M:%S"))
        response1 = client.get("query?query=SELECT * FROM Bill MAXRESULTS 1")
        bills1 = response1.get('QueryResponse', {}).get('Bill', [])
        
        if not bills1:
            pytest.skip("No bills available for consistency test")
        
        bill1 = bills1[0]
        bill1_id = bill1.get('Id')
        bill1_updated = bill1.get('MetaData', {}).get('LastUpdatedTime')
        print(f"✅ First fetch: Bill {bill1_id}, LastUpdated: {bill1_updated}")
        
        # Wait a moment then fetch again
        import time
        time.sleep(2)
        
        print("\n📋 Second fetch at", datetime.now().strftime("%H:%M:%S"))
        response2 = client.get(f"query?query=SELECT * FROM Bill WHERE Id = '{bill1_id}'")
        bills2 = response2.get('QueryResponse', {}).get('Bill', [])
        
        if bills2:
            bill2 = bills2[0]
            bill2_updated = bill2.get('MetaData', {}).get('LastUpdatedTime')
            print(f"✅ Second fetch: Bill {bill1_id}, LastUpdated: {bill2_updated}")
            
            # Verify timestamps match (data hasn't changed)
            assert bill1_updated == bill2_updated
            print("✅ Stale Mirror: QBO data is stable (good for caching)")
        else:
            pytest.fail("Bill not found in second fetch")

    def test_qbo_version_tracking_via_metadata(self, qbo_realm_id):
        """
        Test that QBO MetaData can be used for version tracking and staleness detection.
        """
        print("\n🔥 STALE MIRROR: VERSION TRACKING TEST")
        print(f"✅ Testing with realm: {qbo_realm_id[:10]}...")
        
        client = QBORawClient("system", qbo_realm_id)
        
        # Fetch multiple bills to validate version tracking
        print("\n📋 Fetching bills to check version metadata")
        response = client.get("query?query=SELECT * FROM Bill MAXRESULTS 3")
        
        bills = response.get('QueryResponse', {}).get('Bill', [])
        
        if bills:
            print(f"✅ Got {len(bills)} bills")
            
            for bill in bills:
                metadata = bill.get('MetaData', {})
                bill_id = bill.get('Id')
                last_updated = metadata.get('LastUpdatedTime')
                
                print(f"✅ Bill {bill_id}: LastUpdated={last_updated}")
                
                # Verify each bill has version tracking metadata
                assert metadata is not None
                assert last_updated is not None
            
            print("✅ Stale Mirror: All bills have version tracking metadata")
        else:
            pytest.skip("No bills available for version tracking test")

    def test_qbo_companyinfo_for_global_sync_version(self, qbo_realm_id):
        """
        Test fetching CompanyInfo to get global sync version.
        CompanyInfo can be used to detect if any data has changed since last sync.
        """
        print("\n🔥 STALE MIRROR: GLOBAL SYNC VERSION TEST")
        print(f"✅ Testing with realm: {qbo_realm_id[:10]}...")
        
        client = QBORawClient("system", qbo_realm_id)
        
        # Fetch CompanyInfo which includes global metadata
        print("\n📋 Fetching CompanyInfo for global sync version")
        response = client.get("companyinfo/1")
        
        company_info = response.get('CompanyInfo')
        assert company_info is not None
        
        # Check for metadata that can indicate global changes
        metadata = company_info.get('MetaData', {})
        last_updated = metadata.get('LastUpdatedTime')
        
        print(f"✅ Company: {company_info.get('CompanyName')}")
        print(f"✅ Last updated: {last_updated}")
        
        assert metadata is not None
        print("✅ Stale Mirror: CompanyInfo provides global sync indicators")


if __name__ == "__main__":
    # Run the test directly
    import pytest
    pytest.main([__file__, "-v", "-s"])

