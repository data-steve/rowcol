"""
TestDrive Experience Service

Provides TestDrive PLG experience using the DigestDataOrchestrator with
flexible configuration for A/B testing and experimentation.

TestDrive is essentially a configurable version of the Digest experience
designed to convert prospects into paying customers by showing them
the value of Oodaloo's analysis capabilities.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from runway.services.data_orchestrators.digest_data_orchestrator import DigestDataOrchestrator, DigestConfig
from runway.services.calculators.insight_calculator import InsightCalculator
import logging

logger = logging.getLogger(__name__)


class TestDriveService:
    """
    TestDrive experience service that uses DigestDataOrchestrator with TestDrive configuration.
    
    This service provides a PLG (Product-Led Growth) experience by showing prospects
    what Oodaloo can do for their business using their own data or sandbox data.
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Use SAME orchestrator as digest with different configuration
        self.data_orchestrator = DigestDataOrchestrator(db)
        # Add insight calculator for enhanced analysis
        self.insight_calculator = InsightCalculator(db, "test_drive", validate_business=False)
    
    async def get_test_drive_experience(self, business_id: str, 
                                      experiment_variant: str = "A") -> Dict[str, Any]:
        """
        Get TestDrive experience with A/B testing support.
        
        Args:
            business_id: The business to analyze (None for sandbox)
            experiment_variant: A/B test variant ("A", "B", "C", etc.)
            
        Returns:
            TestDrive experience data
        """
        try:
            # Get configuration for this variant
            config = DigestConfig.for_test_drive(experiment_variant)
            
            # Use same digest logic with TestDrive parameters
            return await self.data_orchestrator.get_digest_data(business_id, config)
            
        except Exception as e:
            logger.error(f"Error getting TestDrive experience for business {business_id}: {e}")
            raise
    
    async def get_test_drive_experience_custom(self, business_id: str, 
                                             config: DigestConfig) -> Dict[str, Any]:
        """Get TestDrive with custom configuration for experimentation."""
        try:
            # Ensure it's configured for TestDrive
            config.trigger_type = "test_drive"
            config.preview_mode = True  # TestDrive is always preview mode
            
            return await self.data_orchestrator.get_digest_data(business_id, config)
            
        except Exception as e:
            logger.error(f"Error getting custom TestDrive experience for business {business_id}: {e}")
            raise
    
    async def get_sandbox_test_drive(self, experiment_variant: str = "A") -> Dict[str, Any]:
        """Get TestDrive experience using sandbox data for prospects without real data."""
        try:
            # Use sandbox business_id for demo data
            return await self.get_test_drive_experience("sandbox", experiment_variant)
            
        except Exception as e:
            logger.error(f"Error getting sandbox TestDrive experience: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def get_enhanced_test_drive_experience(self, business_id: str, 
                                               experiment_variant: str = "A") -> Dict[str, Any]:
        """
        Get enhanced TestDrive experience with insights and value proposition analysis.
        
        Args:
            business_id: The business to analyze (None for sandbox)
            experiment_variant: A/B test variant ("A", "B", "C", etc.)
            
        Returns:
            Enhanced TestDrive experience data with insights
        """
        try:
            # Get base test drive data
            test_drive_data = await self.get_test_drive_experience(business_id, experiment_variant)
            
            # Generate insights about the data
            insights = self.insight_calculator.generate_insights(test_drive_data)
            
            # Generate value proposition analysis
            value_prop = self.insight_calculator.calculate_value_proposition(test_drive_data)
            
            # Generate demo metrics
            demo_metrics = self.insight_calculator.calculate_demo_metrics(test_drive_data)
            
            # Generate marketing copy
            marketing_copy = self.insight_calculator.generate_marketing_copy(value_prop)
            
            # Enhance the test drive data
            test_drive_data.update({
                "insights": insights,
                "value_proposition": value_prop,
                "demo_metrics": demo_metrics,
                "marketing_copy": marketing_copy,
                "enhanced": True
            })
            
            return test_drive_data
            
        except Exception as e:
            logger.error(f"Error getting enhanced TestDrive experience for business {business_id}: {e}")
            raise


class DemoTestDriveService:
    """
    Legacy DemoTestDriveService - TEMPORARY PLACEHOLDER
    
    This service is a placeholder to maintain backward compatibility while
    we complete the orchestrator integration analysis (S07).
    
    TODO: Replace with proper implementation after S07 analysis is complete.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.test_drive_service = TestDriveService(db)
    
    async def generate_test_drive(self, business_id: str = None, use_sandbox: bool = False) -> Dict[str, Any]:
        """Generate test drive data - uses new TestDriveService."""
        try:
            if use_sandbox or business_id is None:
                return await self.test_drive_service.get_sandbox_test_drive()
            else:
                return await self.test_drive_service.get_test_drive_experience(business_id)
                
        except Exception as e:
            logger.error(f"Error generating test drive: {e}")
            raise
    
    def generate_hygiene_score(self, business_id: str) -> Dict[str, Any]:
        """TEMPORARY: Placeholder for hygiene score - needs S07 analysis."""
        logger.warning("generate_hygiene_score called - needs S07 analysis to determine proper implementation")
        return {
            "business_id": business_id,
            "error": "Method needs S07 analysis - temporary placeholder",
            "status": "pending_analysis"
        }
    
    def generate_qbo_sandbox_test_drive(self, industry: str = "software_agency") -> Dict[str, Any]:
        """TEMPORARY: Placeholder for sandbox demo - needs S07 analysis."""
        logger.warning("generate_qbo_sandbox_test_drive called - needs S07 analysis to determine proper implementation")
        return {
            "industry": industry,
            "error": "Method needs S07 analysis - temporary placeholder",
            "status": "pending_analysis"
        }