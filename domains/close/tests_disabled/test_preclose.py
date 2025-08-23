# """
# Preamble: Tests for Close domain services in Stage 2 of the Escher project.
# References: Stage 2 requirements, domains/close/services/preclose.py.
# """
# import pytest
# from datetime import datetime, timedelta
# from domains.close.services.preclose import PreCloseService, PBCTrackerService, ClientCommsService, ClientPortalService
# from domains.close.schemas.preclose import PBCRequestCreate
# from domains.core.models.user import User as UserModel
# from domains.close.models.preclose import Exception as ExceptionModel
# import hashlib

# def test_run_checks(db, test_firm, test_client, mock_qbo):
#     service = PreCloseService(db)
#     period = datetime.utcnow()
#     checks = service.run_checks(test_firm.firm_id, test_client.client_id, period)
#     assert len(checks) == 2
#     assert any(c.type == "bank_rec" for c in checks)
#     assert any(c.type == "pbc_complete" for c in checks)

# def test_resolve_exception(db, test_firm, test_client, mock_qbo):
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
#     resolved = service.resolve_exception(test_firm.firm_id, exception.exception_id, "Manually reconciled")
#     assert resolved.resolution == "Manually reconciled"

# def test_create_pbc_request(db, test_firm, test_client, mock_qbo):
#     service = PBCTrackerService(db)
#     pbc_data = PBCRequestCreate(
#         period=datetime.utcnow(),
#         item_type="bank_stmt",
#         owner="client@example.com",
#         due_date=datetime.utcnow() + timedelta(days=7)
#     )
#     pbc = service.create_pbc_request(pbc_data, test_firm.firm_id, test_client.client_id)
#     assert pbc.firm_id == test_firm.firm_id
#     assert pbc.task_id is not None

# def test_compute_readiness_score(db, test_firm, test_client, mock_qbo):
#     service = PBCTrackerService(db)
#     period = datetime.utcnow()
#     score = service.compute_readiness_score(test_firm.firm_id, test_client.client_id, period)
#     assert score.score >= 0

# def test_login(db, test_firm, test_client, mock_qbo):
#     db.add(UserModel(
#         firm_id=test_firm.firm_id,
#         email="client@example.com",
#         role="client"
#     ))
#     db.commit()
#     # For now, just test that the user was created
#     user = db.query(UserModel).filter(UserModel.email == "client@example.com").first()
#     assert user is not None
#     assert user.role == "client"
