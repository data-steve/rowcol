"""
Mock Document Processor for AP Domain

Provides realistic mock document processing during development.
Follows ADR-002 Mock-First Development Strategy.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from decimal import Decimal

from .document_processor import DocumentProcessor


class MockDocumentProcessor(DocumentProcessor):
    """
    Mock implementation of document processor.
    
    Simulates realistic document processing results with variety
    in confidence scores, extraction quality, and processing times.
    """
    
    def __init__(self):
        # Mock vendor patterns for realistic extraction
        self._vendor_patterns = [
            {
                "name": "HubSpot",
                "variations": ["HubSpot", "HUBSPOT", "Hub Spot", "HubSpot, Inc."],
                "typical_amounts": [1200.00, 2400.00, 600.00],
                "bill_number_pattern": "HS-{year}-{month:02d}-{seq:04d}"
            },
            {
                "name": "Google Workspace", 
                "variations": ["Google", "Google LLC", "Google Workspace", "G Suite"],
                "typical_amounts": [144.00, 288.00, 72.00],
                "bill_number_pattern": "GWS-{year}{month:02d}-{seq:06d}"
            },
            {
                "name": "Office Depot",
                "variations": ["Office Depot", "OFFICE DEPOT", "Office Depot, Inc."],
                "typical_amounts": [89.99, 234.56, 156.78, 45.23],
                "bill_number_pattern": "OD{seq:08d}"
            },
            {
                "name": "Adobe Creative Cloud",
                "variations": ["Adobe", "Adobe Inc.", "Adobe Creative Cloud", "Adobe Systems"],
                "typical_amounts": [79.99, 159.98, 239.97],
                "bill_number_pattern": "ADO-{year}-{seq:07d}"
            }
        ]
    
    def extract_bill_data(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Mock bill data extraction with realistic variety.
        
        Simulates OCR processing with varying confidence levels
        and realistic vendor/amount combinations.
        """
        # Simulate processing delay
        import time
        time.sleep(random.uniform(0.5, 2.0))
        
        # Select random vendor for mock extraction
        vendor_data = random.choice(self._vendor_patterns)
        vendor_name = random.choice(vendor_data["variations"])
        
        # Generate realistic bill details
        issue_date = datetime.utcnow() - timedelta(days=random.randint(1, 15))
        due_date = issue_date + timedelta(days=random.choice([15, 30, 45]))
        amount = random.choice(vendor_data["typical_amounts"])
        
        # Generate bill number
        bill_number = vendor_data["bill_number_pattern"].format(
            year=issue_date.year,
            month=issue_date.month,
            seq=random.randint(1, 9999)
        )
        
        # Simulate OCR confidence based on document quality
        file_extension = filename.lower().split('.')[-1]
        if file_extension == 'pdf':
            base_confidence = random.uniform(0.85, 0.98)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            base_confidence = random.uniform(0.70, 0.90)
        else:
            base_confidence = random.uniform(0.60, 0.80)
        
        # Add some noise to confidence
        confidence = max(0.5, min(1.0, base_confidence + random.uniform(-0.1, 0.1)))
        
        # Generate description
        descriptions = [
            f"{vendor_data['name']} monthly subscription",
            f"{vendor_data['name']} services - {issue_date.strftime('%B %Y')}",
            f"Invoice from {vendor_data['name']}",
            f"{vendor_data['name']} - Professional services"
        ]
        description = random.choice(descriptions)
        
        # Simulate occasional extraction errors (10% chance)
        if random.random() < 0.1:
            # Introduce realistic OCR errors
            if random.random() < 0.5:
                # Wrong amount extraction
                amount *= random.uniform(0.8, 1.2)
                confidence *= 0.7
            else:
                # Wrong vendor name
                vendor_name = vendor_name.replace('o', '0').replace('l', '1')
                confidence *= 0.6
        
        extracted_data = {
            "vendor_name": vendor_name,
            "amount": round(amount, 2),
            "bill_number": bill_number,
            "due_date": due_date,
            "issue_date": issue_date,
            "description": description,
            "confidence": round(confidence, 3),
            "extracted_fields": {
                "raw_text": f"Mock OCR text for {filename}",
                "vendor_variations_found": [vendor_name],
                "amount_candidates": [amount],
                "date_candidates": [issue_date.isoformat(), due_date.isoformat()],
                "processing_method": "mock_ocr",
                "document_type": "bill",
                "page_count": 1,
                "file_size": len(file_data),
                "processing_time_ms": random.randint(500, 2000)
            }
        }
        
        return extracted_data
    
    def validate_document(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Mock document validation."""
        # Simulate validation delay
        import time
        time.sleep(random.uniform(0.1, 0.3))
        
        file_extension = filename.lower().split('.')[-1]
        file_size = len(file_data)
        
        # Simulate validation results
        is_valid = True
        quality_score = 0.9
        issues = []
        
        # Check file type
        if file_extension not in ['pdf', 'jpg', 'jpeg', 'png', 'tiff']:
            is_valid = False
            quality_score = 0.0
            issues.append(f"Unsupported file type: {file_extension}")
        
        # Check file size (simulate limits)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            is_valid = False
            quality_score *= 0.5
            issues.append("File too large (max 10MB)")
        
        if file_size < 1024:  # 1KB minimum
            is_valid = False
            quality_score *= 0.3
            issues.append("File too small (likely corrupted)")
        
        # Simulate quality assessment
        if file_extension in ['jpg', 'jpeg', 'png']:
            # Simulate image quality issues
            if random.random() < 0.2:
                quality_score *= random.uniform(0.6, 0.8)
                issues.append("Low image quality detected")
        
        return {
            "is_valid": is_valid,
            "quality_score": round(quality_score, 3),
            "file_type": file_extension,
            "file_size": file_size,
            "issues": issues,
            "recommendations": [
                "Use high-resolution PDF for best results",
                "Ensure text is clearly visible",
                "Avoid blurry or rotated images"
            ] if quality_score < 0.8 else []
        }
