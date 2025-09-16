from typing import Tuple, Optional
from domains.core.models.business import Business

class QBOAuth:
    def __init__(self):
        self.tokens = {}  # business_id -> (access, refresh)

    def initiate_oauth(self, redirect_uri: str) -> str:
        return "https://mock.qbo.auth/url?state=mock_state"

    def exchange_tokens(self, code: str, business_id: int) -> Tuple[str, Optional[str]]:
        access = f"mock_access_{business_id}"
        refresh = f"mock_refresh_{business_id}"
        self.tokens[business_id] = (access, refresh)
        return access, refresh

qbo_auth = QBOAuth()
