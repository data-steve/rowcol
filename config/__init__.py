"""Configuration module for Oodaloo application."""

from .business_rules import (
    RunwayThresholds,
    RunwayAnalysisSettings,
    DataQualityThresholds,
    ProofOfValueThresholds,
    CollectionsRules,
    PaymentRules,
    RiskAssessmentRules,
    CommunicationRules
)

# Legacy imports for backward compatibility
# TODO: Move these to appropriate business rule classes
TrayPriorities = None  # TODO: Create TrayRules class
DigestSettings = None  # TODO: Move to CommunicationRules
EmailSettings = None   # TODO: Move to CommunicationRules
QBOSettings = None     # TODO: Move to IntegrationRules
OnboardingSettings = OnboardingSettings if 'OnboardingSettings' in dir() else None
TrayItemTypes = None   # TODO: Move to TrayRules
TrayItemStatuses = None # TODO: Move to TrayRules
BusinessStatuses = None # TODO: Move to BusinessRules
IntegrationStatuses = None # TODO: Move to IntegrationRules
DocumentSettings = None # TODO: Move to DocumentRules
AdjustmentSettings = None # TODO: Move to AdjustmentRules

__all__ = [
    # Core business rules
    "RunwayThresholds",
    "RunwayAnalysisSettings",
    "DataQualityThresholds", 
    "ProofOfValueThresholds",
    "CollectionsRules",
    "PaymentRules",
    "RiskAssessmentRules",
    "CommunicationRules",
    
    # Legacy (TODO: Migrate to proper rule classes)
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
