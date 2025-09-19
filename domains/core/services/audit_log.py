from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import Request
from decimal import Decimal
from domains.core.models.audit_log import AuditLog, EntityType, AuditSource, AuditAction
from typing import Optional, Dict, Any
import json
import uuid
from enum import Enum
from sqlalchemy.inspection import inspect


class AuditLogService:
    def __init__(self, db: Session, request: Request = None):
        self.db = db
        self.request = request

  
    def _sanitize_values(self, values: Any) -> Dict[str, Any]:
        sensitive_fields = {"password", "hashed_password", "token"}

        if hasattr(values, "__table__"):  # likely a SQLAlchemy model instance
            values = {
                c.key: getattr(values, c.key)
                for c in inspect(values).mapper.column_attrs
            }

        if not isinstance(values, dict):
            return {}

        sanitized = {}
        for k, v in values.items():
            if k in sensitive_fields:
                sanitized[k] = "REDACTED"
            elif isinstance(v, (datetime, date)):
                sanitized[k] = v.isoformat()
            elif isinstance(v, Enum):
                sanitized[k] = v.value
            elif isinstance(v, (uuid.UUID, Decimal)):
                sanitized[k] = str(v)
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_values(v)
            else:
                sanitized[k] = v
        return sanitized

    async def log_audit_event(
        self,
        user_id: Optional[str],
        business_id: Optional[str],
        action: AuditAction,
        entity_type: EntityType,
        entity_id: str,
        new_values: Dict[str, Any],
        cause_id: Optional[str] = None,
        source: AuditSource = AuditSource.USER,
        session_id: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        ip_address = "unknown"
        user_agent = "unknown"
        if self.request and hasattr(self.request, "client") and self.request.client:
            ip_address = self.request.client.host
        if self.request and hasattr(self.request, "headers") and self.request.headers:
            user_agent = self.request.headers.get("user-agent")
        sanitized_values = self._sanitize_values(new_values)
        sanitized_metadata = self._sanitize_values(context_metadata) if context_metadata else None
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            performed_by_user_id=user_id,
            context_business_id=business_id,
            source=source,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            new_values=json.dumps(sanitized_values) if sanitized_values else None,
            cause_id=cause_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            context_metadata=json.dumps(sanitized_metadata) if sanitized_metadata else None,
            created_at=datetime.utcnow()
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    