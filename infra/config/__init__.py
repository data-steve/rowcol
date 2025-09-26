"""
Business Rules - Centralized business logic parameters

This module provides centralized access to all business rules while maintaining
clear domain separation and preventing both bloat and buried magic numbers.

Architecture follows ADR-005: Business logic parameters belong in dedicated 
rule classes, not buried in service implementations.
"""

# Core system thresholds (runway, data quality, etc.)
from .core_thresholds import (
    RunwayAnalysisSettings,
    RunwayThresholds, 
    DataQualityThresholds,
    ProofOfValueThresholds,
    # Legacy classes (TODO: Move to appropriate domain rules)
    TrayPriorities,
    DigestSettings,
    EmailSettings,
    QBOSettings,
    OnboardingSettings,
    TrayItemTypes,
    TrayItemStatuses,
    BusinessStatuses,
    IntegrationStatuses,
    DocumentSettings,
    AdjustmentSettings
)

# Domain-specific business rules
from .collections_rules import CollectionsRules
from .payment_rules import PaymentRules  
from .risk_assessment_rules import RiskAssessmentRules
from .communication_rules import CommunicationRules

__all__ = [
    # Core thresholds
    "RunwayAnalysisSettings",
    "RunwayThresholds",
    "DataQualityThresholds", 
    "ProofOfValueThresholds",
    
    # Domain rules
    "CollectionsRules",
    "PaymentRules",
    "RiskAssessmentRules", 
    "CommunicationRules",
    
    # Legacy classes (TODO: Move to appropriate domain rules)
    "TrayPriorities",
    "DigestSettings",
    "EmailSettings",
    "QBOSettings",
    "OnboardingSettings",
    "TrayItemTypes",
    "TrayItemStatuses",
    "BusinessStatuses",
    "IntegrationStatuses",
    "DocumentSettings",
    "AdjustmentSettings"
]
