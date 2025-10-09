"""
Validation Utilities - Data Validation and Sanitization

Provides comprehensive data validation utilities for business data,
API inputs, and configuration values across the application.

Key Features:
- Business data validation (runway calculations, financial data)
- API input validation and sanitization
- Configuration validation
- Custom validation rules and constraints
- Error reporting with detailed field-level messages
"""

import re
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union, Callable, Type
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from enum import Enum

from infra.config.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    sanitized_data: Optional[Dict[str, Any]] = None


@dataclass
class ValidationRule:
    """A validation rule definition."""
    field: str
    validator: Callable
    error_message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    required: bool = True
    sanitizer: Optional[Callable] = None


class DataValidator:
    """
    Comprehensive data validation utility.
    
    Provides validation for business data, API inputs, and configuration
    with detailed error reporting and data sanitization.
    """
    
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register default validation functions."""
        self.custom_validators.update({
            'business_id': self._validate_business_id,
            'email': self._validate_email,
            'phone': self._validate_phone,
            'currency': self._validate_currency,
            'percentage': self._validate_percentage,
            'date_string': self._validate_date_string,
            'positive_number': self._validate_positive_number,
            'runway_days': self._validate_runway_days,
            'cash_amount': self._validate_cash_amount,
            'account_number': self._validate_account_number,
            'routing_number': self._validate_routing_number,
            'tax_id': self._validate_tax_id,
            'zip_code': self._validate_zip_code,
            'state_code': self._validate_state_code,
        })
    
    def add_validation_rules(self, context: str, rules: List[ValidationRule]):
        """
        Add validation rules for a specific context.
        
        Args:
            context: Context name (e.g., 'business', 'invoice', 'payment')
            rules: List of validation rules
        """
        if context not in self.rules:
            self.rules[context] = []
        self.rules[context].extend(rules)
    
    def validate(self, context: str, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against rules for a specific context.
        
        Args:
            context: Validation context
            data: Data to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        if context not in self.rules:
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        
        errors = []
        warnings = []
        sanitized_data = data.copy()
        
        for rule in self.rules[context]:
            field_value = data.get(rule.field)
            
            # Check if required field is missing
            if rule.required and (field_value is None or field_value == ""):
                error = {
                    'field': rule.field,
                    'message': f"{rule.field} is required",
                    'severity': rule.severity.value,
                    'code': 'REQUIRED_FIELD'
                }
                if rule.severity == ValidationSeverity.ERROR:
                    errors.append(error)
                else:
                    warnings.append(error)
                continue
            
            # Skip validation if field is not required and empty
            if not rule.required and (field_value is None or field_value == ""):
                continue
            
            # Apply sanitization if available
            if rule.sanitizer:
                try:
                    sanitized_value = rule.sanitizer(field_value)
                    sanitized_data[rule.field] = sanitized_value
                    field_value = sanitized_value
                except Exception as e:
                    error = {
                        'field': rule.field,
                        'message': f"Sanitization failed: {str(e)}",
                        'severity': ValidationSeverity.ERROR.value,
                        'code': 'SANITIZATION_ERROR'
                    }
                    errors.append(error)
                    continue
            
            # Apply validation
            try:
                is_valid = rule.validator(field_value)
                if not is_valid:
                    error = {
                        'field': rule.field,
                        'message': rule.error_message,
                        'severity': rule.severity.value,
                        'code': 'VALIDATION_FAILED',
                        'value': field_value
                    }
                    if rule.severity == ValidationSeverity.ERROR:
                        errors.append(error)
                    else:
                        warnings.append(error)
            except Exception as e:
                error = {
                    'field': rule.field,
                    'message': f"Validation error: {str(e)}",
                    'severity': ValidationSeverity.ERROR.value,
                    'code': 'VALIDATION_EXCEPTION',
                    'value': field_value
                }
                errors.append(error)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_data
        )
    
    def validate_business_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate business-related data."""
        return self.validate('business', data)
    
    def validate_financial_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate financial data (invoices, payments, etc.)."""
        return self.validate('financial', data)
    
    def validate_user_input(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate user input data."""
        return self.validate('user_input', data)
    
    # Default validation functions
    def _validate_business_id(self, value: Any) -> bool:
        """Validate business ID format."""
        if not isinstance(value, str):
            return False
        # Business ID should be alphanumeric with hyphens, 8-50 characters
        pattern = r'^[a-zA-Z0-9\-]{8,50}$'
        return bool(re.match(pattern, value))
    
    def _validate_email(self, value: Any) -> bool:
        """Validate email address format."""
        if not isinstance(value, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    def _validate_phone(self, value: Any) -> bool:
        """Validate phone number format."""
        if not isinstance(value, str):
            return False
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', value)
        # Should have 10 or 11 digits
        return len(digits) in [10, 11]
    
    def _validate_currency(self, value: Any) -> bool:
        """Validate currency amount."""
        try:
            if isinstance(value, (int, float)):
                return value >= 0
            if isinstance(value, str):
                # Remove currency symbols and commas
                cleaned = re.sub(r'[^\d.-]', '', value)
                amount = float(cleaned)
                return amount >= 0
            return False
        except (ValueError, TypeError):
            return False
    
    def _validate_percentage(self, value: Any) -> bool:
        """Validate percentage value (0-100)."""
        try:
            if isinstance(value, (int, float)):
                return 0 <= value <= 100
            if isinstance(value, str):
                # Remove % symbol
                cleaned = re.sub(r'[^\d.-]', '', value)
                percentage = float(cleaned)
                return 0 <= percentage <= 100
            return False
        except (ValueError, TypeError):
            return False
    
    def _validate_date_string(self, value: Any) -> bool:
        """Validate date string format (YYYY-MM-DD)."""
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _validate_positive_number(self, value: Any) -> bool:
        """Validate positive number."""
        try:
            if isinstance(value, (int, float)):
                return value > 0
            if isinstance(value, str):
                num = float(value)
                return num > 0
            return False
        except (ValueError, TypeError):
            return False
    
    def _validate_runway_days(self, value: Any) -> bool:
        """Validate runway days (0-3650)."""
        try:
            if isinstance(value, (int, float)):
                return 0 <= value <= 3650
            if isinstance(value, str):
                days = float(value)
                return 0 <= days <= 3650
            return False
        except (ValueError, TypeError):
            return False
    
    def _validate_cash_amount(self, value: Any) -> bool:
        """Validate cash amount (can be negative for overdraft)."""
        try:
            if isinstance(value, (int, float)):
                return True  # Any numeric value is valid for cash
            if isinstance(value, str):
                # Remove currency symbols and commas
                cleaned = re.sub(r'[^\d.-]', '', value)
                float(cleaned)  # Just check if it's a valid number
                return True
            return False
        except (ValueError, TypeError):
            return False
    
    def _validate_account_number(self, value: Any) -> bool:
        """Validate bank account number."""
        if not isinstance(value, str):
            return False
        # Account numbers are typically 4-17 digits
        digits = re.sub(r'\D', '', value)
        return 4 <= len(digits) <= 17
    
    def _validate_routing_number(self, value: Any) -> bool:
        """Validate bank routing number."""
        if not isinstance(value, str):
            return False
        # Routing numbers are exactly 9 digits
        digits = re.sub(r'\D', '', value)
        return len(digits) == 9
    
    def _validate_tax_id(self, value: Any) -> bool:
        """Validate tax ID (SSN or EIN format)."""
        if not isinstance(value, str):
            return False
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', value)
        # SSN: 9 digits, EIN: 9 digits
        return len(digits) == 9
    
    def _validate_zip_code(self, value: Any) -> bool:
        """Validate US ZIP code."""
        if not isinstance(value, str):
            return False
        # US ZIP: 5 digits or 5+4 format
        pattern = r'^\d{5}(-\d{4})?$'
        return bool(re.match(pattern, value))
    
    def _validate_state_code(self, value: Any) -> bool:
        """Validate US state code."""
        if not isinstance(value, str):
            return False
        # Two-letter state codes
        valid_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC'
        }
        return value.upper() in valid_states


