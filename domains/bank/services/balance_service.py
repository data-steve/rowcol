"""
Balance Service - Bank service for managing financial account balances.

Handles account balance data retrieval and formatting for digest generation
and financial reporting. Moved from domains/core/ to domains/bank/ as balances
are bank account data, not core business data.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.services.base_service import TenantAwareService
import logging

logger = logging.getLogger(__name__)

class BalanceService(TenantAwareService):
    """
    Service for managing financial account balances.
    
    Handles balance data queries and formatting for use by SmartSync
    and other services requiring balance information.
    """
    def __init__(self, db: Session, business_id: str):
        super().__init__(db, business_id)
        logger.info(f"Initialized BalanceService for business {business_id}")

    # ==================== SMART SYNC DATA METHODS ====================

    def get_current_balances(self) -> List[Dict[str, Any]]:
        """Get current balances for all accounts."""
        try:
            balances = self.db.query(Balance).filter(
                Balance.business_id == self.business_id
            ).all()

            return [
                {
                    "account_id": balance.qbo_account_id,
                    "current_balance": float(balance.current_balance),
                    "available_balance": float(balance.available_balance),
                    "account_type": balance.account_type,
                    "snapshot_date": balance.snapshot_date.isoformat() if balance.snapshot_date else None
                }
                for balance in balances
            ]
        except Exception as e:
            logger.error(f"Failed to get current balances: {e}")
            return []

    def get_total_available_balance(self) -> float:
        """Get total available balance across all accounts."""
        try:
            balances = self.db.query(Balance).filter(
                Balance.business_id == self.business_id
            ).all()
            
            return sum(float(balance.available_balance or 0) for balance in balances)
        except Exception as e:
            logger.error(f"Failed to get total available balance: {e}")
            return 0.0
    
    def get_balance_by_account_type(self, account_type: str) -> List[Dict[str, Any]]:
        """Get balances filtered by account type (checking, savings, etc.)."""
        try:
            balances = self.db.query(Balance).filter(
                Balance.business_id == self.business_id,
                Balance.account_type == account_type
            ).all()

            return [
                {
                    "account_id": balance.qbo_account_id,
                    "current_balance": float(balance.current_balance),
                    "available_balance": float(balance.available_balance),
                    "account_type": balance.account_type,
                    "snapshot_date": balance.snapshot_date.isoformat() if balance.snapshot_date else None
                }
                for balance in balances
            ]
        except Exception as e:
            logger.error(f"Failed to get balances for account type {account_type}: {e}")
            return []
