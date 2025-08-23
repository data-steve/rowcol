"""
Unit tests for PolicyEngineService ServicePro Rules

Tests the ServicePro-specific business rules for contractor expense categorization.
"""

import pytest
from unittest.mock import Mock
from domains.policy.services.policy_engine import PolicyEngineService


class TestPolicyEngineServicePro:
    """Unit tests for ServicePro-specific policy engine functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db = Mock()
        # Mock the query chain for PolicyRuleTemplate
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        # Mock the query chain for VendorCategory  
        db.query.return_value.filter.return_value.first.return_value = None
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        """PolicyEngineService instance with mocked database."""
        return PolicyEngineService(mock_db)
    
    def test_get_servicepro_rules_structure(self, service):
        """Test that ServicePro rules have correct structure."""
        rules = service.get_servicepro_rules("firm_001")
        
        assert len(rules) > 0
        
        # Check rule structure
        for rule in rules:
            assert "rule_name" in rule
            assert "pattern" in rule
            assert "match_type" in rule
            assert "confidence" in rule
            assert "actions" in rule
            assert "vendor_keywords" in rule
            assert "amount_range" in rule
            
            # Check actions structure
            actions = rule["actions"]
            assert "default_account" in actions
            assert "category" in actions
            
            # Confidence should be reasonable
            assert 0.0 <= rule["confidence"] <= 1.0
    
    def test_home_depot_materials_rule(self, service):
        """Test Home Depot materials categorization."""
        txn = {
            "description": "HOME DEPOT STORE #1234",
            "vendor_name": "Home Depot",
            "amount": 450.00,
            "memo": "Mulch and plants for Smith job"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "5000-Materials"
        assert result["confidence"] >= 0.85
        assert result["category"] == "Materials & Supplies"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_job_size"
        assert "Home Depot Materials" in result["rule_name"]
    
    def test_fuel_reimbursements_rule(self, service):
        """Test fuel expense categorization."""
        txn = {
            "description": "SHELL GAS STATION #5678",
            "vendor_name": "Shell",
            "amount": 85.50,
            "memo": "Fuel for crew truck"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "5400-Vehicle Expenses"
        assert result["confidence"] >= 0.85
        assert result["category"] == "Fuel & Transportation"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_crew_hours"
        assert "Fuel Reimbursements" in result["rule_name"]
    
    def test_hvac_equipment_rule(self, service):
        """Test HVAC equipment categorization."""
        txn = {
            "description": "HVAC Supply Co - Furnace Unit",
            "vendor_name": "Carrier HVAC Supply",
            "amount": 3200.00,
            "memo": "New furnace for Johnson project"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "5000-Materials"
        assert result["confidence"] >= 0.85
        assert result["category"] == "HVAC Equipment"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_job_size"
    
    def test_equipment_rental_rule(self, service):
        """Test equipment rental categorization."""
        txn = {
            "description": "UNITED RENTALS - Excavator",
            "vendor_name": "United Rentals",
            "amount": 450.00,
            "memo": "Excavator rental for foundation work"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "5200-Equipment Rental"
        assert result["confidence"] >= 0.75
        assert result["category"] == "Equipment Rental"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_usage_days"
    
    def test_subcontractor_services_rule(self, service):
        """Test subcontractor services categorization."""
        txn = {
            "description": "ABC Licensed Electrical Contractors",
            "vendor_name": "ABC Electrical",
            "amount": 2800.00,
            "memo": "Electrical work for commercial project"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "6000-Subcontractor Services"
        assert result["confidence"] >= 0.85
        assert result["category"] == "Subcontractor Services"
        assert result["requires_contract"] == True
        assert result["job_allocation"] == "by_job_size"
    
    def test_vehicle_maintenance_rule(self, service):
        """Test vehicle maintenance categorization."""
        txn = {
            "description": "JIFFY LUBE - Oil Change",
            "vendor_name": "Jiffy Lube",
            "amount": 45.00,
            "memo": "Oil change for work truck"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "5400-Vehicle Expenses"
        assert result["confidence"] >= 0.75
        assert result["category"] == "Vehicle Maintenance"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_vehicle_usage"
    
    def test_small_tools_rule(self, service):
        """Test small tools categorization."""
        txn = {
            "description": "HARBOR FREIGHT TOOLS",
            "vendor_name": "Harbor Freight",
            "amount": 125.00,
            "memo": "Drill bits and hand tools"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "5100-Small Tools"
        assert result["confidence"] >= 0.75
        assert result["category"] == "Small Tools"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_job_count"
    
    def test_office_supplies_rule(self, service):
        """Test office supplies categorization."""
        txn = {
            "description": "STAPLES OFFICE SUPPLIES",
            "vendor_name": "Staples",
            "amount": 75.00,
            "memo": "Paper and printer ink"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "6100-Office Supplies"
        assert result["confidence"] >= 0.85
        assert result["category"] == "Office Supplies"
        assert result["requires_receipt"] == True
        assert result["job_allocation"] == "by_job_count"
    
    def test_professional_services_rule(self, service):
        """Test professional services categorization."""
        txn = {
            "description": "SMITH & ASSOCIATES CPA",
            "vendor_name": "Smith CPA",
            "amount": 500.00,
            "memo": "Monthly accounting services"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["account"] == "6200-Professional Services"
        assert result["confidence"] >= 0.85
        assert result["category"] == "Professional Services"
        assert result["requires_invoice"] == True
        assert result["job_allocation"] == "by_job_count"
    
    def test_confidence_calculation_vendor_match(self, service):
        """Test confidence calculation with vendor keyword match."""
        rules = service.get_servicepro_rules("firm_001")
        home_depot_rule = next(r for r in rules if r["rule_name"] == "Home Depot Materials")
        
        # Perfect vendor match
        confidence = service._calculate_servicepro_rule_confidence(
            home_depot_rule,
            "home depot store materials",
            "home depot",
            450.00
        )
        
        # Should get high confidence (pattern + vendor + amount + complexity)
        assert confidence >= 0.85
    
    def test_confidence_calculation_pattern_only(self, service):
        """Test confidence calculation with pattern match only."""
        rules = service.get_servicepro_rules("firm_001")
        fuel_rule = next(r for r in rules if r["rule_name"] == "Fuel Reimbursements")
        
        # Pattern match but no vendor match
        confidence = service._calculate_servicepro_rule_confidence(
            fuel_rule,
            "gas station fuel purchase",
            "unknown vendor",
            85.50
        )
        
        # Should get medium confidence (pattern + amount)
        assert 0.15 <= confidence < 0.9
    
    def test_confidence_calculation_amount_out_of_range(self, service):
        """Test confidence calculation with amount outside expected range."""
        rules = service.get_servicepro_rules("firm_001")
        fuel_rule = next(r for r in rules if r["rule_name"] == "Fuel Reimbursements")
        
        # Amount way outside expected range for fuel
        confidence = service._calculate_servicepro_rule_confidence(
            fuel_rule,
            "shell gas fuel",
            "shell",
            5000.00  # $5000 for fuel is suspicious
        )
        
        # Should get lower confidence (no amount match)
        assert confidence < 0.8
    
    def test_no_match_fallback(self, service, mock_db):
        """Test fallback to general categorization when no ServicePro rules match."""
        # Mock the general categorization method
        mock_suggestion = Mock()
        service.categorize_transaction = Mock(return_value=mock_suggestion)
        
        # Transaction that doesn't match any ServicePro rules
        txn = {
            "description": "RANDOM VENDOR XYZ",
            "vendor_name": "Random Vendor",
            "amount": 123.45,
            "memo": "Some random expense"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        # Should fall back to general categorization
        service.categorize_transaction.assert_called_once_with(txn, "firm_001", None)
        # The result should be a dictionary converted from the mock suggestion
        assert isinstance(result, dict)
        assert "account" in result
        assert "confidence" in result
        assert "category" in result
    
    def test_multiple_pattern_matches_takes_highest_confidence(self, service):
        """Test that when multiple rules match, highest confidence wins."""
        # Transaction that could match both materials and tools
        txn = {
            "description": "HOME DEPOT TOOLS AND MATERIALS",
            "vendor_name": "Home Depot",
            "amount": 200.00,
            "memo": "Tools and materials purchase"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        # Should pick the rule with higher confidence
        # Home Depot Materials rule has higher confidence (0.95) than Small Tools (0.80)
        assert result["category"] == "Materials & Supplies"
        assert result["rule_name"] == "Home Depot Materials"
    
    def test_case_insensitive_matching(self, service):
        """Test that pattern matching is case insensitive."""
        txn = {
            "description": "home depot store",  # lowercase
            "vendor_name": "HOME DEPOT",  # uppercase
            "amount": 300.00,
            "memo": "materials purchase"
        }
        
        result = service.categorize_servicepro_transaction(txn, "firm_001")
        
        assert result["category"] == "Materials & Supplies"
        assert result["confidence"] >= 0.85
    
    def test_text_complexity_bonus(self, service):
        """Test that longer descriptions get complexity bonus."""
        rules = service.get_servicepro_rules("firm_001")
        home_depot_rule = next(r for r in rules if r["rule_name"] == "Home Depot Materials")
        
        # Short description
        short_confidence = service._calculate_servicepro_rule_confidence(
            home_depot_rule,
            "home depot",
            "home depot",
            300.00
        )
        
        # Long description (>50 chars)
        long_confidence = service._calculate_servicepro_rule_confidence(
            home_depot_rule,
            "home depot store #1234 materials purchase for landscaping project including mulch plants and irrigation supplies",
            "home depot",
            300.00
        )
        
        # Long description should get complexity bonus
        assert long_confidence > short_confidence
