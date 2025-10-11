#!/usr/bin/env python3
"""
QBO Token Management Script

This script helps get and refresh QBO tokens for testing.
It uses the QBOAuthService to manage tokens properly.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from infra.qbo.auth import QBOAuthService, QBOEnvironment
from infra.qbo.config import qbo_config

def print_status(message, status="INFO"):
    """Print status message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['QBO_CLIENT_ID', 'QBO_CLIENT_SECRET']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print_status(f"Missing required environment variables: {', '.join(missing)}", "ERROR")
        print_status("Please set these in your .env file or environment", "ERROR")
        return False
    
    print_status("Environment variables found", "SUCCESS")
    return True

def get_tokens_interactive():
    """Get tokens through interactive OAuth flow."""
    print_status("Starting QBO OAuth flow...")
    
    # Use a test business ID
    business_id = "test_business_001"
    
    # Create auth service
    auth_service = QBOAuthService(business_id, QBOEnvironment.SANDBOX)
    
    # Initiate OAuth flow
    try:
        oauth_data = auth_service.initiate_oauth_flow("test_user")
        auth_url = oauth_data['auth_url']
        
        print_status(f"Please visit this URL to authorize the app:", "INFO")
        print(f"\n{auth_url}\n")
        
        # Get authorization code from user
        auth_code = input("Enter the authorization code from the URL: ").strip()
        realm_id = input("Enter the realm_id (company ID) from the URL: ").strip()
        
        if not auth_code or not realm_id:
            print_status("Authorization code and realm_id are required", "ERROR")
            return False
        
        # Complete OAuth flow
        print_status("Exchanging authorization code for tokens...")
        token_data = auth_service.complete_oauth_flow(auth_code, auth_code, realm_id)
        
        # Store tokens
        success = auth_service.store_tokens(
            token_data['access_token'],
            token_data['refresh_token']
        )
        
        if success:
            print_status("Tokens stored successfully!", "SUCCESS")
            print_status(f"Business ID: {business_id}")
            print_status(f"Realm ID: {realm_id}")
            return True
        else:
            print_status("Failed to store tokens", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"OAuth flow failed: {e}", "ERROR")
        return False

def test_existing_tokens():
    """Test if existing tokens work."""
    print_status("Testing existing tokens...")
    
    business_id = "test_business_001"
    auth_service = QBOAuthService(business_id, QBOEnvironment.SANDBOX)
    
    # Check connection status
    status = auth_service.get_connection_status()
    print_status(f"Connection status: {status}")
    
    # Try to get valid token
    token = auth_service.get_valid_access_token()
    if token:
        print_status("Valid access token found!", "SUCCESS")
        print_status(f"Token: {token[:20]}...")
        return True
    else:
        print_status("No valid access token found", "WARNING")
        return False

def main():
    """Main function."""
    print_status("QBO Token Management Script")
    print_status("=" * 50)
    
    # Check environment
    if not check_environment():
        return 1
    
    # Test existing tokens first
    if test_existing_tokens():
        print_status("Existing tokens are working!", "SUCCESS")
        return 0
    
    # If no working tokens, start OAuth flow
    print_status("No working tokens found. Starting OAuth flow...")
    if get_tokens_interactive():
        print_status("Token setup complete!", "SUCCESS")
        return 0
    else:
        print_status("Token setup failed", "ERROR")
        return 1

if __name__ == "__main__":
    exit(main())
