#!/usr/bin/env python3
"""
Simple QBO Token Setup - Uses OAuth Playground (No Local Server Issues)

This script:
1. Opens the OAuth playground 
2. You authorize and get redirected back with code
3. You paste the code here
4. Script saves tokens to database

No redirect URI configuration needed.
"""

import os
import sys
import json
import webbrowser
from datetime import datetime, timedelta
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

load_dotenv()

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'dev_tokens.json')


def save_tokens_to_file(auth_client: AuthClient, realm_id: str):
    """Saves tokens to a durable JSON file for development."""
    token_data = {
        'access_token': auth_client.access_token,
        'refresh_token': auth_client.refresh_token,
        'realm_id': realm_id,
        'token_expires_at': (datetime.utcnow() + timedelta(seconds=auth_client.expires_in)).isoformat(),
        'refresh_token_expires_at': (datetime.utcnow() + timedelta(seconds=auth_client.x_refresh_token_expires_in)).isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=4)
    print(f"✅ Tokens saved to durable file: {TOKEN_FILE}")


def save_tokens_to_database(access_token: str, refresh_token: str, realm_id: str) -> bool:
    """Save tokens to database for runtime use (secondary to file storage)"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from domains.core.models.business import Business
        from domains.core.models.integration import Integration, IntegrationStatuses
        
        # Connect to database
        database_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///oodaloo.db')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Create or find business
            business = session.query(Business).first()
            if not business:
                business = Business(name="QBO Connected Business")
                session.add(business)
                session.flush()
            
            # Create or update QBO integration
            integration = session.query(Integration).filter(
                Integration.platform == "qbo",
                Integration.business_id == business.business_id
            ).first()
            
            if integration:
                # Update existing integration
                integration.access_token = access_token
                integration.refresh_token = refresh_token
                integration.realm_id = realm_id
                integration.status = IntegrationStatuses.CONNECTED.value
                integration.connected_at = datetime.utcnow()
                integration.token_expires_at = datetime.utcnow() + timedelta(hours=1)
                integration.expires_at = datetime.utcnow() + timedelta(days=101)
                print("✅ Updated existing QBO integration in database")
            else:
                # Create new integration
                integration = Integration(
                    business_id=business.business_id,
                    platform="qbo",
                    status=IntegrationStatuses.CONNECTED.value,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    realm_id=realm_id,
                    connected_at=datetime.utcnow(),
                    token_expires_at=datetime.utcnow() + timedelta(hours=1),
                    expires_at=datetime.utcnow() + timedelta(days=101)
                )
                session.add(integration)
                print("✅ Created new QBO integration in database")
            
            session.commit()
            return True
            
    except Exception as e:
        print(f"❌ Failed to save to database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Get QBO tokens and save to database"""
    print("🚀 QBO Token Setup")
    print("=" * 40)
    
    # Check credentials
    client_id = os.getenv("QBO_CLIENT_ID")
    client_secret = os.getenv("QBO_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing QBO_CLIENT_ID or QBO_CLIENT_SECRET in .env")
        return
    
    print(f"✅ Found credentials for client: {client_id[:10]}...")
    
    # Generate auth URL
    redirect_uri = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"
    auth_client = AuthClient(client_id, client_secret, redirect_uri, "sandbox")
    auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    
    print("\n1️⃣ Opening QBO authorization page...")
    print(f"   {auth_url}")
    
    # Open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Opened in your browser")
    except Exception:
        print("❌ Could not open browser - copy the URL above")
    
    print("\n2️⃣ After authorizing, you'll be redirected to the OAuth playground.")
    print("   Copy the 'code' and 'realmId' from the URL parameters.")
    print("\n⚠️  IMPORTANT: DO NOT click any 'GET TOKEN' buttons - just copy the code from the URL!")
    print()
    
    # Get input from user
    auth_code = input("📝 Paste the authorization code: ").strip()
    if not auth_code:
        print("❌ No authorization code provided. Exiting.")
        return
    
    # Get realm_id from environment (it's persistent for the app)
    realm_id = os.getenv("QBO_REALM_ID")
    if not realm_id:
        print("❌ QBO_REALM_ID not found in .env file. Please add it.")
        return
    print(f"✅ Using realm ID from .env: {realm_id}")
    
    print("\n3️⃣ Exchanging authorization code for tokens...")
    
    try:
        # Exchange code for tokens
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        
        access_token = auth_client.access_token
        refresh_token = auth_client.refresh_token
        
        print(f"✅ Got access token: {access_token[:20]}...")
        print(f"✅ Got refresh token: {refresh_token[:20]}...")
        
        # Save to durable file first
        save_tokens_to_file(auth_client, realm_id)

        # Then, save to database for immediate use by the running application
        if save_tokens_to_database(access_token, refresh_token, realm_id):
            print("\n🎉 QBO Setup Complete!")
            print("✅ Your QBO integration is ready to use")
            print("✅ Tokens saved to both database and dev_tokens.json")
            print("✅ System will self-heal from dev_tokens.json on future runs")
            print("\nTest it with:")
            print("   poetry run pytest tests/integration/test_qbo_api_direct.py -m qbo_real_api")
        else:
            print("\n❌ Setup failed - could not save to database")
            print("💡 Tokens were saved to dev_tokens.json, so the system can still self-heal")
            
    except Exception as e:
        print(f"❌ Token exchange failed: {str(e)}")
        print("💡 Make sure the authorization code and realm ID are correct.")

if __name__ == "__main__":
    main()
