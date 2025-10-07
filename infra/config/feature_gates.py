"""
Feature Gates - Control access to multi-rail functionality

This module provides centralized feature gating for different integration rails
and product capabilities. Follows the same pattern as other config modules.

Architecture follows ADR-005: Feature gates belong in dedicated config classes,
not buried in service implementations.
"""

import os
from typing import Dict, Any, List
from enum import Enum

class IntegrationRail(Enum):
    """Supported integration rails."""
    QBO = "qbo"
    RAMP = "ramp" 
    PLAID = "plaid"
    STRIPE = "stripe"

class FeatureGateSettings:
    """Feature gate configuration for different integration rails."""
    
    def __init__(self):
        # Environment-based feature flags
        self.enable_qbo = os.getenv("ENABLE_QBO_INTEGRATION", "true").lower() == "true"
        self.enable_ramp = os.getenv("ENABLE_RAMP_INTEGRATION", "false").lower() == "true"
        self.enable_plaid = os.getenv("ENABLE_PLAID_INTEGRATION", "false").lower() == "true"
        self.enable_stripe = os.getenv("ENABLE_STRIPE_INTEGRATION", "false").lower() == "true"
        
        # Product capability flags (derived from enabled rails)
        self.enable_reserve_management = self.enable_ramp  # Requires Ramp
        self.enable_payment_execution = self.enable_ramp  # Requires Ramp
        self.enable_multi_rail_hygiene = self.enable_ramp or self.enable_plaid
        self.enable_multi_rail_decisions = self.enable_ramp or self.enable_plaid or self.enable_stripe
        
        # QBO-only mode (QBO enabled, no other rails)
        self.is_qbo_only_mode = self.enable_qbo and not any([self.enable_ramp, self.enable_plaid, self.enable_stripe])
    
    def is_rail_enabled(self, rail: IntegrationRail) -> bool:
        """Check if a specific integration rail is enabled."""
        rail_map = {
            IntegrationRail.QBO: self.enable_qbo,
            IntegrationRail.RAMP: self.enable_ramp,
            IntegrationRail.PLAID: self.enable_plaid,
            IntegrationRail.STRIPE: self.enable_stripe
        }
        return rail_map.get(rail, False)
    
    def can_use_feature(self, feature: str) -> bool:
        """Check if a specific feature can be used based on enabled rails."""
        feature_requirements = {
            # Core features
            "qbo_sync": self.enable_qbo,
            "qbo_read_only": self.enable_qbo,
            
            # Payment execution (requires Ramp)
            "payment_execution": self.enable_ramp,
            "immediate_payment": self.enable_ramp,
            "scheduled_payment_execution": self.enable_ramp,
            
            # Reserve management (requires Ramp)
            "reserve_management": self.enable_ramp,
            "runway_reserves": self.enable_ramp,
            
            # Multi-rail features
            "multi_rail_hygiene": self.enable_multi_rail_hygiene,
            "multi_rail_decisions": self.enable_multi_rail_decisions,
            "multi_rail_data_sources": self.enable_multi_rail_decisions,
            
            # QBO-only mode features
            "qbo_only_mode": self.is_qbo_only_mode,
            "qbo_bill_approval": self.enable_qbo,  # Always available with QBO
            "qbo_scheduled_payment_sync": self.enable_qbo,  # Sync only, no execution
            
            # Data source features
            "ramp_data": self.enable_ramp,
            "plaid_data": self.enable_plaid,
            "stripe_data": self.enable_stripe,
        }
        return feature_requirements.get(feature, False)
    
    def get_enabled_rails(self) -> List[IntegrationRail]:
        """Get list of currently enabled integration rails."""
        enabled = []
        for rail in IntegrationRail:
            if self.is_rail_enabled(rail):
                enabled.append(rail)
        return enabled
    
    def get_available_payment_methods(self) -> List[str]:
        """Get available payment methods based on enabled rails."""
        methods = []
        
        if self.enable_qbo:
            methods.extend(["qbo_sync"])  # QBO can sync payment records
        
        if self.enable_ramp:
            methods.extend(["ach", "wire", "check"])  # Ramp can execute payments
        
        if self.enable_stripe:
            methods.extend(["card", "ach"])  # Stripe can process cards and ACH
        
        return methods
    
    def get_available_data_sources(self) -> List[str]:
        """Get available data sources based on enabled rails."""
        sources = []
        
        if self.enable_qbo:
            sources.append("qbo")
        
        if self.enable_ramp:
            sources.append("ramp")
        
        if self.enable_plaid:
            sources.append("plaid")
        
        if self.enable_stripe:
            sources.append("stripe")
        
        return sources
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging/logging."""
        return {
            "qbo_enabled": self.enable_qbo,
            "ramp_enabled": self.enable_ramp,
            "plaid_enabled": self.enable_plaid,
            "stripe_enabled": self.enable_stripe,
            "reserve_management_enabled": self.enable_reserve_management,
            "payment_execution_enabled": self.enable_payment_execution,
            "is_qbo_only_mode": self.is_qbo_only_mode,
            "enabled_rails": [rail.value for rail in self.get_enabled_rails()],
            "available_payment_methods": self.get_available_payment_methods(),
            "available_data_sources": self.get_available_data_sources()
        }

# Global feature gate instance
feature_gates = FeatureGateSettings()
