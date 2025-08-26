"""
Preamble: Tests for PayrollService and routes in Stage 1D of the Escher project.
Includes unit and integration tests for payroll batch/remittance creation, listing, and reconciliation.
References: Stage 1D requirements, tests/conftest.py, services/payroll.py.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from domains.payroll.services.payroll import PayrollService
from domains.bank.services.bank_transaction import BankTransactionService
from domains.payroll.schemas.payroll import PayrollBatchCreate, PayrollRemittanceCreate
from domains.bank.schemas.bank_transaction import BankTransactionCreate
from datetime import datetime, timedelta

def test_create_batch(mock_qbo, db: Session, test_firm, test_client):
    """
    Test creating a payroll batch with tenant isolation.
    """
    service = PayrollService(db)
    batch_data = PayrollBatchCreate(
        total_amount=5000.0,
        payroll_date=datetime.utcnow(),
        period_start=datetime.utcnow() - timedelta(days=14),
        period_end=datetime.utcnow(),
        description="Bi-weekly payroll"
    )
    
    batch = service.create_batch(batch_data, test_firm.firm_id, test_client.client_id)
    
    assert batch.firm_id == test_firm.firm_id
    assert batch.client_id == test_client.client_id
    assert batch.total_amount == 5000.0
    assert batch.status == "pending"

def test_create_remittance(mock_qbo, db: Session, test_firm, test_client):
    """
    Test creating a payroll remittance with tenant isolation.
    """
    service = PayrollService(db)
    batch_data = PayrollBatchCreate(
        total_amount=5000.0,
        payroll_date=datetime.utcnow(),
        period_start=datetime.utcnow() - timedelta(days=14),
        period_end=datetime.utcnow(),
        description="Bi-weekly payroll"
    )
    batch = service.create_batch(batch_data, test_firm.firm_id, test_client.client_id)
    
    remittance_data = PayrollRemittanceCreate(
        batch_id=batch.batch_id,
        amount=1500.0,
        tax_agency="IRS",
        remittance_date=datetime.utcnow()
    )
    
    remittance = service.create_remittance(remittance_data, test_firm.firm_id)
    
    assert remittance.firm_id == test_firm.firm_id
    assert remittance.batch_id == batch.batch_id
    assert remittance.amount == 1500.0
    assert remittance.tax_agency == "IRS"
    assert remittance.status == "pending"

def test_reconcile_batch(mock_qbo, db: Session, test_firm, test_client):
    """
    Test reconciling a payroll batch with bank transactions.
    """
    payroll_service = PayrollService(db)
    bank_service = BankTransactionService(db)
    
    # Create payroll batch
    batch_data = PayrollBatchCreate(
        total_amount=5000.0,
        payroll_date=datetime.utcnow(),
        period_start=datetime.utcnow() - timedelta(days=14),
        period_end=datetime.utcnow(),
        description="Bi-weekly payroll"
    )
    batch = payroll_service.create_batch(batch_data, test_firm.firm_id, test_client.client_id)
    
    # Create remittances
    remittance_data = PayrollRemittanceCreate(
        batch_id=batch.batch_id,
        amount=1500.0,
        tax_agency="IRS",
        remittance_date=datetime.utcnow()
    )
    payroll_service.create_remittance(remittance_data, test_firm.firm_id)
    
    # Create matching bank transaction
    transaction_data = BankTransactionCreate(
        amount=1500.0,
        date=datetime.utcnow(),
        description="Payroll Tax Payment",
        source="qbo_feed"
    )
    bank_service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    # Reconcile batch
    reconciled_batch = payroll_service.reconcile_batch(test_firm.firm_id, batch.batch_id, test_client.client_id)
    
    assert reconciled_batch["status"] == "unmatched"  # Only 1500 matched out of 5000
    remittances = payroll_service.list_remittances(test_firm.firm_id, batch.batch_id)
    assert remittances[0].status == "reconciled"
    assert remittances[0].transaction_id is not None

def test_create_batch_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the POST /api/payroll/batches endpoint.
    """
    response = client.post(
        "/api/payroll/batches",
        json={
            "total_amount": 5000.0,
            "payroll_date": datetime.utcnow().isoformat(),
            "period_start": (datetime.utcnow() - timedelta(days=14)).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "description": "Bi-weekly payroll"
        },
        params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["firm_id"] == test_firm.firm_id
    assert data["client_id"] == test_client.client_id
    assert data["total_amount"] == 5000.0

def test_create_remittance_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the POST /api/payroll/remittances endpoint.
    """
    payroll_service = PayrollService(db)
    batch_data = PayrollBatchCreate(
        total_amount=5000.0,
        payroll_date=datetime.utcnow(),
        period_start=datetime.utcnow() - timedelta(days=14),
        period_end=datetime.utcnow(),
        description="Bi-weekly payroll"
    )
    batch = payroll_service.create_batch(batch_data, test_firm.firm_id, test_client.client_id)
    
    response = client.post(
        "/api/payroll/remittances",
        json={
            "batch_id": batch.batch_id,
            "amount": 1500.0,
            "tax_agency": "IRS",
            "remittance_date": datetime.utcnow().isoformat()
        },
        params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["firm_id"] == test_firm.firm_id
    assert data["batch_id"] == batch.batch_id
    assert data["amount"] == 1500.0

def test_reconcile_batch_api(client: TestClient, db: Session, test_firm, test_client, mock_qbo):
    """
    Test the POST /api/payroll/reconcile/{batch_id} endpoint.
    """
    payroll_service = PayrollService(db)
    bank_service = BankTransactionService(db)
    
    batch_data = PayrollBatchCreate(
        total_amount=5000.0,
        payroll_date=datetime.utcnow(),
        period_start=datetime.utcnow() - timedelta(days=14),
        period_end=datetime.utcnow(),
        description="Bi-weekly payroll"
    )
    batch = payroll_service.create_batch(batch_data, test_firm.firm_id, test_client.client_id)
    
    remittance_data = PayrollRemittanceCreate(
        batch_id=batch.batch_id,
        amount=1500.0,
        tax_agency="IRS",
        remittance_date=datetime.utcnow()
    )
    payroll_service.create_remittance(remittance_data, test_firm.firm_id)
    
    transaction_data = BankTransactionCreate(
        amount=1500.0,
        date=datetime.utcnow(),
        description="Payroll Tax Payment",
        source="qbo_feed"
    )
    bank_service.create_transaction(transaction_data, test_firm.firm_id, test_client.client_id)
    
    response = client.post(
        f"/api/payroll/batches/{batch.batch_id}/reconcile",
        params={"firm_id": test_firm.firm_id, "client_id": test_client.client_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == batch.batch_id
    assert data["status"] == "unmatched"