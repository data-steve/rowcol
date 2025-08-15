from sqlalchemy.orm import Session
from domains.core.models.service import Service as ServiceModel
from domains.ap.models.compliance import ComplianceRequirement, ServiceComplianceMapping
from domains.ap.models.task_template import TaskTemplate
from domains.core.schemas.service import Service
from typing import List, Optional
import json

# In-memory cache
IN_MEMORY_CACHE = {}

class ServiceService:
    def __init__(self, db: Session):
        self.db = db

    def create_service(self, service: Service) -> ServiceModel:
        """Create a new service."""
        db_service = ServiceModel(**service.model_dump())
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        return db_service

    def get_service(self, service_id: int, firm_id: str) -> ServiceModel:
        """Get a service by ID."""
        service = self.db.query(ServiceModel).filter(
            ServiceModel.service_id == service_id,
            ServiceModel.firm_id == firm_id
        ).first()
        if not service:
            raise ValueError("Service not found")
        return service

    def list_services(self) -> List[ServiceModel]:
        """List all services."""
        services = self.db.query(ServiceModel).all()
        return services

    def preview_service(self, service_id: int, firm_id: str) -> dict:
        """Preview service compliance requirements using real data from database."""
        service = self.db.query(ServiceModel).filter(
            ServiceModel.service_id == service_id,
            ServiceModel.firm_id == firm_id
        ).first()
        if not service:
            raise ValueError("Service not found")
        
        # Get real compliance requirements from database based on service type
        compliance_mappings = self.db.query(ServiceComplianceMapping).filter(
            ServiceComplianceMapping.service_type == service.service_type,
            ServiceComplianceMapping.is_required == True
        ).order_by(ServiceComplianceMapping.priority).all()
        
        compliance_requirements = []
        for mapping in compliance_mappings:
            requirement = mapping.requirement
            compliance_requirements.append({
                "requirement": requirement.requirement_name,
                "regulatory_source": requirement.regulatory_source,
                "frequency": requirement.frequency,
                "deadline": requirement.deadline,
                "description": requirement.description,
                "priority": mapping.priority,
                "status": "pending"  # This would be dynamic based on client compliance history
            })
        
        # Get task templates for this service type
        task_templates = self.db.query(TaskTemplate).filter(
            TaskTemplate.service_type == service.service_type
        ).all()
        
        task_sequence = []
        for template in task_templates:
            task_sequence.append({
                "step_type": template.task_type,
                "title": template.title,
                "description": template.description,
                "estimated_hours": template.estimated_hours,
                "priority": template.priority,
                "micro_tasks": template.micro_tasks or []
            })
        
        # Cache the result
        cache_key = f"service_preview_{service_id}_{firm_id}"
        IN_MEMORY_CACHE[cache_key] = json.dumps({
            "compliance_requirements": compliance_requirements,
            "task_sequence": task_sequence
        })
        
        return {
            "service_id": service.service_id,
            "name": service.name,
            "task_sequence": task_sequence,
            "firm_id": service.firm_id,
            "compliance_requirements": compliance_requirements
        }

    def bundle_services(self, tier: str) -> List[ServiceModel]:
        cache_key = f"services:{tier}"
        if cache_key in IN_MEMORY_CACHE:
            return [ServiceModel(**json.loads(item)) for item in json.loads(IN_MEMORY_CACHE[cache_key])]
        services = self.db.query(ServiceModel).filter(ServiceModel.tier == tier).all()
        total_price = sum(s.price for s in services)
        if tier == "pro":
            total_price *= 1.2  # 20% premium
        elif tier == "enterprise":
            total_price *= 1.5  # 50% premium
        IN_MEMORY_CACHE[cache_key] = json.dumps([s.__dict__ for s in services])
        return services

    def calculate_automation_score(self, service: Service) -> float:
        """Calculate automation score based on real task templates and business rules."""
        # Get task templates for this service type
        task_templates = self.db.query(TaskTemplate).filter(
            TaskTemplate.service_type == service.service_type
        ).all()
        
        if not task_templates:
            return 0.5  # Default score if no templates found
        
        # Calculate score based on task complexity and automation potential
        total_hours = sum(t.estimated_hours for t in task_templates)
        automated_tasks = sum(1 for t in task_templates if t.task_type in ['categorize', 'reconcile'])
        
        # Higher automation score for services with more automated tasks
        automation_score = min(0.9, 0.3 + (automated_tasks / len(task_templates)) * 0.6)
        
        return automation_score