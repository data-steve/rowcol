from sqlalchemy.orm import Session
from models.service import Service
from schemas.service import ServiceCreate, ServicePreview
from typing import List
import json

# In-memory cache
IN_MEMORY_CACHE = {}

class ServiceService:
    def __init__(self, db: Session):
        self.db = db

    def create_service(self, service: ServiceCreate) -> Service:
        db_service = Service(**service.dict())
        db_service.automation_score = self.calculate_automation_score(db_service)
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        cache_dict = {
            "service_id": db_service.service_id,
            "name": db_service.name,
            "description": db_service.description,
            "price": db_service.price,
            "complexity_score": db_service.complexity_score,
            "task_sequence": db_service.task_sequence,
            "tier": db_service.tier,
            "automation_score": db_service.automation_score,
            "client_instructions": db_service.client_instructions
        }
        IN_MEMORY_CACHE[f"service:{db_service.service_id}"] = json.dumps(cache_dict)
        return db_service

    def bundle_services(self, tier: str) -> List[Service]:
        cache_key = f"services:{tier}"
        if cache_key in IN_MEMORY_CACHE:
            return [Service(**json.loads(item)) for item in json.loads(IN_MEMORY_CACHE[cache_key])]
        services = self.db.query(Service).filter(Service.tier == tier).all()
        total_price = sum(s.price for s in services)
        if tier == "pro":
            total_price *= 1.2  # 20% premium
        elif tier == "enterprise":
            total_price *= 1.5  # 50% premium
        IN_MEMORY_CACHE[cache_key] = json.dumps([s.__dict__ for s in services])
        return services

    def preview_service(self, service_id: int) -> ServicePreview:
        service = self.db.query(Service).filter(Service.service_id == service_id).first()
        if not service:
            raise ValueError("Service not found")
        requirements = [{"form": "bookkeeping", "requirement": "Provide QBO access"}]
        return ServicePreview(
            service_id=service.service_id,
            name=service.name,
            task_sequence=service.task_sequence,
            compliance_requirements=requirements
        )

    def calculate_automation_score(self, service: Service) -> float:
        # Mock automation score based on task sequence
        return 0.8 if any(t.get("step_type") == "reconcile" for t in service.task_sequence) else 0.5