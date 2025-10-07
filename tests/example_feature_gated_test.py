"""
Example Feature-Gated Test

This file demonstrates how to use feature gating in tests to ensure
strategic test execution based on available functionality.

Key principles:
1. Use feature gates to control test execution, not blanket silencing
2. Test both enabled and disabled states of features
3. Document why each test is gated
4. Plan when to enable each test
"""

import pytest
from unittest.mock import Mock, patch
from infra.testing.feature_gate_helpers import (
    FeatureGateTestMixin, 
    requires_payment_execution, 
    requires_reserve_management,
    qbo_only
)
from infra.config import feature_gates
from domains.ap.services.payment import PaymentService

class TestPaymentServiceFeatureGating(FeatureGateTestMixin):
    """Test PaymentService with feature gating."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock()
        self.business_id = "test_business"
        self.payment_service = PaymentService(self.db, self.business_id)
    
    def test_payment_execution_with_ramp_enabled(self):
        """Test payment execution when Ramp is enabled."""
        with self.feature_gate_enabled("payment_execution"):
            # Test that payment execution works with Ramp
            payment = Mock()
            payment.payment_id = "test_payment"
            payment.amount = 100.00
            payment.status = "PENDING"
            
            # Mock the smart_sync to avoid actual QBO calls
            with patch.object(self.payment_service, 'smart_sync') as mock_sync:
                mock_sync.sync_payment_record.return_value = {"Payment": {"Id": "qbo_123"}}
                
                # This should execute via Ramp (simulated)
                result = self.payment_service.execute_payment(payment)
                
                # Verify payment was marked as executed
                assert payment.status == "EXECUTED"
                assert payment.confirmation_number == "RAMP-test_payment"
    
    def test_payment_execution_qbo_only_mode(self):
        """Test payment behavior in QBO-only mode."""
        with self.feature_gate_disabled("payment_execution"):
            payment = Mock()
            payment.payment_id = "test_payment"
            payment.amount = 100.00
            payment.status = "PENDING"
            
            # Mock the smart_sync to avoid actual QBO calls
            with patch.object(self.payment_service, 'smart_sync') as mock_sync:
                mock_sync.sync_payment_record.return_value = {"Payment": {"Id": "qbo_123"}}
                
                # This should sync to QBO but not execute
                result = self.payment_service.execute_payment(payment)
                
                # Verify payment remains pending (external execution required)
                assert payment.status == "PENDING"
                assert payment.confirmation_number == "PENDING-test_payment"
                assert payment.qbo_payment_id == "qbo_123"
    
    @requires_payment_execution
    def test_payment_workflow_with_execution(self):
        """Test complete payment workflow when execution is available.
        
        This test will be skipped if payment execution is not available.
        """
        # Test the full payment workflow including execution
        payment = Mock()
        payment.payment_id = "test_payment"
        payment.amount = 100.00
        payment.status = "PENDING"
        
        with patch.object(self.payment_service, 'smart_sync'):
            result = self.payment_service.execute_payment_workflow(1)
            # Assertions for full workflow with execution
            assert result is not None
    
    @qbo_only
    def test_qbo_only_mode_limitations(self):
        """Test QBO-only mode limitations.
        
        This test will be skipped if not in QBO-only mode.
        """
        # Test that QBO-only mode has expected limitations
        assert feature_gates.can_use_feature("qbo_only_mode")
        assert not feature_gates.can_use_feature("payment_execution")
        assert not feature_gates.can_use_feature("reserve_management")
    
    def test_feature_gate_combinations(self):
        """Test different combinations of feature gates."""
        # Test with multiple gates enabled
        with self.with_feature_gates({
            "payment_execution": True,
            "reserve_management": True,
            "multi_rail_decisions": True
        }):
            assert feature_gates.can_use_feature("payment_execution")
            assert feature_gates.can_use_feature("reserve_management")
            assert feature_gates.can_use_feature("multi_rail_decisions")
        
        # Test with only QBO enabled
        with self.with_feature_gates({
            "qbo_sync": True,
            "payment_execution": False,
            "reserve_management": False
        }):
            assert feature_gates.can_use_feature("qbo_sync")
            assert not feature_gates.can_use_feature("payment_execution")
            assert not feature_gates.can_use_feature("reserve_management")

class TestReserveServiceFeatureGating(FeatureGateTestMixin):
    """Test ReserveService with feature gating."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock()
        self.business_id = "test_business"
        from runway.services.0_data_orchestrators.reserve_runway import RunwayReserveService
        self.reserve_service = RunwayReserveService(self.db, self.business_id)
    
    def test_reserve_creation_with_ramp_enabled(self):
        """Test reserve creation when Ramp is enabled."""
        with self.feature_gate_enabled("reserve_management"):
            from runway.schemas.runway_reserve import RunwayReserveCreate
            reserve_data = RunwayReserveCreate(
                business_id=self.business_id,
                name="Test Reserve",
                description="Test reserve for feature gating",
                reserve_type="operational",
                target_amount=10000.00
            )
            
            # This should work with Ramp enabled
            with patch.object(self.reserve_service.db, 'add') as mock_add:
                result = self.reserve_service.create_reserve(reserve_data)
                mock_add.assert_called_once()
    
    def test_reserve_creation_qbo_only_mode(self):
        """Test reserve creation fails in QBO-only mode."""
        with self.feature_gate_disabled("reserve_management"):
            from runway.schemas.runway_reserve import RunwayReserveCreate
            reserve_data = RunwayReserveCreate(
                business_id=self.business_id,
                name="Test Reserve",
                description="Test reserve for feature gating",
                reserve_type="operational",
                target_amount=10000.00
            )
            
            # This should raise an error in QBO-only mode
            with pytest.raises(Exception) as exc_info:
                self.reserve_service.create_reserve(reserve_data)
            
            assert "Reserve management requires Ramp integration" in str(exc_info.value)
    
    @requires_reserve_management
    def test_reserve_operations(self):
        """Test reserve operations when reserve management is available.
        
        This test will be skipped if reserve management is not available.
        """
        # Test reserve funding, allocation, and utilization
        # These operations require Ramp integration
        pass

# Example of how to run tests with specific feature gates
class TestFeatureGateConfiguration:
    """Test feature gate configuration and behavior."""
    
    def test_qbo_only_mode_detection(self):
        """Test QBO-only mode detection."""
        # Test current configuration
        if feature_gates.can_use_feature("qbo_only_mode"):
            assert feature_gates.can_use_feature("qbo_sync")
            assert not feature_gates.can_use_feature("payment_execution")
            assert not feature_gates.can_use_feature("reserve_management")
    
    def test_available_payment_methods(self):
        """Test available payment methods based on feature gates."""
        methods = feature_gates.get_available_payment_methods()
        
        if feature_gates.can_use_feature("qbo_only_mode"):
            assert "qbo_sync" in methods
            assert "ach" not in methods
        elif feature_gates.can_use_feature("payment_execution"):
            assert "ach" in methods
            assert "wire" in methods
    
    def test_available_data_sources(self):
        """Test available data sources based on feature gates."""
        sources = feature_gates.get_available_data_sources()
        
        if feature_gates.can_use_feature("qbo_only_mode"):
            assert "qbo" in sources
            assert "ramp" not in sources
        elif feature_gates.can_use_feature("multi_rail_decisions"):
            assert "qbo" in sources
            # Additional sources depend on configuration
