import pytest
from domains.integrations.jobber.sync import JobberSyncService
from domains.ar.models.invoice import Invoice
from domains.core.models.sync_cursor import SyncCursor
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_jobber_sync(db, test_firm, test_jobber_integration):
    with patch("domains.integrations.jobber.client.JobberClient.fetch_data", new=AsyncMock()) as mock_fetch:
        mock_fetch.return_value = {
            "invoices": {
                "nodes": [{"id": "INV_001", "jobId": "JOB_001", "amount": 1000.0, "paidDate": "2025-01-01", "customer": {"id": "CUST_001"}}],
                "pageInfo": {"endCursor": "cursor_001", "hasNextPage": True}
            }
        }

        service = JobberSyncService(db)
        result = await service.sync(test_firm.firm_id, commit=True)

        assert "invoices" in result
        assert len(result["invoices"]["nodes"]) == 1
        invoice = db.query(Invoice).filter(Invoice.qbo_id == "INV_001").first()
        assert invoice is not None
        assert invoice.total == 1000.0
        cursor = db.query(SyncCursor).filter(SyncCursor.firm_id == test_firm.firm_id, SyncCursor.source == "jobber").first()
        assert cursor.cursor == "cursor_001"
