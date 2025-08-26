#!/usr/bin/env python3
"""
Simple QBO token exchange using the OAuth2 Playground redirect URL.
This eliminates the need for ngrok or local callback servers.
"""

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

def main():
    client_id = os.getenv("QBO_CLIENT_ID")
    client_secret = os.getenv("QBO_CLIENT_SECRET")
    redirect_uri = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"
    environment = "sandbox"
    
    if not client_id or not client_secret:
        print("❌ Missing QBO_CLIENT_ID or QBO_CLIENT_SECRET in .env")
        return
    
    auth_client = AuthClient(client_id, client_secret, redirect_uri, environment)
    
    print("🔗 QBO OAuth Flow")
    print("=" * 50)
    print()
    
    # Step 1: Get authorization URL
    auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    print("1️⃣ Visit this URL to authorize your app:")
    print(f"   {auth_url}")
    print()
    
    # Step 2: Get the authorization code from user
    print("2️⃣ After authorizing, you'll be redirected to the OAuth2 Playground.")
    print("   Copy the 'code' and 'realmId' parameters from the URL.")
    print()
    
    auth_code = input("📝 Enter the authorization code: ").strip()
    if not auth_code:
        print("❌ No authorization code provided. Exiting.")
        return
    
    realm_id = input("📝 Enter the realm ID (company ID): ").strip()
    if not realm_id:
        print("❌ No realm ID provided. Exiting.")
        return
    
    print()
    print("3️⃣ Exchanging authorization code for tokens...")
    
    try:
        # Step 3: Exchange code for tokens
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        
        # Step 4: Save tokens
        access_token = auth_client.access_token
        refresh_token = auth_client.refresh_token
        
        tokens_data = {
            "timestamp": datetime.now().isoformat(),
            "realm_id": realm_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "environment": environment
        }
        
        # Save to file
        tokens_file = "qbo_tokens.json"
        with open(tokens_file, "w") as f:
            json.dump(tokens_data, f, indent=2)
        
        print("✅ Success! Tokens saved.")
        print(f"📁 Tokens saved to: {tokens_file}")
        print(f"🔑 Access Token: {access_token[:20]}...")
        print(f"🔄 Refresh Token: {refresh_token[:20]}...")
        print(f"🏢 Realm ID: {realm_id}")
        print()
        
        # Step 5: Update .env instructions
        print("4️⃣ Update your .env file with these values:")
        print(f"QBO_ACCESS_TOKEN={access_token}")
        print(f"QBO_REFRESH_TOKEN={refresh_token}")
        print(f"QBO_REALM_ID={realm_id}")
        print()
        print("🎉 QBO OAuth setup complete!")
        
    except Exception as e:
        print(f"❌ Token exchange failed: {str(e)}")
        print("💡 Make sure the authorization code and realm ID are correct.")

if __name__ == "__main__":
    main()
