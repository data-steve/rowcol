"""
Simple test configuration for direct QBO API tests.
NO complex imports, NO database setup - just basic pytest config.
"""

import pytest
from sqlalchemy import create_engine

# Database configuration - SINGLE SOURCE OF TRUTH
DATABASE_URL = 'sqlite:///../../_clean/rowcol.db'

def get_database_engine():
    """Get database engine for tests. SINGLE SOURCE OF TRUTH for database path."""
    return create_engine(DATABASE_URL)

def get_database_url():
    """Get database URL for tests. SINGLE SOURCE OF TRUTH for database path."""
    return DATABASE_URL

# Just define the marker
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "qbo_real_api: mark test as requiring real QBO API access"
    )

