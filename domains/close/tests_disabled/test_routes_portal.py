# """
# Preamble: Integration tests for Close domain portal routes in Stage 2.
# References: Stage 2 requirements, domains/close/routes/portal.py.
# """
# import pytest
# from fastapi.testclient import TestClient
# from datetime import datetime, timedelta
# from domains.close.services.preclose import PBCTrackerService
# from domains.close.schemas.preclose import PBCRequestCreate
# from domains.core.models.user import User as UserModel
# import hashlib

# def test_login_api(client: TestClient, db, test_firm, test_client, mock_qbo):
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

# def test_upload_pbc_api(client: TestClient, db, test_firm, test_client, mock_qbo):
#     pbc_service = PBCTrackerService(db)
#     pbc_data = PBCRequestCreate(
#         period=datetime.utcnow(),
#         item_type="bank_stmt",
#         owner="client@example.com",
#         due_date=datetime.utcnow() + timedelta(days=7)
#     )
#     pbc = pbc_service.create_pbc_request(pbc_data, test_firm.firm_id, test_client.client_id)
#     response = client.post(
#         f"/api/close/portal/pbc/upload?request_id={pbc.request_id}&firm_id={test_firm.firm_id}",
#         files={"file": ("test.pdf", b"mock content", "application/pdf")}
#     )
#     assert response.status_code == 200
#     assert response.json()["status"] == "received"
