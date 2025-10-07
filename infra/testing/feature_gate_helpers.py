"""
Feature Gate Testing Helpers

This module provides utilities for testing with feature gates enabled/disabled.
Allows for strategic test gating based on feature flags rather than blanket silencing.

Usage:
    from infra.testing.feature_gate_helpers import FeatureGateTestMixin
    
    class TestPaymentService(FeatureGateTestMixin):
        def test_payment_execution_with_ramp(self):
            with self.feature_gate_enabled("payment_execution"):
                # Test payment execution functionality
                pass
        
        def test_payment_execution_qbo_only(self):
            with self.feature_gate_disabled("payment_execution"):
                # Test QBO-only mode behavior
                pass
"""

import pytest
from unittest.mock import patch
from typing import Dict, Any, Generator
from infra.config import feature_gates

class FeatureGateTestMixin:
    """Mixin class for testing with feature gates."""
    
    def feature_gate_enabled(self, feature: str) -> Generator[None, None, None]:
        """Context manager to enable a specific feature gate for testing."""
        original_can_use = feature_gates.can_use_feature
        
        def mock_can_use_feature(feature_name: str) -> bool:
            if feature_name == feature:
                return True
            return original_can_use(feature_name)
        
        with patch.object(feature_gates, 'can_use_feature', side_effect=mock_can_use_feature):
            yield
    
    def feature_gate_disabled(self, feature: str) -> Generator[None, None, None]:
        """Context manager to disable a specific feature gate for testing."""
        original_can_use = feature_gates.can_use_feature
        
        def mock_can_use_feature(feature_name: str) -> bool:
            if feature_name == feature:
                return False
            return original_can_use(feature_name)
        
        with patch.object(feature_gates, 'can_use_feature', side_effect=mock_can_use_feature):
            yield
    
    def with_feature_gates(self, gates: Dict[str, bool]) -> Generator[None, None, None]:
        """Context manager to set multiple feature gates for testing."""
        original_can_use = feature_gates.can_use_feature
        
        def mock_can_use_feature(feature_name: str) -> bool:
            if feature_name in gates:
                return gates[feature_name]
            return original_can_use(feature_name)
        
        with patch.object(feature_gates, 'can_use_feature', side_effect=mock_can_use_feature):
            yield

# Pytest markers for feature-gated tests
def pytest_configure(config):
    """Configure pytest with feature gate markers."""
    config.addinivalue_line(
        "markers", "requires_payment_execution: mark test as requiring payment execution"
    )
    config.addinivalue_line(
        "markers", "requires_reserve_management: mark test as requiring reserve management"
    )
    config.addinivalue_line(
        "markers", "requires_multi_rail: mark test as requiring multi-rail functionality"
    )
    config.addinivalue_line(
        "markers", "qbo_only: mark test as QBO-only mode specific"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip feature-gated tests based on current configuration."""
    for item in items:
        # Skip tests that require payment execution if not available
        if item.get_closest_marker("requires_payment_execution"):
            if not feature_gates.can_use_feature("payment_execution"):
                skip_reason = "Payment execution requires Ramp integration"
                item.add_marker(pytest.mark.skip(reason=skip_reason))
        
        # Skip tests that require reserve management if not available
        if item.get_closest_marker("requires_reserve_management"):
            if not feature_gates.can_use_feature("reserve_management"):
                skip_reason = "Reserve management requires Ramp integration"
                item.add_marker(pytest.mark.skip(reason=skip_reason))
        
        # Skip tests that require multi-rail functionality if not available
        if item.get_closest_marker("requires_multi_rail"):
            if not feature_gates.can_use_feature("multi_rail_decisions"):
                skip_reason = "Multi-rail functionality not available"
                item.add_marker(pytest.mark.skip(reason=skip_reason))
        
        # Skip QBO-only tests if not in QBO-only mode
        if item.get_closest_marker("qbo_only"):
            if not feature_gates.can_use_feature("qbo_only_mode"):
                skip_reason = "Test is QBO-only mode specific"
                item.add_marker(pytest.mark.skip(reason=skip_reason))

# Example test decorators
def requires_payment_execution(func):
    """Decorator to mark test as requiring payment execution."""
    return pytest.mark.requires_payment_execution(func)

def requires_reserve_management(func):
    """Decorator to mark test as requiring reserve management."""
    return pytest.mark.requires_reserve_management(func)

def requires_multi_rail(func):
    """Decorator to mark test as requiring multi-rail functionality."""
    return pytest.mark.requires_multi_rail(func)

def qbo_only(func):
    """Decorator to mark test as QBO-only mode specific."""
    return pytest.mark.qbo_only(func)
