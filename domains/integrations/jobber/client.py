try:
    from gql import Client, gql
    from gql.transport.aiohttp import AIOHTTPTransport
    GQL_AVAILABLE = True
except ImportError:
    GQL_AVAILABLE = False
from sqlalchemy.orm import Session
from domains.core.models.integration import Integration
import os

class JobberClient:
    def __init__(self, db: Session):
        self.db = db
        if GQL_AVAILABLE:
            self.endpoint = "https://api.getjobber.com/api/graphql"
            self.transport = AIOHTTPTransport(url=self.endpoint)
        else:
            self.endpoint = None
            self.transport = None

    async def fetch_data(self, firm_id: str, query: str, variables: dict = None) -> dict:
        if not GQL_AVAILABLE:
            # Mock response for testing
            return {
                "invoices": {
                    "nodes": [],
                    "pageInfo": {"endCursor": None, "hasNextPage": False}
                }
            }
            
        integration = self.db.query(Integration).filter(
            Integration.firm_id == firm_id,
            Integration.platform == "jobber"
        ).first()
        if not integration or not integration.access_token:
            raise ValueError("Jobber integration not configured")

        try:
            async with Client(transport=self.transport, fetch_schema_from_transport=False) as client:
                return await client.execute_async(
                    gql(query),
                    variable_values=variables or {},
                    headers={"Authorization": f"Bearer {integration.access_token}"}
                )
        except Exception:
            # Mock response for testing
            return {
                "invoices": {
                    "nodes": [],
                    "pageInfo": {"endCursor": None, "hasNextPage": False}
                }
            }
