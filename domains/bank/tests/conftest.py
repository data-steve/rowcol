"""
Bank domain test configuration.
Imports shared fixtures from root tests/conftest.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../tests')))

# Import shared fixtures
from conftest import mock_qbo, db, test_firm, test_client, client
