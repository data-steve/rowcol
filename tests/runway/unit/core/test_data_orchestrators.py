"""
Unit tests for Data Orchestrator Pattern implementation
Tests the core functionality without database dependencies
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from runway.core.data_orchestrators.hygiene_tray_data_orchestrator import HygieneTrayDataOrchestrator
from runway.core.data_orchestrators.decision_console_data_orchestrator import DecisionConsoleDataOrchestrator
from runway.core.runway_calculation_service import RunwayCalculationService


class TestHygieneTrayDataOrchestrator:
    """Test HygieneTrayDataOrchestrator functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def orchestrator(self, mock_db):
        """Create orchestrator instance."""
        return HygieneTrayDataOrchestrator(mock_db)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator can be initialized."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'smart_sync')
    
    @pytest.mark.asyncio
    async def test_get_tray_data_structure(self, orchestrator):
        """Test get_tray_data returns correct structure."""
        # Mock SmartSyncService methods
        with patch('runway.core.data_orchestrators.hygiene_tray_data_orchestrator.SmartSyncService') as mock_smart_sync_class:
            mock_smart_sync = AsyncMock()
            mock_smart_sync.get_bills.return_value = {"bills": [{"id": "1", "amount": 100}]}
            mock_smart_sync.get_invoices.return_value = {"invoices": [{"id": "2", "amount": 200}]}
            mock_smart_sync.get_company_info.return_value = {"balances": [{"account": "cash", "balance": 1000}]}
            mock_smart_sync_class.return_value = mock_smart_sync
            
            result = await orchestrator.get_tray_data("test_business")
            
            assert "bills" in result
            assert "invoices" in result
            assert "balances" in result
            assert "business_id" in result
            assert "synced_at" in result
            assert result["business_id"] == "test_business"
    
    @pytest.mark.asyncio
    async def test_get_tray_items_combines_data(self, orchestrator):
        """Test get_tray_items combines bills and invoices."""
        with patch('runway.core.data_orchestrators.hygiene_tray_data_orchestrator.SmartSyncService') as mock_smart_sync_class:
            mock_smart_sync = AsyncMock()
            mock_smart_sync.get_bills.return_value = {"bills": [{"id": "1", "amount": 100}]}
            mock_smart_sync.get_invoices.return_value = {"invoices": [{"id": "2", "amount": 200}]}
            mock_smart_sync.get_company_info.return_value = {"balances": []}
            mock_smart_sync_class.return_value = mock_smart_sync
            
            result = await orchestrator.get_tray_items("test_business")
            
            assert len(result) == 2
            assert any(item["item_type"] == "bill" for item in result)
            assert any(item["item_type"] == "invoice" for item in result)


