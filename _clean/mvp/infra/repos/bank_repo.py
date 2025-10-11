"""
Balances Mirror Repository for MVP

Implements BalancesMirrorRepo interface using SQLAlchemy models for the Smart Sync pattern.
Database-agnostic implementation that works with SQLite (MVP dev) and PostgreSQL (production).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import json
import logging

from ..db.models import MirrorBalance

logger = logging.getLogger(__name__)

class BalancesMirrorRepo:
    """Database-agnostic implementation of balances mirror repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_all(self, advisor_id: str, business_id: str) -> List[Dict[str, Any]]:
        """List all account balances for advisor and business."""
        try:
            balances = self.db.query(MirrorBalance).filter(
                and_(
                    MirrorBalance.advisor_id == advisor_id,
                    MirrorBalance.business_id == business_id
                )
            ).order_by(MirrorBalance.account_name.asc()).all()
            
            result = []
            for balance in balances:
                balance_data = {
                    'balance_id': balance.balance_id,
                    'advisor_id': balance.advisor_id,
                    'business_id': balance.business_id,
                    'account_id': balance.account_id,
                    'account_name': balance.account_name,
                    'account_type': balance.account_type,
                    'balance': float(balance.balance) if balance.balance else None,
                    'as_of_date': balance.as_of_date,
                    'source_version': balance.source_version,
                    'last_synced_at': balance.last_synced_at.isoformat() if balance.last_synced_at else None,
                }
                
                # Parse JSON data if present
                if balance.data_json:
                    try:
                        balance_data.update(json.loads(balance.data_json))
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON data for balance {balance.balance_id}")
                
                result.append(balance_data)
            
            return result
        except Exception as e:
            logger.error(f"Failed to list balances: {e}")
            return []
    
    def upsert_many(self, advisor_id: str, business_id: str, raw_balances: List[Dict[str, Any]], 
                   source_version: Optional[str], synced_at: datetime) -> None:
        """Upsert many account balances into mirror."""
        try:
            for balance_data in raw_balances:
                # Extract key fields
                account_id = balance_data.get('Id') or balance_data.get('id')
                if not account_id:
                    logger.warning(f"Balance missing account ID, skipping: {balance_data}")
                    continue
                
                account_name = balance_data.get('Name', '') or balance_data.get('name', '')
                account_type = balance_data.get('AccountType', '') or balance_data.get('account_type', '')
                balance = balance_data.get('CurrentBalance', 0) or balance_data.get('balance', 0)
                as_of_date = balance_data.get('MetaData', {}).get('LastUpdatedTime', '') if isinstance(balance_data.get('MetaData'), dict) else ''
                
                # Check if balance exists
                existing_balance = self.db.query(MirrorBalance).filter(
                    and_(
                        MirrorBalance.balance_id == str(account_id),
                        MirrorBalance.advisor_id == advisor_id,
                        MirrorBalance.business_id == business_id
                    )
                ).first()
                
                if existing_balance:
                    # Update existing balance
                    existing_balance.account_name = account_name
                    existing_balance.account_type = account_type
                    existing_balance.balance = balance
                    existing_balance.as_of_date = as_of_date
                    existing_balance.source_version = source_version
                    existing_balance.last_synced_at = synced_at
                    existing_balance.data_json = json.dumps(balance_data)
                else:
                    # Create new balance
                    new_balance = MirrorBalance(
                        balance_id=str(account_id),
                        advisor_id=advisor_id,
                        business_id=business_id,
                        account_id=str(account_id),
                        account_name=account_name,
                        account_type=account_type,
                        balance=balance,
                        as_of_date=as_of_date,
                        source_version=source_version,
                        last_synced_at=synced_at,
                        data_json=json.dumps(balance_data)
                    )
                    self.db.add(new_balance)
            
            self.db.commit()
            logger.info(f"Upserted {len(raw_balances)} balances for advisor {advisor_id}, business {business_id}")
        except Exception as e:
            logger.error(f"Failed to upsert balances: {e}")
            self.db.rollback()
            raise
    
    def is_fresh(self, advisor_id: str, business_id: str, policy: Dict[str, Any]) -> bool:
        """Check if mirror data is fresh according to policy."""
        try:
            soft_ttl = policy.get('soft_ttl_seconds', 120)  # 2 minutes default
            hard_ttl = policy.get('hard_ttl_seconds', 600)
            
            # Get most recent sync time
            latest_balance = self.db.query(MirrorBalance).filter(
                and_(
                    MirrorBalance.advisor_id == advisor_id,
                    MirrorBalance.business_id == business_id
                )
            ).order_by(desc(MirrorBalance.last_synced_at)).first()
            
            if not latest_balance or not latest_balance.last_synced_at:
                return False  # No data, not fresh
            
            age_seconds = (datetime.now() - latest_balance.last_synced_at).total_seconds()
            return age_seconds <= soft_ttl
        except Exception as e:
            logger.error(f"Failed to check freshness: {e}")
            return False
    
    def get_by_id(self, advisor_id: str, business_id: str, balance_id: str) -> Optional[Dict[str, Any]]:
        """Get specific account balance by ID."""
        try:
            balance = self.db.query(MirrorBalance).filter(
                and_(
                    MirrorBalance.advisor_id == advisor_id,
                    MirrorBalance.business_id == business_id,
                    MirrorBalance.balance_id == balance_id
                )
            ).first()
            
            if not balance:
                return None
            
            balance_data = {
                'balance_id': balance.balance_id,
                'advisor_id': balance.advisor_id,
                'business_id': balance.business_id,
                'account_id': balance.account_id,
                'account_name': balance.account_name,
                'account_type': balance.account_type,
                'balance': float(balance.balance) if balance.balance else None,
                'as_of_date': balance.as_of_date,
                'source_version': balance.source_version,
                'last_synced_at': balance.last_synced_at.isoformat() if balance.last_synced_at else None,
            }
            
            # Parse JSON data if present
            if balance.data_json:
                try:
                    balance_data.update(json.loads(balance.data_json))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON data for balance {balance_id}")
            
            return balance_data
        except Exception as e:
            logger.error(f"Failed to get balance by ID: {e}")
            return None
