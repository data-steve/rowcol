"""
QBO Balances Gateway Implementation

Implements BalancesGateway interface using QBO API and Smart Sync pattern.
Provides QBO-specific implementation of rail-agnostic balances operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from domains.bank.gateways import BalancesGateway, AccountBalance, ListBalancesQuery
from infra.sync.orchestrator import SyncOrchestrator
from infra.repos.bank_repo import BalancesMirrorRepo
from infra.rails.qbo.client import QBORawClient
from infra.config.exceptions import IntegrationError

logger = logging.getLogger(__name__)

class QBOBalancesGateway(BalancesGateway):
    """QBO implementation of BalancesGateway using Smart Sync pattern."""
    
    def __init__(self, advisor_id: str, business_id: str, realm_id: str, 
                 sync_orchestrator: SyncOrchestrator, balances_repo: BalancesMirrorRepo):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.realm_id = realm_id
        self.sync_orchestrator = sync_orchestrator
        self.balances_repo = balances_repo
        self.qbo_client = QBORawClient(business_id, realm_id)
        
        logger.info(f"Initialized QBOBalancesGateway for advisor {advisor_id}, business {business_id}")
    
    async def list_balances(self, query: ListBalancesQuery) -> List[AccountBalance]:
        """List account balances using Smart Sync pattern."""
        try:
            # Use sync orchestrator to get fresh data
            result = await self.sync_orchestrator.read_refresh(
                advisor_id=self.advisor_id,
                business_id=self.business_id,
                entity_type="balances",
                freshness_hint=query.freshness_hint,
                read_func=self._fetch_balances_from_qbo,
                read_params={}
            )
            
            # Convert QBO data to domain AccountBalance objects
            balances = []
            for balance_data in result.get("data", []):
                balance = self._convert_qbo_to_balance(balance_data)
                balances.append(balance)
            
            return balances
            
        except Exception as e:
            logger.error(f"Failed to list balances: {e}")
            raise IntegrationError(f"Failed to list balances: {e}")
    
    async def get_balance(self, account_id: str) -> Optional[AccountBalance]:
        """Get specific account balance by ID."""
        try:
            # Check mirror first
            mirror_balance = self.balances_repo.get_by_id(
                self.advisor_id, self.business_id, account_id
            )
            
            if mirror_balance:
                return self._convert_mirror_to_balance(mirror_balance)
            
            # If not in mirror, fetch from QBO using raw HTTP
            qbo_response = self.qbo_client.get(f"accounts/{account_id}")
            qbo_balance = qbo_response.get("QueryResponse", {}).get("Account", [])
            if qbo_balance:
                return self._convert_qbo_to_balance(qbo_balance[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get balance {account_id}: {e}")
            raise IntegrationError(f"Failed to get balance: {e}")
    
    async def _fetch_balances_from_qbo(self) -> Dict[str, Any]:
        """Fetch account balances from QBO API."""
        try:
            # Use raw HTTP client to get accounts
            response = self.qbo_client.get("accounts")
            balances_data = response.get("QueryResponse", {})
            
            # Update mirror with fresh data
            await self.sync_orchestrator.write_with_log(
                advisor_id=self.advisor_id,
                business_id=self.business_id,
                entity_type="balances",
                operation="sync",
                status="success",
                metadata={"count": len(balances_data.get("accounts", []))}
            )
            
            return balances_data
            
        except Exception as e:
            logger.error(f"Failed to fetch balances from QBO: {e}")
            await self.sync_orchestrator.write_with_log(
                advisor_id=self.advisor_id,
                business_id=self.business_id,
                entity_type="balances",
                operation="sync",
                status="error",
                error_message=str(e)
            )
            raise
    
    def _convert_qbo_to_balance(self, qbo_data: Dict[str, Any]) -> AccountBalance:
        """Convert QBO account data to domain AccountBalance object."""
        return AccountBalance(
            balance_id=str(qbo_data.get("Id", "")),
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            account_id=str(qbo_data.get("Id", "")),
            account_name=qbo_data.get("Name", ""),
            account_type=qbo_data.get("AccountType", ""),
            balance=Decimal(str(qbo_data.get("CurrentBalance", 0))),
            as_of_date=qbo_data.get("MetaData", {}).get("LastUpdatedTime", ""),
            qbo_sync_token=qbo_data.get("SyncToken", ""),
            qbo_meta_data=qbo_data.get("MetaData", {}),
            raw_data=qbo_data
        )
    
    def _convert_mirror_to_balance(self, mirror_data: Dict[str, Any]) -> AccountBalance:
        """Convert mirror balance data to domain AccountBalance object."""
        return AccountBalance(
            balance_id=mirror_data["balance_id"],
            advisor_id=mirror_data["advisor_id"],
            business_id=mirror_data["business_id"],
            account_id=mirror_data.get("account_id", ""),
            account_name=mirror_data.get("account_name", ""),
            account_type=mirror_data.get("account_type", ""),
            balance=Decimal(str(mirror_data.get("balance", 0))),
            as_of_date=mirror_data.get("as_of_date", ""),
            qbo_sync_token=mirror_data.get("qbo_sync_token", ""),
            qbo_meta_data=mirror_data.get("qbo_meta_data", {}),
            raw_data=mirror_data
        )
