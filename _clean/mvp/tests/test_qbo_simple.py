#!/usr/bin/env python3
"""
QBO Simple API Tests - Basic QBO API functionality

This test proves that:
1. QBO API connectivity works with real tokens
2. QBO Bills query works
3. QBO Accounts query works
4. The foundation is ready for MVP development
"""

import pytest
import os
from sqlalchemy.orm import Session
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from conftest import db_session

from infra.rails.qbo.client import QBORawClient
from infra.db.models import SystemIntegrationToken


@pytest.mark.qbo_real_api
class TestQBOSimpleAPI:
    """Simple QBO API tests to prove foundation works."""

    def test_qbo_api_connectivity(self, db_session):
        """Test that QBO API connectivity works with real tokens."""
        # Get realm_id from database
        token = db_session.query(SystemIntegrationToken).filter(
            SystemIntegrationToken.rail == 'qbo',
            SystemIntegrationToken.environment == 'sandbox',
            SystemIntegrationToken.status == 'active'
        ).order_by(SystemIntegrationToken.updated_at.desc()).first()
        
        if not token:
            pytest.skip("No QBO system tokens found. Run qbo_token_setup.py --init-from-json first.")
        
        realm_id = token.external_id
        
        if not realm_id:
            pytest.skip("QBO business missing realm_id.")
        
        # Test QBO client with automatic token refresh
        client = QBORawClient("system", realm_id)
        response = client.get("companyinfo/1")
        
        company_name = response.get('CompanyInfo', {}).get('CompanyName', 'N/A')
        assert company_name is not None
        assert 'CompanyInfo' in response

    def test_qbo_bills_query(self, db_session):
        """Test that we can query bills from QBO sandbox."""
        # Get realm_id from database
        token = db_session.query(SystemIntegrationToken).filter(
            SystemIntegrationToken.rail == 'qbo',
            SystemIntegrationToken.environment == 'sandbox',
            SystemIntegrationToken.status == 'active'
        ).order_by(SystemIntegrationToken.updated_at.desc()).first()
        
        if not token:
            pytest.skip("No QBO system tokens found. Run qbo_token_setup.py --init-from-json first.")
        
        realm_id = token.external_id
        
        if not realm_id:
            pytest.skip("QBO business missing realm_id.")
        
        # Test QBO client with automatic token refresh
        client = QBORawClient("system", realm_id)
        response = client.get("query?query=SELECT * FROM Bill MAXRESULTS 5")
        
        bills = response.get('QueryResponse', {}).get('Bill', [])
        assert 'QueryResponse' in response

    def test_qbo_accounts_query(self, db_session):
        """Test that we can query accounts from QBO sandbox."""
        # Get realm_id from database
        token = db_session.query(SystemIntegrationToken).filter(
            SystemIntegrationToken.rail == 'qbo',
            SystemIntegrationToken.environment == 'sandbox',
            SystemIntegrationToken.status == 'active'
        ).order_by(SystemIntegrationToken.updated_at.desc()).first()
        
        if not token:
            pytest.skip("No QBO system tokens found. Run qbo_token_setup.py --init-from-json first.")
        
        realm_id = token.external_id
        
        if not realm_id:
            pytest.skip("QBO business missing realm_id.")
        
        # Test QBO client with automatic token refresh
        client = QBORawClient("system", realm_id)
        response = client.get("query?query=SELECT * FROM Account MAXRESULTS 5")
        
        accounts = response.get('QueryResponse', {}).get('Account', [])
        assert 'QueryResponse' in response