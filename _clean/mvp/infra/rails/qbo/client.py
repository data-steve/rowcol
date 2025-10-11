"""
Raw QBO HTTP Client

This module provides raw HTTP calls to QBO endpoints with no business logic.
Just HTTP requests to QBO API - no orchestration, no caching, no retry logic.

Key Principles:
- Raw HTTP calls only
- No business logic
- No orchestration
- No caching
- No retry logic
- Just HTTP requests to QBO endpoints
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .config import qbo_config
from .auth import QBOAuthService

logger = logging.getLogger(__name__)


class QBORawClient:
    """
    Raw QBO HTTP client that only makes HTTP calls to QBO endpoints.
    
    This client provides no business logic, orchestration, caching, or retry logic.
    It's just HTTP requests to QBO API endpoints.
    """
    
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.business_id = business_id
        self.realm_id = realm_id
        self.base_url = f"{qbo_config.api_base_url}/{realm_id}"
        self.db_session = db_session
        
        # Get auth service for token management
        self.auth_service = QBOAuthService(business_id) if business_id else None
        
        logger.info(f"Initialized QBORawClient for business {business_id}, realm {realm_id}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for QBO API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Get access token if auth service is available
        if self.auth_service:
            try:
                access_token = self.auth_service.get_valid_access_token()
                if access_token:
                    headers["Authorization"] = f"Bearer {access_token}"
                    logger.debug(f"Using access token: {access_token[:20]}...")
                else:
                    logger.warning(f"No valid access token for business {self.business_id}")
            except Exception as e:
                logger.error(f"Failed to get access token: {e}")
        else:
            logger.warning("No auth service available - requests will fail")
        
        return headers
        
    def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to QBO API endpoint."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to QBO API endpoint."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request to QBO API endpoint."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to QBO API endpoint."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
  