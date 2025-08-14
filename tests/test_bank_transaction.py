"""
Preamble: Tests for BankTransactionService and routes in Stage 1C of the Escher project.
Includes unit and integration tests for transaction creation, listing, and categorization (Slice 2).
References: Stage 1C requirements, tests/conftest.py, tests/test_policy_engine.py.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from services.bank_transaction import BankTransactionService
from schemas.bank_transaction import BankTransactionCreate, BankTransactionCategorize
from models.bank_transaction import BankTransaction as BankTransactionModel
from datetime import datetime

def test_create_transaction(mock_qbo, db: Session, test_firm, test_client):
    """
    Test creating a bank transaction with tenant isolation and categorization.
    """
    service = BankTransactionService(db)
    transaction_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=150.0,
        date=datetime.utcnow(),
        description="Starbucks Purchase",
        source="qbo_feed"
    )
    
    transaction = service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    assert transaction.firm_id == test_firm.firm_id
    assert transaction.client_id == test_client.client_id
    assert transaction.amount == 150.0
    assert transaction.description == "Starbucks Purchase"
    assert transaction.suggestion_id is not None
    assert transaction.confidence > 0.0

def test_list_transactions(mock_qbo, db: Session, test_firm, test_client):
    """
    Test listing transactions with tenant isolation.
    """
    service = BankTransactionService(db)
    transaction_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=150.0,
        date=datetime.utcnow(),
        description="Starbucks Purchase",
        source="qbo_feed"
    )
    
    # Create a transaction
    service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    # List transactions
    transactions = service.list_transactions(test_firm.firm_id, test_client.client_id)
    
    assert len(transactions) == 1
    assert transactions[0].firm_id == test_firm.firm_id
    assert transactions[0].client_id == test_client.client_id

def test_categorize_transaction(mock_qbo, db: Session, test_firm, test_client):
    """
    Test categorizing an existing transaction with tenant isolation.
    """
    service = BankTransactionService(db)
    transaction_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=150.0,
        date=datetime.utcnow(),
        description="Starbucks Purchase",
        source="qbo_feed"
    )
    
    transaction = service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    categorize_data = BankTransactionCategorize(
        transaction_id=transaction.transaction_id,
        description="Starbucks Coffee",
        amount=150.0
    )
    
    updated_transaction = service.categorize_transaction(test_firm.firm_id, categorize_data)
    
    assert updated_transaction.transaction_id == transaction.transaction_id
    assert updated_transaction.suggestion_id is not None
    assert updated_transaction.confidence > 0.0
    assert updated_transaction.account_id == "6000-Expenses"

def test_create_transaction_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the POST /api/bank/transactions endpoint.
    """
    response = client.post(
        "/api/bank/transactions",
        json={
            "firm_id": test_firm.firm_id,
            "client_id": test_client.client_id,
            "amount": 150.0,
            "date": datetime.utcnow().isoformat(),
            "description": "Starbucks Purchase",
            "source": "qbo_feed"
        },
        params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["firm_id"] == test_firm.firm_id
    assert data["client_id"] == test_client.client_id
    assert data["amount"] == 150.0

def test_list_transactions_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the GET /api/bank/transactions endpoint.
    """
    # Create a transaction
    service = BankTransactionService(db)
    transaction_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=150.0,
        date=datetime.utcnow(),
        description="Starbucks Purchase",
        source="qbo_feed"
    )
    service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    response = client.get(
        "/api/bank/transactions",
        params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["firm_id"] == test_firm.firm_id
    assert data[0]["client_id"] == test_client.client_id

def test_categorize_transaction_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the POST /api/bank/transactions/categorize endpoint.
    """
    service = BankTransactionService(db)
    transaction_data = BankTransactionCreate(
        firm_id=test_firm.firm_id,
        amount=150.0,
        date=datetime.utcnow(),
        description="Starbucks Purchase",
        source="qbo_feed"
    )
    transaction = service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    response = client.post(
        "/api/bank/transactions/categorize",
        json={
            "transaction_id": transaction.transaction_id,
            "description": "Starbucks Coffee",
            "amount": 150.0
        },
        params={"firm_id": test_firm.firm_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == transaction.transaction_id
    assert data["account_id"] == "6000-Expenses"