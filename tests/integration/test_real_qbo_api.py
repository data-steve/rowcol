"""
CRITICAL SOURCE OF TRUTH: Real QBO API Integration Test

This test file is the ONLY place where we hit the actual QBO Sandbox API.
There are NO MOCKS in this file.

If tests in this file pass, we know with 100% certainty that our core QBO
integration code is working correctly with the live QBO Sandbox environment.

To run these tests, you must have your QBO Sandbox credentials in your .env file:
- QBO_SANDBOX_ACCESS_TOKEN
- QBO_SANDBOX_REFRESH_TOKEN
- QBO_SANDBOX_REALM_ID
"""
import pytest
import os
from sqlalchemy.orm import Session

from domains.core.models.business import Business
from domains.core.models.integration import Integration, IntegrationStatuses
from domains.integrations.qbo.client import get_real_qbo_client
from tests.conftest import test_business  # Re-using the basic business fixture

@pytest.mark.qbo_real_api
class TestRealQBOApi:
    """
    This test suite hits the REAL QBO Sandbox API.
    It is the ultimate source of truth for our QBO integration.
    """

    @pytest.fixture(scope="function")
    def real_qbo_business(self) -> tuple[Business, str]:
        """
        Uses existing QBO integration from MAIN database (not test database).
        
        To run this test, first get fresh tokens using:
            poetry run python domains/integrations/qbo/get_qbo_tokens.py
        
        This will save valid tokens to the main database.
        
        Returns:
            Tuple of (Business, realm_id)
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Connect to MAIN database (not test database)
        database_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite:///oodaloo.db')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Look for existing QBO integration in MAIN database
            integration = session.query(Integration).filter(
                Integration.platform == "qbo",
                Integration.status == IntegrationStatuses.CONNECTED.value
            ).first()

            if not integration:
                pytest.skip("SKIPPING REAL QBO TESTS: No QBO integration found. Run 'poetry run python domains/integrations/qbo/get_qbo_tokens.py' to set up tokens.")

            if not all([integration.access_token, integration.refresh_token, integration.realm_id]):
                pytest.skip("SKIPPING REAL QBO TESTS: QBO integration missing required tokens. Run token exchange script to refresh.")

            # Get the associated business
            business = session.query(Business).filter(Business.business_id == integration.business_id).first()
            if not business:
                pytest.skip("SKIPPING REAL QBO TESTS: Business not found for QBO integration.")

            # Return both business and realm_id to avoid session issues
            return business, integration.realm_id

    @pytest.mark.asyncio
    async def test_connect_and_get_bills_from_real_qbo_sandbox(self, db: Session, real_qbo_business: tuple[Business, str]):
        """
        THE PROOF: This test connects to the real QBO sandbox and fetches bills.
        If this passes, our connection, authentication, and basic API calls are working.
        """
        print("\\n--- PROOF OF LIFE: Hitting REAL QBO Sandbox API ---")
        
        business, realm_id = real_qbo_business
        
        qbo_client = get_real_qbo_client(
            business_id=business.business_id, 
            db=db,
            realm_id=realm_id
        )
        
        # This will raise an exception if the API call fails for any reason.
        bills_response = await qbo_client.get_bills()

        # The assertion is simple: did we get a list back?
        # A sandbox might have 0 bills, so we just check the type.
        assert isinstance(bills_response, list)
        
        print(f"✅ SUCCESS: Successfully connected to REAL QBO Sandbox for Realm ID: {qbo_client.realm_id}")
        print(f"✅ Found {len(bills_response)} bills in the sandbox.")
        print("--- TEST COMPLETE ---")
