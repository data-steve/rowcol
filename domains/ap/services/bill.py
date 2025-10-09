"""
BillService - QBO-Honest Bill Management

Handles bill data operations that QBO actually supports:
- Bill sync from QBO (read-only)
- Basic CRUD operations on local copies
- Business logic and querying
- QBO synchronization

QBO is only a ledger rail - it cannot execute payments or create invoices.
Execution capabilities moved to _parked/ for future rail implementation.
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from fastapi import UploadFile, HTTPException

from domains.core.services.base_service import TenantAwareService
from domains.ap.models.bill import Bill, BillStatus, BillPriority
from domains.ap.models.vendor import Vendor
from domains.qbo.services.sync_service import QBOSyncService
from infra.qbo.qbo_mapper import QBOMapper
from infra.config.exceptions import ValidationError

logger = logging.getLogger(__name__)


class BillApprovalRules:
    """Business rules for bill approval thresholds."""
    AUTO_APPROVAL_THRESHOLD = 1000.0  # Bills over $1000 require approval


class BillService(TenantAwareService):
    """
    QBO-honest bill service for basic CRUD operations and QBO sync.
    
    This service only provides functionality that QBO actually supports:
    - Sync bills from QBO (read-only)
    - Basic CRUD on local copies
    - Business logic and querying
    
    Execution capabilities moved to _parked/:
    - Payment execution (moved to _parked/ap_execution/)
    - Bill approval (moved to _parked/ap_execution/)
    - Payment scheduling (moved to _parked/ap_execution/)
    """
    
    def __init__(self, db: Session, business_id: str, 
                 qbo_provider=None, document_processor=None, runway_reserve_service=None,
                 validate_business: bool = True):
        """
        Initialize bill service with tenant isolation.
        
        Args:
            db: Database session
            business_id: Business identifier for tenant isolation
            qbo_provider: Optional QBO provider (uses factory if None)
            document_processor: Optional document processor (uses factory if None)
            runway_reserve_service: Optional runway reserve service
            validate_business: Whether to validate business exists (default: True)
        """
        super().__init__(db, business_id, validate_business=validate_business)
        
        # Use QBOSyncService for QBO operations (Pattern 2: Domain Service → Infrastructure Service)
        self.qbo_sync = QBOSyncService(business_id, "", self.db)
        # self.document_processor = document_processor  # TODO: Implement when provider strategy decided
        self.document_processor = None  # Document processing not yet implemented
        self.runway_reserve_service = runway_reserve_service
        
        logger.info(f"Initialized BillService for business {business_id}")

    # ==================== SMART SYNC DATA METHODS ====================
    
    def get_payment_ready_bills(self, max_amount: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get bills that are ready for payment, with optional amount constraint.
        
        This method handles the database query and entity transformation.
        For priority calculations, use PaymentPriorityCalculator from runway/core/services.
        
        Args:
            max_amount: Maximum total amount to consider for payment (optional)
        
        Returns:
            List of bill dictionaries ready for payment prioritization
        """
        try:
            from domains.ap.models.bill import Bill, BillStatus
            
            bills = self.db.query(Bill).filter(
                Bill.business_id == self.business_id,
                Bill.status.in_([BillStatus.APPROVED, 'approved'])
            ).all()
            
            bill_dicts = [
                {
                    'qbo_id': bill.qbo_bill_id,
                    'amount': float(bill.amount_cents / 100) if bill.amount_cents else 0.0,
                    'due_date': bill.due_date.isoformat() if bill.due_date else None,
                    'vendor_id': bill.vendor_id,
                    'vendor_name': getattr(bill.vendor, 'name', 'Unknown') if hasattr(bill, 'vendor') and bill.vendor else 'Unknown',
                    'status': bill.status,
                    'bill_type': getattr(bill, 'bill_type', '')
                }
                for bill in bills
            ]
            
            # Apply amount constraint if specified
            if max_amount is not None:
                total = 0.0
                filtered = []
                # Sort by amount ascending to fit more bills within constraint
                bill_dicts.sort(key=lambda x: x['amount'])
                for bill in bill_dicts:
                    if total + bill['amount'] <= max_amount:
                        filtered.append(bill)
                        total += bill['amount']
                    else:
                        break
                return filtered
            
            return bill_dicts
            
        except Exception as e:
            logger.error(f"Failed to get payment-ready bills: {e}")
            return []
    
    def get_bills_due_in_days(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get bills due within specified number of days.
        
        This is the proper method for SmartSync to call instead of 
        duplicating business logic.
        """
        try:
            from datetime import datetime, timedelta
            
            due_cutoff = datetime.utcnow() + timedelta(days=days)
            bills = self.db.query(Bill).filter(
                Bill.business_id == self.business_id,
                Bill.due_date <= due_cutoff,
                Bill.status.in_([BillStatus.PENDING, BillStatus.APPROVED, "pending", "approved"])
            ).all()
            
            return [
                {
                    "qbo_id": bill.qbo_bill_id,
                    "vendor": bill.vendor.name if bill.vendor else "Unknown Vendor",
                    "vendor_id": bill.vendor_id,
                    "amount": float(bill.amount_cents / 100),  # Convert cents to dollars
                    "due_date": bill.due_date.isoformat() if bill.due_date else None,
                    "status": bill.status if isinstance(bill.status, str) else bill.status.value,
                    "balance": float(bill.amount_cents / 100)  # Simplified for now
                }
                for bill in bills
            ]
        except Exception as e:
            logger.error(f"Failed to get bills due in {days} days: {e}")
            return []
    
    def get_overdue_bills(self) -> List[Dict[str, Any]]:
        """Get overdue bills for collections."""
        try:
            today = datetime.utcnow()
            bills = self.db.query(Bill).filter(
                Bill.business_id == self.business_id,
                Bill.due_date < today,
                Bill.status.in_([BillStatus.PENDING, BillStatus.APPROVED, "pending", "approved"])
            ).all()
            
            return [
                {
                    "qbo_id": bill.qbo_bill_id,
                    "vendor": bill.vendor.name if bill.vendor else "Unknown Vendor",
                    "vendor_id": bill.vendor_id,
                    "amount": float(bill.amount_cents / 100),
                    "due_date": bill.due_date.isoformat() if bill.due_date else None,
                    "days_overdue": (today - bill.due_date).days if bill.due_date else 0,
                    "status": bill.status if isinstance(bill.status, str) else bill.status.value
                }
                for bill in bills
            ]
        except Exception as e:
            logger.error(f"Failed to get overdue bills: {e}")
            return []

    # ==================== BILL INGESTION ====================
    
    
    
    async def sync_bills_from_qbo(self) -> Dict[str, Any]:
        """Sync bills from QBO - Pattern 2: Domain Service → Infrastructure Service."""
        return await self.qbo_sync.get_bills()
    
    async def sync_bill_from_qbo(self, qbo_bill_id: str) -> Dict[str, Any]:
        """Sync single bill from QBO - Pattern 2: Domain Service → Infrastructure Service."""
        return await self.qbo_sync.get_bill(qbo_bill_id)
        
    async def process_bill(self, file: UploadFile, vendor_id: int = None):
        """Process uploaded bill document."""
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file data
        file_data = await file.read()
        
        # Use the document ingestion method
        bill = self.ingest_document(
            file_data=file_data,
            filename=file.filename,
            vendor_id=vendor_id
        )
        
        return {"status": "success", "bill_id": bill.bill_id}
    
    def ingest_document(self, file_data: bytes, filename: str, 
                       vendor_id: Optional[int] = None) -> Bill:
        """Ingest a bill document and extract bill data."""
        try:
            logger.info(f"Ingesting document {filename} for business {self.business_id}")
            
            # Process document to extract bill data
            extracted_data = self.document_processor.extract_bill_data(
                file_data, filename
            )
            
            # Create bill from extracted data
            bill = self._create_bill_from_document(extracted_data, vendor_id)
            
            self.db.commit()
            logger.info(f"Successfully ingested document as bill {bill.bill_id}")
            return bill
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Document ingestion failed: {str(e)}")
            raise ValidationError(f"Document ingestion failed: {str(e)}")
    
    def ingest_bill_from_qbo(self, business_id: str, qbo_bill_data: Dict[str, Any]) -> Bill:
        """
        Ingest a bill from QBO data structure into our database.
        
        Args:
            business_id: The ID of the business
            qbo_bill_data: Dictionary containing QBO bill data
        
        Returns:
            Bill: The created or updated bill object
        """
        try:
            qbo_id = qbo_bill_data.get('qbo_id')
            
            # Extract and create/find vendor from QBO vendor_ref
            vendor_service = self._get_vendor_service()
            vendor = vendor_service.get_or_create_vendor_from_qbo_data(qbo_bill_data)
            vendor_id = vendor.vendor_id if vendor else None
            
            bill = self.db.query(Bill).filter(
                Bill.qbo_bill_id == qbo_id,
                Bill.business_id == business_id
            ).first()
            
            if not bill:
                bill = Bill(
                    business_id=business_id,
                    qbo_bill_id=qbo_id,
                    amount_cents=int(qbo_bill_data.get('amount', 0) * 100),  # Convert dollars to cents
                    due_date=datetime.fromisoformat(qbo_bill_data.get('due_date')) if qbo_bill_data.get('due_date') else None,
                    status=BillStatus.PENDING if isinstance(qbo_bill_data.get('status'), str) else qbo_bill_data.get('status', BillStatus.PENDING),
                    vendor_id=vendor_id
                )
                self.db.add(bill)
            else:
                bill.amount_cents = int(qbo_bill_data.get('amount', 0) * 100)
                bill.due_date = datetime.fromisoformat(qbo_bill_data.get('due_date')) if qbo_bill_data.get('due_date') else None
                bill.status = BillStatus.PENDING if isinstance(qbo_bill_data.get('status'), str) else qbo_bill_data.get('status', BillStatus.PENDING)
                bill.vendor_id = vendor_id
            
            self.db.commit()
            self.db.refresh(bill)
            return bill
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to ingest bill from QBO: {e}")
            raise ValueError(f"Failed to ingest bill from QBO: {e}")

    
    def is_bill_overdue(self, bill: Bill) -> bool:
        """Check if bill is past due."""
        if not bill.due_date:
            return False
        return datetime.utcnow() > bill.due_date and bill.status not in [BillStatus.PAID, BillStatus.REJECTED]
    
    def get_days_until_due(self, bill: Bill) -> Optional[int]:
        """Get days until bill is due (negative if overdue)."""
        if not bill.due_date:
            return None
        delta = bill.due_date - datetime.utcnow()
        return delta.days


    # REMOVED: get_runway_impact_suggestion() - This belongs in runway/ services, not domains/
    # Runway impact calculations should be handled by RunwayCalculationService or BillImpactCalculator

    # REMOVED: Execution methods moved to _parked/ap_execution/bill_payment_service.py
    # - can_bill_be_approved() - moved to _parked/
    # - approve_bill_entity() - moved to _parked/
    # - schedule_bill_payment() - moved to _parked/
    
    # QBO-honest: Only provide data querying and business logic
    
    def get_payment_ready_bills_from_db(self) -> List[Dict[str, Any]]:
        """
        Get payment-ready bills from local database - Pattern 1 (Read Operations).
        
        This follows the correct data flow pattern:
        Domain Service → Local DB (mirrored data)
        """
        try:
            logger.info(f"Getting payment-ready bills from local DB for business {self.business_id}")
            return self.get_payment_ready_bills()
        except Exception as e:
            logger.error(f"Failed to get payment-ready bills from local DB: {e}")
            return []
    
    
    def _bill_to_dict(self, bill: Bill) -> Dict[str, Any]:
        """Convert bill to dictionary for API responses."""
        return {
            'bill_id': bill.bill_id,
            'business_id': bill.business_id,
            'vendor_id': bill.vendor_id,
            'qbo_bill_id': bill.qbo_bill_id,
            'bill_number': bill.bill_number,
            'amount': float(bill.amount),
            'due_date': bill.due_date.isoformat() if bill.due_date else None,
            'issue_date': bill.issue_date.isoformat() if bill.issue_date else None,
            'status': bill.status,
            'priority': bill.priority,  # Priority calculated elsewhere
            'approval_status': bill.approval_status,
            'approved_by': bill.approved_by,
            'approved_at': bill.approved_at.isoformat() if bill.approved_at else None,
            'scheduled_payment_date': bill.scheduled_payment_date.isoformat() if bill.scheduled_payment_date else None,
            'payment_method': bill.payment_method,
            'is_reserved': bill.is_reserved,
            'reserve_amount': float(bill.reserve_amount),
            'gl_account': bill.gl_account,
            'expense_category': bill.expense_category,
            'confidence': bill.confidence,
            'is_overdue': self.is_bill_overdue(bill),
            'days_until_due': self.get_days_until_due(bill),
            'requires_approval': bill.requires_approval,
            'description': bill.description,
            'tags': bill.tags,
            'created_at': bill.created_at.isoformat(),
            'updated_at': bill.updated_at.isoformat()
        }
    
    # ==================== UTILITY METHODS ====================
    
    def _get_bill_or_raise(self, bill_id: int) -> Bill:
        """Get bill by ID or raise ValidationError."""
        return self._get_by_id_or_raise(Bill, bill_id, f"Bill {bill_id} not found")
    
    def get_bill_by_qbo_id(self, qbo_id: str) -> Optional[Bill]:
        """Get bill by QBO ID for this business."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.qbo_bill_id == qbo_id
        ).first()
    
    def get_bill_by_id(self, bill_id: int) -> Optional[Bill]:
        """Get bill by internal ID for this business."""
        return self.db.query(Bill).filter(
            Bill.business_id == self.business_id,
            Bill.bill_id == bill_id
        ).first()
    
    def _create_bill_from_document(self, extracted_data: Dict, 
                                  vendor_id: Optional[int] = None) -> Bill:
        """Create Bill from document extraction data."""
        # Find vendor if not provided
        if not vendor_id and extracted_data.get("vendor_name"):
            vendor_service = self._get_vendor_service()
            vendor = vendor_service.find_vendor_by_name(extracted_data["vendor_name"])
            vendor_id = vendor.vendor_id if vendor else None
        
        # Create bill
        bill = Bill(
            business_id=self.business_id,
            vendor_id=vendor_id,
            bill_number=extracted_data.get("bill_number"),
            amount=Decimal(str(extracted_data.get("amount", 0))),
            due_date=extracted_data.get("due_date"),
            issue_date=extracted_data.get("issue_date"),
            status=BillStatus.REVIEW,  # Documents start in review
            description=extracted_data.get("description"),
            extracted_fields=extracted_data,
            confidence=extracted_data.get("confidence", 0.0)
        )
        
        # Set priority and approval requirements
        bill.priority = self.calculate_bill_priority(bill)
        bill.requires_approval = self._requires_approval(bill)
        
        self.db.add(bill)
        self.db.flush()
        
        return bill
    
    def _get_vendor_service(self):
        """Get VendorService instance for vendor operations."""
        from domains.ap.services.vendor import VendorService
        return VendorService(self.db, self.business_id)

    def _requires_approval(self, bill: Bill) -> bool:
        """Determine if a bill requires approval based on business rules."""
        if bill.amount >= Decimal(str(BillApprovalRules.AUTO_APPROVAL_THRESHOLD)):
            return True
        
        if bill.vendor and bill.vendor.is_critical:
            return True
        
        return False
    
    def _process_qbo_bill(self, qbo_bill_data: Dict) -> Optional[Bill]:
        """Process a single QBO bill and create/update local Bill record."""
        try:
            qbo_bill_id = qbo_bill_data.get("Id")
            
            # Check if bill already exists
            existing_bill = self.db.query(Bill).filter(
                Bill.business_id == self.business_id,
                Bill.qbo_bill_id == qbo_bill_id
            ).first()
            
            if existing_bill:
                # Update existing bill
                self._update_bill_from_qbo_data(existing_bill, qbo_bill_data)
                return existing_bill
            else:
                # Create new bill
                return self._create_bill_from_qbo_data(qbo_bill_data)
                
        except Exception as e:
            logger.error(f"Failed to process QBO bill {qbo_bill_data.get('Id')}: {str(e)}")
            return None
    
    def _create_bill_from_qbo_data(self, qbo_bill_data: Dict) -> Bill:
        """Create a new Bill from QBO data."""
        # Map QBO data to standardized format
        mapped_bill = QBOMapper.map_bill_data(qbo_bill_data)
        
        # Find or create vendor
        vendor_service = self._get_vendor_service()
        vendor = vendor_service.get_or_create_vendor_from_qbo_ref(qbo_bill_data.get("VendorRef"))
        
        # Create bill
        bill = Bill(
            business_id=self.business_id,
            vendor_id=vendor.vendor_id if vendor else None,
            qbo_bill_id=mapped_bill.get("qbo_id"),
            qbo_sync_token=mapped_bill.get("sync_token"),
            bill_number=mapped_bill.get("doc_number"),
            amount=Decimal(str(mapped_bill.get("amount", 0))),
            due_date=self._get_qbo_utils().parse_qbo_date(mapped_bill.get("due_date")),
            issue_date=self._get_qbo_utils().parse_qbo_date(mapped_bill.get("txn_date")),
            status=BillStatus.PENDING,
            description=qbo_bill_data.get("Memo"),
            qbo_last_sync=datetime.utcnow()
        )
        
        # Set priority based on amount and due date
        bill.priority = self.calculate_bill_priority(bill)
        
        # Determine if approval is required
        bill.requires_approval = self._requires_approval(bill)
        
        self.db.add(bill)
        self.db.flush()
        
        logger.info(f"Created new bill {bill.bill_id} from QBO bill {bill.qbo_bill_id}")
        return bill
    
    
    def _get_qbo_utils(self):
        """Get QBO utilities for QBO-specific operations."""
        from infra.qbo.utils import QBOUtils
        return QBOUtils
