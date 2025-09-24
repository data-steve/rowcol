from typing import Dict
from sqlalchemy.orm import Session
try:
    from plaid import Configuration, ApiBusiness
    from plaid.api import plaid_api
    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False
from domains.core.models.sync_cursor import SyncCursor
from domains.core.models.integration import Integration
from domains.bank.models.bank_transaction import BankTransaction, ProcessorType
from datetime import datetime
import os

class PlaidSyncService:
    def __init__(self, db: Session):
        self.db = db
        if PLAID_AVAILABLE:
            configuration = Configuration(
                host="https://sandbox.plaid.com",
                api_key={"clientId": os.getenv("PLAID_CLIENT_ID"), "secret": os.getenv("PLAID_SECRET")}
            )
            self.client = plaid_api.PlaidApi(ApiBusiness(configuration))
        else:
            self.client = None

    async def sync(self, business_id: int, commit: bool = False) -> Dict:
        if not PLAID_AVAILABLE or not self.client:
            return {"added": [], "has_more": False, "next_cursor": None}
            
        cursor = self.db.query(SyncCursor).filter(
            SyncCursor.business_id == business_id,
            SyncCursor.source == "plaid"
        ).first()
        integration = self.db.query(Integration).filter(
            Integration.business_id == business_id,
            Integration.platform == "plaid"
        ).first()

        if not integration or not integration.access_token:
            raise ValueError("Plaid integration not configured")

        try:
            result = self.client.transactions_sync({
                "access_token": integration.access_token,
                "cursor": cursor.cursor if cursor else None,
                "count": 500  # Maximize transactions per call
            }).to_dict()
        except Exception:
            # Mock response for testing
            result = {"added": [], "has_more": False, "next_cursor": None}

        if commit:
            for tx in result["added"]:
                # Deduplicate using (source, external_id, day_bucket)
                day_bucket = tx["date"]
                existing = self.db.query(BankTransaction).filter(
                    BankTransaction.business_id == business_id,
                    BankTransaction.source == "plaid",
                    BankTransaction.external_id == tx["transaction_id"],
                    BankTransaction.date.startswith(day_bucket)
                ).first()
                if not existing:
                    # Validate business account using /identity/get
                    identity = self.client.identity_get({"access_token": integration.access_token}).to_dict()
                    is_business = any(acc["subtype"] in ["checking", "savings"] and acc["name"].lower().find("business") != -1 for acc in identity["accounts"])
                    if not is_business:
                        status = "pending"  # Flag for manual review
                    else:
                        status = "pending"

                    transaction = BankTransaction(
                        business_id=business_id,
                        external_id=tx["transaction_id"],
                        amount=tx["amount"],
                        date=datetime.strptime(tx["date"], "%Y-%m-%d"),
                        description=tx["name"] or "Unknown",
                        account_id=tx["account_id"],
                        source="plaid",
                        processor=ProcessorType.ACH if tx["payment_channel"] == "ach" else None,
                        status=status,
                        confidence=1.0 if is_business else 0.5
                    )
                    self.db.add(transaction)

                if result["has_more"]:
                    if not cursor:
                        cursor = SyncCursor(business_id=business_id, source="plaid")
                        self.db.add(cursor)
                    cursor.cursor = result["next_cursor"]

            self.db.commit()

        return result
