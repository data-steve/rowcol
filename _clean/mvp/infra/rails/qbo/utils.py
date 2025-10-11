"""
QBO Utilities - Centralized QBO-specific utility functions

Common utility functions for QBO data processing:
- Date parsing and formatting
- Data validation and transformation
- QBO-specific data type conversions
- Error handling for QBO API responses

This centralizes QBO utility functions that were scattered across services.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QBOUtils:
    """Centralized utility functions for QBO data processing."""
    
    @staticmethod
    def parse_qbo_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse QBO date string to datetime.
        
        Handles common QBO date formats:
        - "2024-01-15" (ISO date)
        - "2024-01-15T10:30:00" (ISO datetime)
        - "2024-01-15T10:30:00Z" (ISO datetime with timezone)
        
        Args:
            date_str: QBO date string to parse
            
        Returns:
            datetime object if successful, None otherwise
        """
        if not date_str:
            return None
        
        # Common QBO date formats to try
        date_formats = [
            "%Y-%m-%d",                    # 2024-01-15
            "%Y-%m-%dT%H:%M:%S",          # 2024-01-15T10:30:00
            "%Y-%m-%dT%H:%M:%SZ",         # 2024-01-15T10:30:00Z
            "%Y-%m-%dT%H:%M:%S.%f",       # 2024-01-15T10:30:00.123456
            "%Y-%m-%dT%H:%M:%S.%fZ",      # 2024-01-15T10:30:00.123456Z
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse QBO date: {date_str}")
        return None
    
    @staticmethod
    def format_qbo_date(dt: datetime) -> str:
        """
        Format datetime to QBO-compatible date string.
        
        Args:
            dt: datetime object to format
            
        Returns:
            QBO-compatible date string (YYYY-MM-DD)
        """
        return dt.strftime("%Y-%m-%d")
    
    @staticmethod
    def format_qbo_datetime(dt: datetime) -> str:
        """
        Format datetime to QBO-compatible datetime string.
        
        Args:
            dt: datetime object to format
            
        Returns:
            QBO-compatible datetime string (YYYY-MM-DDTHH:MM:SS)
        """
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    @staticmethod
    def validate_qbo_date_string(date_str: str) -> bool:
        """
        Validate if a string is a valid QBO date format.
        
        Args:
            date_str: String to validate
            
        Returns:
            True if valid QBO date format, False otherwise
        """
        return QBOUtils.parse_qbo_date(date_str) is not None
    
    @staticmethod
    def extract_qbo_entity_id(entity_ref: Dict[str, Any]) -> Optional[str]:
        """
        Extract entity ID from QBO entity reference.
        
        Args:
            entity_ref: QBO entity reference dict (e.g., VendorRef, CustomerRef)
            
        Returns:
            Entity ID if found, None otherwise
        """
        if not entity_ref or not isinstance(entity_ref, dict):
            return None
        
        return entity_ref.get("value")
    
    @staticmethod
    def extract_qbo_entity_name(entity_ref: Dict[str, Any]) -> Optional[str]:
        """
        Extract entity name from QBO entity reference.
        
        Args:
            entity_ref: QBO entity reference dict (e.g., VendorRef, CustomerRef)
            
        Returns:
            Entity name if found, None otherwise
        """
        if not entity_ref or not isinstance(entity_ref, dict):
            return None
        
        return entity_ref.get("name")
    
    @staticmethod
    def create_qbo_entity_ref(entity_id: str, entity_name: str = None) -> Dict[str, Any]:
        """
        Create QBO entity reference dict.
        
        Args:
            entity_id: QBO entity ID
            entity_name: Optional entity name
            
        Returns:
            QBO entity reference dict
        """
        ref = {"value": entity_id}
        if entity_name:
            ref["name"] = entity_name
        return ref
    
    @staticmethod
    def safe_qbo_amount(amount: Any) -> float:
        """
        Safely convert QBO amount to float.
        
        Args:
            amount: QBO amount value (could be string, int, float, or None)
            
        Returns:
            Float amount, 0.0 if conversion fails
        """
        if amount is None:
            return 0.0
        
        try:
            return float(amount)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert QBO amount to float: {amount}")
            return 0.0
    
    @staticmethod
    def safe_qbo_int(value: Any) -> int:
        """
        Safely convert QBO value to int.
        
        Args:
            value: QBO value (could be string, int, float, or None)
            
        Returns:
            Int value, 0 if conversion fails
        """
        if value is None:
            return 0
        
        try:
            return int(float(value))  # Convert to float first to handle "123.0"
        except (ValueError, TypeError):
            logger.warning(f"Could not convert QBO value to int: {value}")
            return 0
    
    @staticmethod
    def clean_qbo_string(value: Any) -> Optional[str]:
        """
        Clean and validate QBO string value.
        
        Args:
            value: QBO string value
            
        Returns:
            Cleaned string, None if invalid
        """
        if value is None:
            return None
        
        if not isinstance(value, str):
            value = str(value)
        
        # Remove leading/trailing whitespace
        cleaned = value.strip()
        
        # Return None for empty strings
        return cleaned if cleaned else None
    
    @staticmethod
    def is_qbo_error_response(response: Dict[str, Any]) -> bool:
        """
        Check if QBO API response contains an error.
        
        Args:
            response: QBO API response dict
            
        Returns:
            True if response contains error, False otherwise
        """
        if not response or not isinstance(response, dict):
            return True
        
        # Check for common QBO error indicators
        error_indicators = [
            "Fault",
            "Error",
            "error",
            "errors",
            "ErrorCode",
            "ErrorMessage"
        ]
        
        return any(indicator in response for indicator in error_indicators)
    
    @staticmethod
    def extract_qbo_error_message(response: Dict[str, Any]) -> Optional[str]:
        """
        Extract error message from QBO API response.
        
        Args:
            response: QBO API response dict
            
        Returns:
            Error message if found, None otherwise
        """
        if not QBOUtils.is_qbo_error_response(response):
            return None
        
        # Try different error message locations
        error_locations = [
            "Fault.Error.0.Message",
            "Error.Message",
            "ErrorMessage",
            "error.message",
            "errors.0.message"
        ]
        
        for location in error_locations:
            try:
                # Navigate nested dict structure
                parts = location.split(".")
                value = response
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                
                if value and isinstance(value, str):
                    return value
            except (KeyError, TypeError, AttributeError):
                continue
        
        return "Unknown QBO error"
