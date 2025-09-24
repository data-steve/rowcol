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
import webbrowser
from datetime import datetime, timedelta
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

load_dotenv()

def save_tokens_to_database(access_token: str, refresh_token: str, realm_id: str) -> bool:
    """Save tokens to database"""
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
                print("✅ Updated existing QBO integration")
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
                print("✅ Created new QBO integration")
            
            session.commit()
            print(f"✅ Tokens saved to database for business: {business.business_id}")
            print(f"🏢 Realm ID: {realm_id}")
            print("⏰ Access token expires in 1 hour, refresh token in 101 days")
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
    except:
        print("❌ Could not open browser - copy the URL above")
    
    print("\n2️⃣ After authorizing, you'll be redirected to the OAuth playground.")
    print("   Copy the 'code' and 'realmId' from the URL parameters.")
    print()
    
    # Get input from user
    auth_code = input("📝 Paste the authorization code: ").strip()
    if not auth_code:
        print("❌ No authorization code provided. Exiting.")
        return
    
    realm_id = input("📝 Paste the realm ID (company ID): ").strip()
    if not realm_id:
        print("❌ No realm ID provided. Exiting.")
        return
    
    print("\n3️⃣ Exchanging authorization code for tokens...")
    
    try:
        # Exchange code for tokens
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        
        access_token = auth_client.access_token
        refresh_token = auth_client.refresh_token
        
        print(f"✅ Got access token: {access_token[:20]}...")
        print(f"✅ Got refresh token: {refresh_token[:20]}...")
        
        # Save to database
        if save_tokens_to_database(access_token, refresh_token, realm_id):
            print("\n🎉 QBO Setup Complete!")
            print("✅ Tokens saved to database")
            print("✅ Your QBO integration is ready to use")
            print("\nTest it with:")
            print("   poetry run pytest tests/integration/test_real_qbo_api.py -m qbo_real_api")
        else:
            print("\n❌ Setup failed - could not save to database")
            
    except Exception as e:
        print(f"❌ Token exchange failed: {str(e)}")
        print("💡 Make sure the authorization code and realm ID are correct.")

if __name__ == "__main__":
    main()
