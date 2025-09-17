# """
# Preamble: Integration tests for Close domain preclose routes in Stage 2.
# References: Stage 2 requirements, domains/close/routes/preclose.py.
# """
# import pytest
# from fastapi.testclient import TestClient
# from datetime import datetime, timedelta
# from domains.close.models.preclose import Exception as ExceptionModel
# from domains.close.services.preclose import PreCloseService

# def test_run_checks_api(client: TestClient, db, test_firm, test_client, mock_qbo):
#     response = client.post(
#         "/api/close/checks",
#         params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id, "period": datetime.utcnow().isoformat()}
#     )
#     assert response.status_code == 200
#     assert len(response.json()) == 2

# def test_resolve_exception_api(client: TestClient, db, test_firm, test_client, mock_qbo):
#     service = PreCloseService(db)
#     period = datetime.utcnow()
    
#     # Create test data that will cause checks to fail
#     from domains.bank.models.bank_transaction import BankTransaction as BankTransactionModel
#     from domains.close.models.preclose import PBCRequest as PBCRequestModel
    
#     # Add an unreconciled bank transaction
#     unreconciled_txn = BankTransactionModel(
#         firm_id=test_firm.firm_id,
#         client_id=test_client.client_id,
#         date=period,
#         amount=100.0,
#         description="Test transaction",
#         status="pending",
#         source="manual"
#     )
#     db.add(unreconciled_txn)
    
#     # Add a pending PBC request
#     pending_pbc = PBCRequestModel(
#         firm_id=test_firm.firm_id,
#         client_id=test_client.client_id,
#         period=period,
#         item_type="bank_stmt",
#         owner="test@example.com",
#         due_date=period + timedelta(days=7),
#         status="pending"
#     )
#     db.add(pending_pbc)
#     db.commit()
    
#     # Now run checks - should create exceptions
#     service.run_checks(test_firm.firm_id, test_client.client_id, period)
#     exception = db.query(ExceptionModel).filter(ExceptionModel.firm_id == test_firm.firm_id).first()
#     assert exception is not None, "Exception should be created by run_checks"
#     response = client.patch(
#         f"/api/close/checks/exceptions/{exception.exception_id}",
#         params={"firm_id": test_firm.firm_id, "resolution": "Resolved"}
#     )
#     assert response.status_code == 200
#     assert response.json()["resolution"] == "Resolved"
