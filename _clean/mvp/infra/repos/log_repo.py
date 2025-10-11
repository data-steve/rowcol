"""
Transaction Log Repository for MVP

Implements LogRepo interface using SQLAlchemy models for the Smart Sync pattern.
Database-agnostic implementation that works with SQLite (MVP dev) and PostgreSQL (production).
Manages the append-only transaction log for audit and retry/replay.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import json
import logging
import uuid

from ..db.models import IntegrationLog

logger = logging.getLogger(__name__)

class LogRepo:
    """Database-agnostic implementation of transaction log repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def append(self, *, direction: str, rail: str, operation: str, advisor_id: str, business_id: str,
               idem_key: Optional[str] = None, http_code: Optional[int] = None,
               status: Optional[str] = None, payload_json: Optional[str] = None,
               source_version: Optional[str] = None) -> None:
        """Append entry to transaction log."""
        try:
            log_entry = IntegrationLog(
                log_id=str(uuid.uuid4()),
                advisor_id=advisor_id,
                business_id=business_id,
                entity_type=rail,  # Using rail as entity_type for now
                entity_id=idem_key,
                operation=operation,
                status=status or 'success',
                error_message=None,
                source_version=source_version,
                metadata_json=payload_json
            )
            
            self.db.add(log_entry)
            self.db.commit()
            logger.debug(f"Logged {direction} {rail} {operation} for advisor {advisor_id}")
        except Exception as e:
            logger.error(f"Failed to append to log: {e}")
            self.db.rollback()
            raise
    
    def flag_hygiene(self, advisor_id: str, code: str) -> None:
        """Flag hygiene issue for advisor."""
        try:
            # For now, we'll log hygiene flags as special log entries
            # In a full implementation, this might go to a separate hygiene table
            payload = json.dumps({"hygiene_code": code, "flagged_at": datetime.now().isoformat()})
            
            log_entry = IntegrationLog(
                log_id=str(uuid.uuid4()),
                advisor_id=advisor_id,
                business_id='',  # Hygiene flags are advisor-level
                entity_type='hygiene',
                entity_id=code,
                operation='hygiene_flag',
                status='FLAGGED',
                error_message=None,
                source_version=None,
                metadata_json=payload
            )
            
            self.db.add(log_entry)
            self.db.commit()
            logger.warning(f"Flagged hygiene issue {code} for advisor {advisor_id}")
        except Exception as e:
            logger.error(f"Failed to flag hygiene: {e}")
            self.db.rollback()
            raise
    
    def get_recent_logs(self, advisor_id: str, business_id: str, limit: int = 100) -> list[Dict[str, Any]]:
        """Get recent log entries for advisor and business."""
        try:
            logs = self.db.query(IntegrationLog).filter(
                and_(
                    IntegrationLog.advisor_id == advisor_id,
                    IntegrationLog.business_id == business_id
                )
            ).order_by(desc(IntegrationLog.created_at)).limit(limit).all()
            
            result = []
            for log in logs:
                log_data = {
                    'log_id': log.log_id,
                    'advisor_id': log.advisor_id,
                    'business_id': log.business_id,
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'operation': log.operation,
                    'status': log.status,
                    'error_message': log.error_message,
                    'source_version': log.source_version,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                }
                
                # Parse JSON payload if present
                if log.metadata_json:
                    try:
                        log_data['payload'] = json.loads(log.metadata_json)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON payload for log {log.log_id}")
                
                result.append(log_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to get recent logs: {e}")
            return []
    
    def get_hygiene_flags(self, advisor_id: str, business_id: str) -> list[Dict[str, Any]]:
        """Get hygiene flags for advisor and business."""
        try:
            flags = self.db.query(IntegrationLog).filter(
                and_(
                    IntegrationLog.advisor_id == advisor_id,
                    IntegrationLog.business_id == business_id,
                    IntegrationLog.entity_type == 'hygiene'
                )
            ).order_by(desc(IntegrationLog.created_at)).all()
            
            result = []
            for flag in flags:
                flag_data = {
                    'log_id': flag.log_id,
                    'advisor_id': flag.advisor_id,
                    'business_id': flag.business_id,
                    'entity_type': flag.entity_type,
                    'entity_id': flag.entity_id,
                    'operation': flag.operation,
                    'status': flag.status,
                    'error_message': flag.error_message,
                    'source_version': flag.source_version,
                    'created_at': flag.created_at.isoformat() if flag.created_at else None,
                }
                
                # Parse JSON payload if present
                if flag.metadata_json:
                    try:
                        flag_data['payload'] = json.loads(flag.metadata_json)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON payload for hygiene flag {flag.log_id}")
                
                result.append(flag_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to get hygiene flags: {e}")
            return []
