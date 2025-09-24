"""
Direct QBO API Test - No Complex Service Layer

This test directly calls the QBO API using the tokens from the main database,
without going through the complex service layer that has database session issues.
"""

import pytest
import os
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domains.core.models.integration import Integration, IntegrationStatuses


@pytest.mark.qbo_real_api
class TestDirectQBOApi:
    """Direct QBO API test without service layer complexity."""

    @pytest.mark.asyncio
    async def test_direct_qbo_api_call(self):
        """
        Direct test: Get tokens from main DB and call QBO API directly.
        This proves the tokens work without any service layer complications.
        """
        print("\n🔥 DIRECT QBO API TEST - No Service Layer")
        
        # Get tokens from main database
        database_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///oodaloo.db')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            integration = session.query(Integration).filter(
                Integration.platform == "qbo",
                Integration.status == IntegrationStatuses.CONNECTED.value
            ).first()
            
            if not integration:
                pytest.skip("No QBO integration found. Run get_qbo_tokens.py first.")
            
            if not all([integration.access_token, integration.refresh_token, integration.realm_id]):
                pytest.skip("QBO integration missing tokens.")
            
            print(f"✅ Found tokens for realm: {integration.realm_id}")
            print(f"✅ Access token: {integration.access_token[:20]}...")
            
            # Make direct API call to QBO
            url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{integration.realm_id}/query"
            params = {
                "query": "SELECT * FROM Bill WHERE DueDate <= '2025-10-23' AND Balance > '0'",
                "minorversion": "65"
            }
            headers = {
                "Authorization": f"Bearer {integration.access_token}",
                "Accept": "application/json"
            }
            
            print(f"🌐 Making direct API call to: {url}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                print(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    bills = data.get("QueryResponse", {}).get("Bill", [])
                    print(f"✅ SUCCESS: Got {len(bills)} bills from QBO!")
                    print("🎉 DIRECT QBO API CALL WORKS!")
                    
                    # Simple assertion
                    assert isinstance(bills, list)
                    
                elif response.status_code == 401:
                    print("❌ 401 Unauthorized - Token expired or invalid")
                    print("💡 Run get_qbo_tokens.py to get fresh tokens")
                    pytest.fail("QBO API returned 401 - tokens are invalid")
                    
                else:
                    print(f"❌ API call failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    pytest.fail(f"QBO API call failed with status {response.status_code}")