class BusinessDataValidator(DataValidator):
    """
    Specialized validator for business data.
    
    Pre-configured with business-specific validation rules.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_business_rules()
    
    def _setup_business_rules(self):
        """Set up business-specific validation rules."""
        business_rules = [
            ValidationRule(
                field='business_id',
                validator=self.custom_validators['business_id'],
                error_message='Business ID must be 8-50 alphanumeric characters with hyphens',
                required=True
            ),
            ValidationRule(
                field='name',
                validator=lambda x: isinstance(x, str) and 1 <= len(x) <= 200,
                error_message='Business name must be 1-200 characters',
                required=True,
                sanitizer=lambda x: x.strip() if isinstance(x, str) else x
            ),
            ValidationRule(
                field='email',
                validator=self.custom_validators['email'],
                error_message='Valid email address required',
                required=True,
                sanitizer=lambda x: x.lower().strip() if isinstance(x, str) else x
            ),
            ValidationRule(
                field='phone',
                validator=self.custom_validators['phone'],
                error_message='Valid phone number required',
                required=False,
                sanitizer=lambda x: re.sub(r'\D', '', str(x)) if x else x
            ),
            ValidationRule(
                field='address',
                validator=lambda x: isinstance(x, str) and 1 <= len(x) <= 500,
                error_message='Address must be 1-500 characters',
                required=False,
                sanitizer=lambda x: x.strip() if isinstance(x, str) else x
            ),
            ValidationRule(
                field='city',
                validator=lambda x: isinstance(x, str) and 1 <= len(x) <= 100,
                error_message='City must be 1-100 characters',
                required=False,
                sanitizer=lambda x: x.strip().title() if isinstance(x, str) else x
            ),
            ValidationRule(
                field='state',
                validator=self.custom_validators['state_code'],
                error_message='Valid US state code required',
                required=False,
                sanitizer=lambda x: x.upper().strip() if isinstance(x, str) else x
            ),
            ValidationRule(
                field='zip_code',
                validator=self.custom_validators['zip_code'],
                error_message='Valid US ZIP code required',
                required=False
            ),
            ValidationRule(
                field='tax_id',
                validator=self.custom_validators['tax_id'],
                error_message='Valid tax ID required',
                required=False,
                sanitizer=lambda x: re.sub(r'\D', '', str(x)) if x else x
            )
        ]
        
        self.add_validation_rules('business', business_rules)


class FinancialDataValidator(DataValidator):
    """
    Specialized validator for financial data.
    
    Pre-configured with financial-specific validation rules.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_financial_rules()
    
    def _setup_financial_rules(self):
        """Set up financial-specific validation rules."""
        financial_rules = [
            ValidationRule(
                field='amount',
                validator=self.custom_validators['currency'],
                error_message='Amount must be a valid currency value',
                required=True,
                sanitizer=lambda x: self._sanitize_currency(x)
            ),
            ValidationRule(
                field='runway_days',
                validator=self.custom_validators['runway_days'],
                error_message='Runway days must be between 0 and 3650',
                required=False
            ),
            ValidationRule(
                field='burn_rate',
                validator=self.custom_validators['currency'],
                error_message='Burn rate must be a valid currency value',
                required=False,
                sanitizer=lambda x: self._sanitize_currency(x)
            ),
            ValidationRule(
                field='cash_position',
                validator=self.custom_validators['cash_amount'],
                error_message='Cash position must be a valid amount',
                required=False,
                sanitizer=lambda x: self._sanitize_currency(x)
            ),
            ValidationRule(
                field='due_date',
                validator=self.custom_validators['date_string'],
                error_message='Due date must be in YYYY-MM-DD format',
                required=False
            ),
            ValidationRule(
                field='invoice_number',
                validator=lambda x: isinstance(x, str) and 1 <= len(x) <= 50,
                error_message='Invoice number must be 1-50 characters',
                required=False,
                sanitizer=lambda x: x.strip() if isinstance(x, str) else x
            )
        ]
        
        self.add_validation_rules('financial', financial_rules)
    
    def _sanitize_currency(self, value: Any) -> float:
        """Sanitize currency value to float."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols, commas, and spaces
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned)
        raise ValueError(f"Cannot convert {type(value)} to currency")


# Global validator instances
business_validator = BusinessDataValidator()
financial_validator = FinancialDataValidator()
general_validator = DataValidator()


def validate_business_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for business data validation."""
    return business_validator.validate_business_data(data)


def validate_financial_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for financial data validation."""
    return financial_validator.validate_financial_data(data)


def validate_user_input(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for user input validation."""
    return general_validator.validate_user_input(data)



