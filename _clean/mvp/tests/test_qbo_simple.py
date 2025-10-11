#!/usr/bin/env python3
"""
Simple QBO API Test - Proves MVP Foundation Works

This test proves that:
1. QBO tokens are valid and working
2. QBO API calls work with real sandbox data
3. The foundation is ready for MVP development
"""

import pytest
import os
import httpx
from sqlalchemy import text
from conftest import get_database_engine


@pytest.mark.qbo_real_api
class TestQBOSimpleAPI:
    """Simple QBO API tests to prove foundation works."""

    @pytest.mark.asyncio
    async def test_qbo_api_connectivity(self):
        """Test that QBO API connectivity works with real tokens."""
        print("\n🔥 QBO API CONNECTIVITY TEST")
        
        # Get tokens from system integration tokens table
        engine = get_database_engine()

        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT external_id, access_token, refresh_token "
                "FROM system_integration_tokens "
                "WHERE rail = 'qbo' AND environment = 'sandbox' AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1"
            )).fetchone()
            
            if not result:
                pytest.skip("No QBO system tokens found. Run qbo_token_setup.py --init-from-json first.")
            
            realm_id, access_token, refresh_token = result
            
            if not all([access_token, realm_id]):
                pytest.skip("QBO business missing tokens.")
            
            print(f"✅ Found tokens for realm: {realm_id}")
            print(f"✅ Access token: {access_token[:20]}...")
            
            # Test QBO API call
            print("\n📋 Testing QBO API call")
            url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/companyinfo/{realm_id}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                
                print(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    company_name = data.get('CompanyInfo', {}).get('CompanyName', 'N/A')
                    print("✅ SUCCESS: QBO API call works!")
                    print(f"✅ Company: {company_name}")
                    assert response.status_code == 200
                    assert company_name is not None
                elif response.status_code == 401:
                    pytest.fail("QBO API returned 401 - tokens are invalid. Run qbo_token_setup.py --init-from-json")
                else:
                    pytest.fail(f"QBO API call failed with status {response.status_code}")

    def test_qbo_bills_query(self):
        """Test that we can query bills from QBO sandbox."""
        print("\n🔥 QBO BILLS QUERY TEST")
        
        # Get realm_id from database
        engine = get_database_engine()

        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT external_id FROM system_integration_tokens "
                "WHERE rail = 'qbo' AND environment = 'sandbox' AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1"
            )).fetchone()
            
            if not result:
                pytest.skip("No QBO system tokens found. Run qbo_token_setup.py --init-from-json first.")
            
            realm_id = result[0]
            
            if not realm_id:
                pytest.skip("QBO business missing realm_id.")
            
            print(f"✅ Testing with realm: {realm_id[:10]}...")
            
            # Use QBO client with auto-refresh
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from infra.rails.qbo.client import QBORawClient
            
            client = QBORawClient("system", realm_id)
            
            # Test QBO Bills query
            print("\n📋 Testing QBO Bills query")
            try:
                response = client.get("query?query=SELECT * FROM Bill MAXRESULTS 5")
                
                bills = response.get('QueryResponse', {}).get('Bill', [])
                print("✅ SUCCESS: QBO Bills query works!")
                print(f"✅ Found {len(bills)} bills")
                
                if bills:
                    first_bill = bills[0]
                    print(f"✅ First bill ID: {first_bill.get('Id', 'N/A')}")
                    print(f"✅ First bill total: {first_bill.get('TotalAmt', 'N/A')}")
                
                assert 'QueryResponse' in response
            except Exception as e:
                print(f"❌ QBO Bills query failed: {e}")
                pytest.fail(f"QBO Bills query failed: {e}")

    def test_qbo_accounts_query(self):
        """Test that we can query accounts from QBO sandbox."""
        print("\n🔥 QBO ACCOUNTS QUERY TEST")
        
        # Get realm_id from database
        engine = get_database_engine()

        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT external_id FROM system_integration_tokens "
                "WHERE rail = 'qbo' AND environment = 'sandbox' AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1"
            )).fetchone()
            
            if not result:
                pytest.skip("No QBO system tokens found. Run qbo_token_setup.py --init-from-json first.")
            
            realm_id = result[0]
            
            if not realm_id:
                pytest.skip("QBO business missing realm_id.")
            
            print(f"✅ Testing with realm: {realm_id[:10]}...")
            
            # Use QBO client with auto-refresh
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from infra.rails.qbo.client import QBORawClient
            
            client = QBORawClient("system", realm_id)
            
            # Test QBO Accounts query
            print("\n📋 Testing QBO Accounts query")
            try:
                response = client.get("query?query=SELECT * FROM Account MAXRESULTS 5")
                
                accounts = response.get('QueryResponse', {}).get('Account', [])
                print("✅ SUCCESS: QBO Accounts query works!")
                print(f"✅ Found {len(accounts)} accounts")
                
                if accounts:
                    first_account = accounts[0]
                    print(f"✅ First account: {first_account.get('Name', 'N/A')}")
                    print(f"✅ Account type: {first_account.get('AccountType', 'N/A')}")
                
                assert 'QueryResponse' in response
                assert len(accounts) > 0
            except Exception as e:
                print(f"❌ QBO Accounts query failed: {e}")
                pytest.fail(f"QBO Accounts query failed: {e}")


if __name__ == "__main__":
    # Run the test directly
    import asyncio
    
    async def run_tests():
        test_instance = TestQBOSimpleAPI()
        await test_instance.test_qbo_api_connectivity()
        await test_instance.test_qbo_bills_query()
        await test_instance.test_qbo_accounts_query()
        print("\n🎉 All QBO API tests passed!")
    
    asyncio.run(run_tests())
