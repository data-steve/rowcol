"""
Bills Mirror Repository for MVP

Implements BillsMirrorRepo interface using SQLAlchemy models for the Smart Sync pattern.
Database-agnostic implementation that works with SQLite (MVP dev) and PostgreSQL (production).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import json
import logging

from ..db.models import MirrorBill

logger = logging.getLogger(__name__)

class BillsMirrorRepo:
    """Database-agnostic implementation of bills mirror repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_open(self, advisor_id: str, business_id: str) -> List[Dict[str, Any]]:
        """List open bills for advisor and business."""
        try:
            bills = self.db.query(MirrorBill).filter(
                and_(
                    MirrorBill.advisor_id == advisor_id,
                    MirrorBill.business_id == business_id,
                    MirrorBill.status == 'OPEN'
                )
            ).order_by(MirrorBill.due_date.asc()).all()
            
            result = []
            for bill in bills:
                bill_data = {
                    'bill_id': bill.bill_id,
                    'advisor_id': bill.advisor_id,
                    'business_id': bill.business_id,
                    'vendor_id': bill.vendor_id,
                    'vendor_name': bill.vendor_name,
                    'due_date': bill.due_date,
                    'amount': float(bill.amount) if bill.amount else None,
                    'status': bill.status,
                    'source_version': bill.source_version,
                    'last_synced_at': bill.last_synced_at.isoformat() if bill.last_synced_at else None,
                }
                
                # Parse JSON data if present
                if bill.data_json:
                    try:
                        bill_data.update(json.loads(bill.data_json))
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON data for bill {bill.bill_id}")
                
                result.append(bill_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to list open bills: {e}")
            return []
    
    def list_all(self, advisor_id: str, business_id: str) -> List[Dict[str, Any]]:
        """List all bills for advisor and business."""
        try:
            bills = self.db.query(MirrorBill).filter(
                and_(
                    MirrorBill.advisor_id == advisor_id,
                    MirrorBill.business_id == business_id
                )
            ).order_by(MirrorBill.due_date.asc()).all()
            
            result = []
            for bill in bills:
                bill_data = {
                    'bill_id': bill.bill_id,
                    'advisor_id': bill.advisor_id,
                    'business_id': bill.business_id,
                    'vendor_id': bill.vendor_id,
                    'vendor_name': bill.vendor_name,
                    'due_date': bill.due_date,
                    'amount': float(bill.amount) if bill.amount else None,
                    'status': bill.status,
                    'source_version': bill.source_version,
                    'last_synced_at': bill.last_synced_at.isoformat() if bill.last_synced_at else None,
                }
                
                # Parse JSON data if present
                if bill.data_json:
                    try:
                        bill_data.update(json.loads(bill.data_json))
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON data for bill {bill.bill_id}")
                
                result.append(bill_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to list all bills: {e}")
            return []
    
    def upsert_many(self, advisor_id: str, business_id: str, raw_bills: List[Dict[str, Any]], 
                   source_version: Optional[str], synced_at: datetime) -> None:
        """Upsert many bills into mirror."""
        try:
            for bill_data in raw_bills:
                # Extract key fields
                bill_id = bill_data.get('Id') or bill_data.get('id')
                if not bill_id:
                    logger.warning(f"Bill missing ID, skipping: {bill_data}")
                    continue
                
                vendor_name = bill_data.get('VendorRef', {}).get('name', '') if isinstance(bill_data.get('VendorRef'), dict) else ''
                due_date = bill_data.get('DueDate', '')
                amount = bill_data.get('TotalAmt', 0) or bill_data.get('amount', 0)
                status = 'OPEN'  # Default status for QBO bills
                
                # Check if bill exists
                existing_bill = self.db.query(MirrorBill).filter(
                    and_(
                        MirrorBill.bill_id == str(bill_id),
                        MirrorBill.advisor_id == advisor_id,
                        MirrorBill.business_id == business_id
                    )
                ).first()
                
                if existing_bill:
                    # Update existing bill
                    existing_bill.vendor_name = vendor_name
                    existing_bill.due_date = due_date
                    existing_bill.amount = amount
                    existing_bill.status = status
                    existing_bill.source_version = source_version
                    existing_bill.last_synced_at = synced_at
                    existing_bill.data_json = json.dumps(bill_data)
                else:
                    # Create new bill
                    new_bill = MirrorBill(
                        bill_id=str(bill_id),
                        advisor_id=advisor_id,
                        business_id=business_id,
                        vendor_name=vendor_name,
                        due_date=due_date,
                        amount=amount,
                        status=status,
                        source_version=source_version,
                        last_synced_at=synced_at,
                        data_json=json.dumps(bill_data)
                    )
                    self.db.add(new_bill)
            
            self.db.commit()
            logger.info(f"Upserted {len(raw_bills)} bills for advisor {advisor_id}, business {business_id}")
        except Exception as e:
            logger.error(f"Failed to upsert bills: {e}")
            self.db.rollback()
            raise
    
    def is_fresh(self, advisor_id: str, business_id: str, policy: Dict[str, Any]) -> bool:
        """Check if mirror data is fresh according to policy."""
        try:
            soft_ttl = policy.get('soft_ttl_seconds', 300)
            hard_ttl = policy.get('hard_ttl_seconds', 3600)
            
            # Get most recent sync time
            latest_bill = self.db.query(MirrorBill).filter(
                and_(
                    MirrorBill.advisor_id == advisor_id,
                    MirrorBill.business_id == business_id
                )
            ).order_by(desc(MirrorBill.last_synced_at)).first()
            
            if not latest_bill or not latest_bill.last_synced_at:
                return False  # No data, not fresh
            
            age_seconds = (datetime.now() - latest_bill.last_synced_at).total_seconds()
            return age_seconds <= soft_ttl
        except Exception as e:
            logger.error(f"Failed to check freshness: {e}")
            return False
    
    def get_by_id(self, advisor_id: str, business_id: str, bill_id: str) -> Optional[Dict[str, Any]]:
        """Get specific bill by ID."""
        try:
            bill = self.db.query(MirrorBill).filter(
                and_(
                    MirrorBill.advisor_id == advisor_id,
                    MirrorBill.business_id == business_id,
                    MirrorBill.bill_id == bill_id
                )
            ).first()
            
            if not bill:
                return None
            
            bill_data = {
                'bill_id': bill.bill_id,
                'advisor_id': bill.advisor_id,
                'business_id': bill.business_id,
                'vendor_id': bill.vendor_id,
                'vendor_name': bill.vendor_name,
                'due_date': bill.due_date,
                'amount': float(bill.amount) if bill.amount else None,
                'status': bill.status,
                'source_version': bill.source_version,
                'last_synced_at': bill.last_synced_at.isoformat() if bill.last_synced_at else None,
            }
            
            # Parse JSON data if present
            if bill.data_json:
                try:
                    bill_data.update(json.loads(bill.data_json))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON data for bill {bill_id}")
            
            return bill_data
        except Exception as e:
            logger.error(f"Failed to get bill by ID: {e}")
            return None
