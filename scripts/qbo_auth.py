from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("QBO_CLIENT_ID")
client_secret = os.getenv("QBO_CLIENT_SECRET")
redirect_uri = "http://localhost:8000/callback"
environment = "sandbox"

auth_client = AuthClient(client_id, client_secret, redirect_uri, environment)
url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
print(f"Visit this URL to authorize: {url}")