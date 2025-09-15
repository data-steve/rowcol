from typing import Tuple, Optional
# Mocked OAuth for Phase 0

class QBOAuth:
    def __init__(self):
        self.tokens = {}  # firm_id -> (access, refresh)

    def initiate_oauth(self, redirect_uri: str) -> str:
        return "https://mock.qbo.auth/url?state=mock_state"

    def exchange_tokens(self, code: str, firm_id: int) -> Tuple[str, Optional[str]]:
        access = f"mock_access_{firm_id}"
        refresh = f"mock_refresh_{firm_id}"
        self.tokens[firm_id] = (access, refresh)
        return access, refresh

qbo_auth = QBOAuth()
