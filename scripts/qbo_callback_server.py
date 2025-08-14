from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from intuitlib.client import AuthClient
from dotenv import load_dotenv
import os
import uvicorn
import json
from datetime import datetime

load_dotenv()

app = FastAPI()

# QBO OAuth configuration
client_id = os.getenv("QBO_CLIENT_ID")
client_secret = os.getenv("QBO_CLIENT_SECRET")
redirect_uri = "http://localhost:8000/callback"
environment = "sandbox"

auth_client = AuthClient(client_id, client_secret, redirect_uri, environment)

@app.get("/callback")
async def oauth_callback(code: str = None, realmId: str = None, state: str = None):
    """Handle the OAuth callback from QuickBooks Online"""
    try:
        if not code:
            return JSONResponse({"error": "No authorization code received"}, status_code=400)
        
        print(f"Received auth code: {code}")
        print(f"Realm ID: {realmId}")
        print(f"State: {state}")
        
        # Exchange the authorization code for access tokens
        auth_client.get_bearer_token(code, realm_id=realmId)
        
        # Get the tokens
        access_token = auth_client.access_token
        refresh_token = auth_client.refresh_token
        
        print(f"Access Token: {access_token[:20]}...")
        print(f"Refresh Token: {refresh_token[:20]}...")
        
        # Save full tokens to a file
        tokens_data = {
            "timestamp": datetime.now().isoformat(),
            "realm_id": realmId,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
        tokens_file = "qbo_tokens.json"
        with open(tokens_file, "w") as f:
            json.dump(tokens_data, f, indent=2)
        
        print(f"Full tokens saved to: {tokens_file}")
        print(f"Access Token (full): {access_token}")
        print(f"Refresh Token (full): {refresh_token}")
        
        return JSONResponse({
            "success": True,
            "message": "OAuth flow completed successfully!",
            "access_token": access_token[:20] + "...",
            "refresh_token": refresh_token[:20] + "...",
            "realm_id": realmId,
            "tokens_saved_to": tokens_file
        })
        
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple home page to test the server"""
    return """
    <h1>QBO OAuth Callback Server</h1>
    <p>This server is running and ready to handle OAuth callbacks.</p>
    <p>Use the qbo_auth.py script to start the OAuth flow.</p>
    """

if __name__ == '__main__':
    print("Starting QBO OAuth callback server on http://localhost:8000")
    print("Make sure to run this before starting the OAuth flow!")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
