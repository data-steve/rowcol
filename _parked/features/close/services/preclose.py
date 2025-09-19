"""
Preamble: Implements services for the Close domain in Stage 2 of the Escher project.
Handles pre-close checks, PBC tracking, client communications, and client portal.
References: Stage 2 requirements, domains/bank/models/bank_transaction.py, domains/payroll/models/payroll.py, domains/core/services/task.py.
"""
from sqlalchemy.orm import Session
from domains.close.models.preclose import PreCloseCheck as PreCloseCheckModel, Exception as ExceptionModel, PBCRequest as PBCRequestModel, CloseChecklist as CloseChecklistModel
from domains.bank.models.bank_transaction import BankTransaction as BankTransactionModel
from domains.payroll.models.payroll import PayrollBatch as PayrollBatchModel
from domains.core.models.task import Task as TaskModel
from domains.close.schemas.preclose import Exception, PBCRequestCreate, KPIResponse
from domains.bank.services.bank_transaction import BankTransactionService
from domains.payroll.services.payroll import PayrollService
from domains.core.services.task import TaskService

from domains.core.models.user import User as UserModel
from domains.core.schemas.task import TaskCreate
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib

class PreCloseService:
    def __init__(self, db: Session):
        self.db = db
        self.bank_service = BankTransactionService(db)
        self.payroll_service = PayrollService(db)

    def run_checks(self, firm_id: str, client_id: Optional[int], period: datetime) -> List[PreCloseCheckModel]:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            checks = []
            # Bank reconciliation check
            bank_check = PreCloseCheckModel(
                firm_id=firm_id,
                client_id=client_id,
                period=period,
                type="bank_rec",
                status="pending",
                evidence_refs=[]
            )
            transactions = self.db.query(BankTransactionModel).filter(
                BankTransactionModel.firm_id == firm_id,
                BankTransactionModel.client_id == client_id,
                BankTransactionModel.date.between(period - timedelta(days=30), period)
            ).all()
            bank_check.status = "pass" if all(t.status == "reconciled" for t in transactions) else "fail"
            self.db.add(bank_check)
            checks.append(bank_check)

            # PBC completeness check
            pbc_check = PreCloseCheckModel(
                firm_id=firm_id,
                client_id=client_id,
                period=period,
                type="pbc_complete",
                status="pending",
                evidence_refs=[]
            )
            pbc_requests = self.db.query(PBCRequestModel).filter(
                PBCRequestModel.firm_id == firm_id,
                PBCRequestModel.client_id == client_id,
                PBCRequestModel.period == period
            ).all()
            pbc_check.status = "pass" if all(r.status == "received" for r in pbc_requests) else "fail"
            self.db.add(pbc_check)
            checks.append(pbc_check)

            # Flag exceptions for failed checks
            if bank_check.status == "fail":
                exception = ExceptionModel(
                    firm_id=firm_id,
                    client_id=client_id,
                    period=period,
                    type="unmatched_txn",
                    description=f"Unmatched bank transactions for period {period}",
                    resolution=None
                )
                self.db.add(exception)
            if pbc_check.status == "fail":
                exception = ExceptionModel(
                    firm_id=firm_id,
                    client_id=client_id,
                    period=period,
                    type="missing_pbc",
                    description=f"Missing PBC items for period {period}",
                    resolution=None
                )
                self.db.add(exception)

            self.db.commit()
            return checks
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Check execution failed: {str(e)}")

    def resolve_exception(self, firm_id: str, exception_id: int, resolution: str) -> ExceptionModel:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            exception = self.db.query(ExceptionModel).filter(
                ExceptionModel.exception_id == exception_id,
                ExceptionModel.firm_id == firm_id
            ).first()
            if not exception:
                raise ValueError("Exception not found or does not belong to firm")
            exception.resolution = resolution
            self.db.commit()
            self.db.refresh(exception)
            return exception
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Exception resolution failed: {str(e)}")

