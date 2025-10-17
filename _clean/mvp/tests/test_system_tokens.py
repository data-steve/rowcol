#!/usr/bin/env python3
"""
Test System Token Management

This script tests the system token management functionality.
"""

import os
import sys
from datetime import datetime, timezone

# Add project root to path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
sys.path.insert(0, root_path)

def test_system_token_management():
    """Test system token management functionality."""
    print("🧪 Testing System Token Management")
    print("=" * 50)
    
    try:
        from mvp.infra.rails.qbo.auth import QBOAuthService, QBOEnvironment
        
        # Create auth service for system tokens
        auth_service = QBOAuthService(
            business_id="system", 
            environment=QBOEnvironment.SANDBOX
        )
        
        # Test 1: Check if system is connected
        print("\n1. Testing system connection status...")
        is_connected = auth_service.is_connected()
        print(f"   System connected: {is_connected}")
        
        # Test 2: Get valid access token
        print("\n2. Testing access token retrieval...")
        access_token = auth_service.get_valid_access_token()
        if access_token:
            print(f"   ✅ Access token retrieved: TOKEN_REDACTED")
        else:
            print("   ❌ No access token available")
        
        # Test 3: Get connection status details
        print("\n3. Testing connection status details...")
        status = auth_service.get_connection_status()
        print(f"   Status: {status}")
        
        # Test 4: Test QBO API call (if token available)
        if access_token:
            print("\n4. Testing QBO API connectivity...")
            try:
                from mvp.infra.rails.qbo.client import QBORawClient
                client = QBORawClient("system", "9341455170902651")
                # Simple test - get company info
                response = client.get("companyinfo/1")
                print(f"   ✅ QBO API call successful: {response.get('QueryResponse', {}).get('CompanyInfo', [{}])[0].get('CompanyName', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ QBO API call failed: {e}")
        else:
            print("\n4. Skipping API test - no access token")
        
        print("\n" + "=" * 50)
        print("✅ System token management test complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This test requires the MVP package structure")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_system_token_management()
