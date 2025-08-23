# Import all fixtures from the main conftest.py
# This allows domain tests to access shared fixtures
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import all fixtures from the main conftest
from tests.conftest import *