class PBCTrackerService:
    def __init__(self, db: Session):
        self.db = db
        self.task_service = TaskService(db)

    def create_pbc_request(self, pbc_data: PBCRequestCreate, firm_id: str, client_id: Optional[int] = None) -> PBCRequestModel:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            db_pbc = PBCRequestModel(
                firm_id=firm_id,
                client_id=client_id,
                period=pbc_data.period,
                item_type=pbc_data.item_type,
                owner=pbc_data.owner,
                due_date=pbc_data.due_date,
                status="pending",
                reminders=[]
            )
            # Create linked task with required fields
            task_data = TaskCreate(
                firm_id=firm_id,
                engagement_id=1,  # Default engagement ID
                client_id=client_id or 1,
                service_id=1,  # Default service ID
                type="pbc_collection",
                status="pending",
                due_date=pbc_data.due_date,
                priority="medium",
                completion_level=0.0,
                priority_score=0.5,
                estimated_hours=1.0,
                automation_eligibility="manual"
            )
            task = self.task_service.create_task(task_data)
            db_pbc.task_id = task.task_id
            self.db.add(db_pbc)
            self.db.commit()
            self.db.refresh(db_pbc)
            return db_pbc
        except (ValueError, TypeError) as e:
            self.db.rollback()
            raise ValueError(f"PBC request creation failed: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error in PBC request creation: {str(e)}")

    def update_pbc_status(self, firm_id: str, request_id: int, status: str) -> PBCRequestModel:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            pbc = self.db.query(PBCRequestModel).filter(
                PBCRequestModel.request_id == request_id,
                PBCRequestModel.firm_id == firm_id
            ).first()
            if not pbc:
                raise ValueError("PBC request not found or does not belong to firm")
            pbc.status = status
            if status == "received" and pbc.task_id:
                self.task_service.update_task_status(firm_id, pbc.task_id, "completed")
            self.db.commit()
            self.db.refresh(pbc)
            return pbc
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"PBC status update failed: {str(e)}")

    def compute_readiness_score(self, firm_id: str, client_id: Optional[int], period: datetime) -> KPIResponse:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            transactions = self.db.query(BankTransactionModel).filter(
                BankTransactionModel.firm_id == firm_id,
                BankTransactionModel.client_id == client_id,
                BankTransactionModel.date.between(period - timedelta(days=30), period)
            ).all()
            payroll_batches = self.db.query(PayrollBatchModel).filter(
                PayrollBatchModel.firm_id == firm_id,
                PayrollBatchModel.client_id == client_id,
                PayrollBatchModel.period_start <= period,
                PayrollBatchModel.period_end >= period
            ).all()
            pbc_requests = self.db.query(PBCRequestModel).filter(
                PBCRequestModel.firm_id == firm_id,
                PBCRequestModel.client_id == client_id,
                PBCRequestModel.period == period
            ).all()
            exceptions = self.db.query(ExceptionModel).filter(
                ExceptionModel.firm_id == firm_id,
                ExceptionModel.client_id == client_id,
                ExceptionModel.period == period,
                ExceptionModel.resolution.is_(None)
            ).all()

            total_txns = len(transactions)
            reconciled_txns = sum(1 for t in transactions if t.status == "reconciled")
            total_batches = len(payroll_batches)
            reconciled_batches = sum(1 for b in payroll_batches if b.status == "reconciled")
            total_pbcs = len(pbc_requests)
            received_pbcs = sum(1 for p in pbc_requests if p.status == "received")
            unresolved_exceptions = len(exceptions)

            score = (
                (reconciled_txns / total_txns if total_txns else 1.0) * 0.4 +
                (reconciled_batches / total_batches if total_batches else 1.0) * 0.3 +
                (received_pbcs / total_pbcs if total_pbcs else 1.0) * 0.3
            ) * 100
            score = max(0, score - unresolved_exceptions * 5)

            return KPIResponse(
                score=round(score, 2),
                reconciled_transactions=reconciled_txns,
                total_transactions=total_txns,
                reconciled_batches=reconciled_batches,
                total_batches=total_batches,
                received_pbcs=received_pbcs,
                total_pbcs=total_pbcs,
                unresolved_exceptions=unresolved_exceptions
            )
        except Exception as e:
            raise ValueError(f"Readiness score computation failed: {str(e)}")

class ClientCommsService:
    def __init__(self, db: Session):
        self.db = db

    def send_pbc_reminder(self, firm_id: str, request_id: int) -> None:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            pbc = self.db.query(PBCRequestModel).filter(
                PBCRequestModel.request_id == request_id,
                PBCRequestModel.firm_id == firm_id
            ).first()
            if not pbc:
                raise ValueError("PBC request not found or does not belong to firm")
            print(f"Sending reminder for PBC {request_id} to {pbc.owner}")
            pbc.reminders.append(datetime.utcnow())
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"PBC reminder failed: {str(e)}")

class ClientPortalService:
    def __init__(self, db: Session):
        self.db = db
        self.task_service = TaskService(db)
        self.pbc_service = PBCTrackerService(db)

    def login(self, firm_id: str, email: str, password: str) -> dict:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            user = self.db.query(UserModel).filter(
                UserModel.email == email,
                UserModel.firm_id == firm_id
            ).first()
            if not user or user.password_hash != hashlib.sha256(password.encode()).hexdigest():
                raise ValueError("Invalid credentials")
            if user.role != "client":
                raise ValueError("User is not a client")
            return {"firm_id": user.firm_id, "client_id": user.client_id, "token": "mock_jwt_token"}
        except Exception as e:
            raise ValueError(f"Login failed: {str(e)}")

    def upload_pbc(self, firm_id: str, request_id: int, file_path: str) -> PBCRequestModel:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            pbc = self.db.query(PBCRequestModel).filter(
                PBCRequestModel.request_id == request_id,
                PBCRequestModel.firm_id == firm_id
            ).first()
            if not pbc:
                raise ValueError("PBC request not found or does not belong to firm")
            # For now, just update the status without document storage
            # TODO: Implement proper document storage integration
            pbc.status = "received"
            pbc.evidence_refs = [f"file_{request_id}"]  # Placeholder
            self.db.commit()
            self.db.refresh(pbc)
            return pbc
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"PBC upload failed: {str(e)}")

    def get_status(self, firm_id: str, client_id: Optional[int], period: datetime) -> dict:
        if not firm_id:
            raise ValueError("firm_id is required")
        try:
            checklist = self.db.query(CloseChecklistModel).filter(
                CloseChecklistModel.firm_id == firm_id,
                CloseChecklistModel.client_id == client_id,
                CloseChecklistModel.period == period
            ).first()
            tasks = self.db.query(TaskModel).filter(
                TaskModel.firm_id == firm_id,
                TaskModel.client_id == client_id,
                TaskModel.due_date.between(period - timedelta(days=30), period)
            ).all()
            readiness = self.pbc_service.compute_readiness_score(firm_id, client_id, period)
            return {
                "checklist_status": checklist.status if checklist else "open",
                "readiness_score": readiness,
                "tasks": [{"task_id": t.task_id, "description": t.description, "status": t.status} for t in tasks]
            }
        except Exception as e:
            raise ValueError(f"Status retrieval failed: {str(e)}")
