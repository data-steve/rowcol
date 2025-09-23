"""
Provider Factories for AP Domain

Environment-driven factory functions for selecting providers.
Follows ADR-002 Mock-First Development Strategy.
"""

import os

from .qbo_provider import QBOAPProvider
from .mock_qbo_provider import MockQBOAPProvider
from .document_processor import DocumentProcessor
from .mock_document_processor import MockDocumentProcessor


def get_qbo_ap_provider(business_id: str) -> QBOAPProvider:
    """
    Get QBO AP provider based on environment configuration.
    
    Environment Variables:
        USE_MOCK_QBO: "true" to use mock provider (default in development)
        ENVIRONMENT: "development", "staging", "production"
        QBO_CLIENT_ID: Required for real QBO provider
        QBO_CLIENT_SECRET: Required for real QBO provider
    
    Args:
        business_id: Business identifier for tenant isolation
        
    Returns:
        QBOAPProvider instance (mock or real based on config)
    """
    use_mock = os.getenv("USE_MOCK_QBO", "true").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    # Always use mock in development unless explicitly disabled
    if environment == "development" and use_mock:
        return MockQBOAPProvider(business_id)
    
    # Use mock if real QBO credentials are not available
    if not os.getenv("QBO_CLIENT_ID") or not os.getenv("QBO_CLIENT_SECRET"):
        return MockQBOAPProvider(business_id)
    
    # Use mock if explicitly requested
    if use_mock:
        return MockQBOAPProvider(business_id)
    
    # Use real QBO provider in production/staging with credentials
    try:
        from .real_qbo_provider import RealQBOAPProvider
        return RealQBOAPProvider(business_id)
    except ImportError:
        # Fall back to mock if real provider not available
        return MockQBOAPProvider(business_id)


def get_document_processor() -> DocumentProcessor:
    """
    Get document processor based on environment configuration.
    
    Environment Variables:
        USE_MOCK_DOCUMENT_PROCESSING: "true" to use mock processor
        ENVIRONMENT: "development", "staging", "production"
        DOCUMENT_PROCESSOR_API_KEY: Required for real processor
    
    Returns:
        DocumentProcessor instance (mock or real based on config)
    """
    use_mock = os.getenv("USE_MOCK_DOCUMENT_PROCESSING", "true").lower() == "true"
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    # Always use mock in development unless explicitly disabled
    if environment == "development" and use_mock:
        return MockDocumentProcessor()
    
    # Use mock if real processor credentials are not available
    if not os.getenv("DOCUMENT_PROCESSOR_API_KEY"):
        return MockDocumentProcessor()
    
    # Use mock if explicitly requested
    if use_mock:
        return MockDocumentProcessor()
    
    # Use real document processor in production/staging with credentials
    try:
        from .real_document_processor import RealDocumentProcessor
        return RealDocumentProcessor()
    except ImportError:
        # Fall back to mock if real processor not available
        return MockDocumentProcessor()


def validate_provider_configuration() -> dict:
    """
    Validate provider configuration and return status.
    
    Returns:
        Dictionary with provider configuration status
    """
    config_status = {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "qbo_provider": "mock",
        "document_processor": "mock",
        "issues": []
    }
    
    # Check QBO configuration
    use_mock_qbo = os.getenv("USE_MOCK_QBO", "true").lower() == "true"
    if not use_mock_qbo:
        if os.getenv("QBO_CLIENT_ID") and os.getenv("QBO_CLIENT_SECRET"):
            config_status["qbo_provider"] = "real"
        else:
            config_status["issues"].append("Real QBO requested but credentials missing")
            config_status["qbo_provider"] = "mock (fallback)"
    
    # Check document processor configuration
    use_mock_docs = os.getenv("USE_MOCK_DOCUMENT_PROCESSING", "true").lower() == "true"
    if not use_mock_docs:
        if os.getenv("DOCUMENT_PROCESSOR_API_KEY"):
            config_status["document_processor"] = "real"
        else:
            config_status["issues"].append("Real document processor requested but API key missing")
            config_status["document_processor"] = "mock (fallback)"
    
    return config_status
