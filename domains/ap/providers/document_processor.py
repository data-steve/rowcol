"""
Document Processor Provider Abstraction

Defines the interface for document processing (OCR, bill extraction).
Follows ADR-002 Mock-First Development Strategy.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class DocumentProcessor(ABC):
    """
    Abstract base class for document processing operations.
    
    Handles extraction of bill data from uploaded documents:
    - PDF processing
    - Image OCR
    - Data extraction and validation
    """
    
    @abstractmethod
    def extract_bill_data(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract bill data from document.
        
        Args:
            file_data: Binary file content
            filename: Original filename
            
        Returns:
            Dictionary containing extracted bill data:
            {
                "vendor_name": str,
                "amount": float,
                "bill_number": str,
                "due_date": datetime,
                "issue_date": datetime,
                "description": str,
                "confidence": float,  # 0.0 to 1.0
                "extracted_fields": dict  # Raw OCR data
            }
        """
        pass
    
    @abstractmethod
    def validate_document(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate document format and quality.
        
        Args:
            file_data: Binary file content
            filename: Original filename
            
        Returns:
            Validation result with quality score and issues
        """
        pass
