from sqlalchemy.orm import Session
from models.engagement import Engagement
from schemas.engagement import EngagementCreate
from models.service import Service
from jinja2 import Environment, FileSystemLoader

from datetime import datetime
import json
import requests
import logging
import pdfkit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory cache and pub/sub simulation
IN_MEMORY_CACHE = {}
SUBSCRIBERS = []

class EngagementService:
    def __init__(self, db: Session):
        self.db = db
        self.env = Environment(loader=FileSystemLoader("templates"))

    def create_engagement(self, engagement: EngagementCreate) -> Engagement:
        db_engagement = Engagement(**engagement.dict())
        self.db.add(db_engagement)
        self.db.commit()
        self.db.refresh(db_engagement)
        self.validate_engagement(db_engagement.engagement_id)
        cache_dict = {
            "engagement_id": db_engagement.engagement_id,
            "firm_id": db_engagement.firm_id,
            "client_id": db_engagement.client_id,
            "service_type": db_engagement.service_type,
            "status": db_engagement.status,
            "due_date": db_engagement.due_date.isoformat(),
            "user_input": db_engagement.user_input,
            "allowance_overage": db_engagement.allowance_overage,
            "agreed_at": db_engagement.agreed_at.isoformat() if db_engagement.agreed_at else None,
            "health_status": db_engagement.health_status,
            "compliance_status": db_engagement.compliance_status,
            "e_signature": db_engagement.e_signature,
            "qbo_sync_status": db_engagement.qbo_sync_status
        }
        IN_MEMORY_CACHE[f"engagement:{db_engagement.engagement_id}"] = json.dumps(cache_dict)
        return db_engagement

    def validate_engagement(self, engagement_id: int):
        engagement = self.db.query(Engagement).filter(Engagement.engagement_id == engagement_id).first()
        if not engagement:
            raise ValueError("Engagement not found")
        errors = []
        if engagement.user_input and "qbo_account" in engagement.user_input:
            if not engagement.user_input["qbo_account"].isdigit():
                errors.append({"error_code": "invalid_qbo_account", "description": "Invalid QBO account number"})
        if errors:
            engagement.compliance_status = "fail"
            engagement.health_status = "critical"
            self.db.commit()
        return errors

    def generate_letter(self, engagement_id: int, format: str = "pdf") -> str:
        engagement = self.db.query(Engagement).filter(Engagement.engagement_id == engagement_id).first()
        if not engagement:
            raise ValueError("Engagement not found")
        services = self.db.query(Service).filter(Service.service_id.in_(engagement.service_ids)).all()
        total_price = sum(s.price for s in services)
        template = self.env.get_template("engagement_letter.html")
        html_content = template.render(
            engagement=engagement,
            services=services,
            total_price=total_price,
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            compliance_clauses=self._get_compliance_clauses()
        )
        if format == "pdf":
            pdf_path = f"static/engagement_{engagement.engagement_id}.pdf"
            pdfkit.from_string(html_content, pdf_path, options={"enable-local-file-access": None})
            return pdf_path
        return html_content

    def sign_engagement(self, engagement_id: int, signer_id: int, signature_data: str):
        engagement = self.db.query(Engagement).filter(Engagement.engagement_id == engagement_id).first()
        if not engagement:
            raise ValueError("Engagement not found")
        engagement.e_signature = {
            "signer_id": signer_id,
            "timestamp": datetime.utcnow().isoformat(),
            "signature_data": signature_data
        }
        engagement.status = "active"
        self.db.commit()
        # Mock DocuSign API - simulate success without making real HTTP calls
        # requests.post("https://mock.docusign.api/sign", json=engagement.e_signature)
        # Simulate pub/sub
        # update = json.dumps({"engagement_id": engagement_id, "status": "active"})
        # for subscriber in SUBSCRIBERS:
        #     subscriber.append(update)

    def sync_qbo(self, engagement_id: int) -> str:
        engagement = self.db.query(Engagement).filter(Engagement.engagement_id == engagement_id).first()
        if not engagement:
            raise ValueError("Engagement not found")
        engagement.qbo_sync_status = "syncing"
        self.db.commit()
        # Mock QBO API call - simulate success without making real HTTP calls
        # Simulate successful sync
        engagement.qbo_sync_status = "success"
        if engagement.user_input is None:
            engagement.user_input = {}
        engagement.user_input.update({"sync_timestamp": datetime.utcnow().isoformat()})
        self.db.commit()
        return "Sync successful"

    def _get_compliance_clauses(self) -> list[str]:
        return [
            "Client must provide accurate QBO account details.",
            "Financial data must be submitted by due date."
        ]