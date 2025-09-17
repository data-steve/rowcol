"""
Preamble: Tests for TransferService and routes in Stage 1C of the Escher project.
Includes unit and integration tests for transfer creation and detection (Slice 3).
References: Stage 1C requirements, tests/conftest.py, services/transfer.py.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from sqlalchemy.orm import Session
from domains.bank.services.transfer import TransferService
from domains.bank.services.bank_transaction import BankTransactionService
from domains.bank.schemas.bank_transaction import BankTransactionCreate
from domains.bank.schemas.transfer import TransferCreate
from datetime import datetime

def test_create_transfer(mock_qbo, db: Session, test_firm, test_client):
    """
    Test creating a transfer linking two bank transactions.
    """
    bank_service = BankTransactionService(db)
    tx1_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=1000.0,
        date=datetime.utcnow(),
        description="Transfer Out",
        source="qbo_feed"
    )
    tx2_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=-1000.0,
        date=datetime.utcnow(),
        description="Transfer In",
        source="qbo_feed"
    )
    
    tx1 = bank_service.create_transaction(tx1_data, test_firm.firm_id, test_client.client_id)
    tx2 = bank_service.create_transaction(tx2_data, test_firm.firm_id, test_client.client_id)
    
    transfer_service = TransferService(db)
    transfer_data = TransferCreate(
        source_transaction_id=tx1.transaction_id,
        destination_transaction_id=tx2.transaction_id,
        amount=1000.0,
        date=datetime.utcnow(),
        description="Account Transfer"
    )
    
    transfer = transfer_service.create_transfer(transfer_data, test_firm.firm_id)
    
    assert transfer.firm_id == test_firm.firm_id
    assert transfer.source_transaction_id == tx1.transaction_id
    assert transfer.destination_transaction_id == tx2.transaction_id
    assert transfer.amount == 1000.0

def test_detect_transfers(mock_qbo, db: Session, test_firm, test_client):
    """
    Test detecting transfers based on equal and opposite transactions.
    """
    bank_service = BankTransactionService(db)
    tx1_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=1000.0,
        date=datetime.utcnow(),
        description="Transfer Out",
        source="qbo_feed"
    )
    tx2_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=-1000.0,
        date=datetime.utcnow(),
        description="Transfer In",
        source="qbo_feed"
    )
    
    bank_service.create_transaction(tx1_data, test_firm.firm_id, test_client.client_id)
    bank_service.create_transaction(tx2_data, test_firm.firm_id, test_client.client_id)
    
    transfer_service = TransferService(db)
    transfers = transfer_service.detect_transfers(test_firm.firm_id, test_client.client_id)
    
    assert len(transfers) == 1
    assert transfers[0].firm_id == test_firm.firm_id
    assert transfers[0].amount == 1000.0

def test_create_transfer_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the POST /api/bank/transfers endpoint.
    """
    bank_service = BankTransactionService(db)
    tx1_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=1000.0,
        date=datetime.utcnow(),
        description="Transfer Out",
        source="qbo_feed"
    )
    tx2_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=-1000.0,
        date=datetime.utcnow(),
        description="Transfer In",
        source="qbo_feed"
    )
    
    tx1 = bank_service.create_transaction(tx1_data, test_firm.firm_id, test_client.client_id)
    tx2 = bank_service.create_transaction(tx2_data, test_firm.firm_id, test_client.client_id)
    
    response = client.post(
            "/api/bank/transfers",
            json={
                "source_transaction_id": tx1.transaction_id,
                "destination_transaction_id": tx2.transaction_id,
                "amount": 1000.0,
                "date": datetime.utcnow().isoformat(),
                "description": "Account Transfer"
            },
            params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["firm_id"] == test_firm.firm_id
    assert data["source_transaction_id"] == tx1.transaction_id
    assert data["destination_transaction_id"] == tx2.transaction_id

def test_detect_transfers_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the GET /api/bank/transfers endpoint.
    """
    bank_service = BankTransactionService(db)
    tx1_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=1000.0,
        date=datetime.utcnow(),
        description="Transfer Out",
        source="qbo_feed"
    )
    tx2_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=-1000.0,
        date=datetime.utcnow(),
        description="Transfer In",
        source="qbo_feed"
    )
    
    bank_service.create_transaction(tx1_data, test_firm.firm_id, test_client.client_id)
    bank_service.create_transaction(tx2_data, test_firm.firm_id, test_client.client_id)
    
    response = client.get(
        "/api/bank/transfers",
        params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["firm_id"] == test_firm.firm_id