class TestDecisionConsoleDataOrchestrator:
    """Test DecisionConsoleDataOrchestrator functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def orchestrator(self, mock_db):
        """Create orchestrator instance."""
        return DecisionConsoleDataOrchestrator(mock_db)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator can be initialized."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'smart_sync')
    
    @pytest.mark.asyncio
    async def test_get_console_data_structure(self, orchestrator):
        """Test get_console_data returns correct structure."""
        with patch('runway.core.data_orchestrators.decision_console_data_orchestrator.SmartSyncService') as mock_smart_sync_class:
            mock_smart_sync = AsyncMock()
            mock_smart_sync.get_bills.return_value = {"bills": [{"id": "1", "amount": 100}]}
            mock_smart_sync.get_invoices.return_value = {"invoices": [{"id": "2", "amount": 200}]}
            mock_smart_sync.get_company_info.return_value = {"balances": [{"account": "cash", "balance": 1000}]}
            mock_smart_sync_class.return_value = mock_smart_sync
            
            # Mock the decision queue method
            with patch.object(orchestrator, '_get_decision_queue', return_value=[]):
                result = await orchestrator.get_console_data("test_business")
                
                assert "bills" in result
                assert "invoices" in result
                assert "balances" in result
                assert "decision_queue" in result
                assert "business_id" in result
                assert "synced_at" in result
                assert result["business_id"] == "test_business"
    
    @pytest.mark.asyncio
    async def test_add_decision(self, orchestrator):
        """Test adding a decision to the queue."""
        with patch.object(orchestrator, '_store_decision') as mock_store:
            with patch.object(orchestrator, 'get_console_data', return_value={"decisions": []}) as mock_get:
                result = await orchestrator.add_decision("test_business", {"action": "pay_bill"})
                
                mock_store.assert_called_once_with("test_business", {"action": "pay_bill"})
                mock_get.assert_called_once_with("test_business")
                assert result == {"decisions": []}


class TestRunwayCalculationServicePureCalculation:
    """Test RunwayCalculationService as pure calculation service."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def calculator(self, mock_db):
        """Create calculator instance."""
        return RunwayCalculationService(mock_db, "test_business")
    
    def test_initialization(self, calculator):
        """Test calculator can be initialized."""
        assert calculator is not None
        assert not hasattr(calculator, 'smart_sync')  # Should not have smart_sync
    
    def test_calculate_current_runway_requires_data(self, calculator):
        """Test calculate_current_runway requires qbo_data parameter."""
        test_data = {
            "bills": [{"amount": 100, "status": "unpaid"}],
            "invoices": [{"amount": 200, "status": "unpaid"}],
            "balances": [{"account": "cash", "balance": 1000}]
        }
        
        result = calculator.calculate_current_runway(test_data)
        
        assert "business_id" in result
        assert "calculated_at" in result
        assert "cash_position" in result
        assert "base_runway_days" in result
    
    def test_calculate_current_runway_without_data_raises_error(self, calculator):
        """Test calculate_current_runway raises error without data."""
        with pytest.raises(ValueError, match="qbo_data is required"):
            calculator.calculate_current_runway(None)
    
    def test_calculate_scenario_impact_requires_data(self, calculator):
        """Test calculate_scenario_impact requires qbo_data parameter."""
        test_data = {
            "bills": [{"amount": 100, "status": "unpaid"}],
            "invoices": [{"amount": 200, "status": "unpaid"}],
            "balances": [{"account": "cash", "balance": 1000}]
        }
        
        scenario = {"type": "delay_payment", "amount": 50}
        
        result = calculator.calculate_scenario_impact(scenario, test_data)
        
        assert "scenario_name" in result
        assert "runway_impact_days" in result


class TestDataOrchestratorIntegration:
    """Test integration between orchestrators and RunwayCalculationService."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()
    
    @pytest.mark.asyncio
    async def test_tray_orchestrator_with_runway_calculator(self, mock_db):
        """Test that tray orchestrator data works with RunwayCalculationService."""
        tray_orchestrator = HygieneTrayDataOrchestrator(mock_db)
        runway_calculator = RunwayCalculationService(mock_db, "test_business")
        
        with patch('runway.core.data_orchestrators.hygiene_tray_data_orchestrator.SmartSyncService') as mock_smart_sync_class:
            mock_smart_sync = AsyncMock()
            mock_smart_sync.get_bills.return_value = {"bills": [{"amount": 100, "status": "unpaid"}]}
            mock_smart_sync.get_invoices.return_value = {"invoices": [{"amount": 200, "status": "unpaid"}]}
            mock_smart_sync.get_company_info.return_value = {"balances": [{"account": "cash", "balance": 1000}]}
            mock_smart_sync_class.return_value = mock_smart_sync
            
            # Get data from orchestrator
            tray_data = await tray_orchestrator.get_tray_data("test_business")
            
            # Use data with RunwayCalculationService
            runway_result = runway_calculator.calculate_current_runway(tray_data)
            
            assert runway_result["business_id"] == "test_business"
            assert "base_runway_days" in runway_result
