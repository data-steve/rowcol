#!/usr/bin/env python3
"""
QBO Simple API Tests - Basic QBO API functionality

This test proves that:
1. QBO API connectivity works with real tokens
2. QBO Bills query works
3. QBO Accounts query works
4. The foundation is ready for MVP development
"""

import pytest
import os
from sqlalchemy import text
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from conftest import get_database_engine

from infra.rails.qbo.client import QBORawClient


@pytest.mark.qbo_real_api
class TestQBOSimpleAPI:
    """Simple QBO API tests to prove foundation works."""

    def test_qbo_api_connectivity(self):
        """Test that QBO API connectivity works with real tokens."""
        print("\n🔥 QBO API CONNECTIVITY TEST")
        
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
            
            # Test QBO client with automatic token refresh
            print("\n📋 Testing QBO client connectivity")
            client = QBORawClient("system", realm_id)
            
            try:
                response = client.get("companyinfo/1")
                print("✅ SUCCESS: QBO API connectivity works!")
                
                company_name = response.get('CompanyInfo', {}).get('CompanyName', 'N/A')
                print(f"✅ Company: {company_name}")
                
                assert company_name is not None
                assert 'CompanyInfo' in response
                
            except Exception as e:
                print(f"❌ QBO API connectivity failed: {e}")
                pytest.fail(f"QBO API connectivity failed: {e}")

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
            
            # Test QBO client with automatic token refresh
            print("\n📋 Testing QBO Bills query")
            client = QBORawClient("system", realm_id)
            
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
            
            # Test QBO client with automatic token refresh
            print("\n📋 Testing QBO Accounts query")
            client = QBORawClient("system", realm_id)
            
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
                
            except Exception as e:
                print(f"❌ QBO Accounts query failed: {e}")
                pytest.fail(f"QBO Accounts query failed: {e}")