"""
BillService - Complete Bill Lifecycle Management

Handles the complete lifecycle of bills from ingestion through payment:
- Bill ingestion from QBO and document upload
- Approval workflow management
- Payment scheduling and coordination
- Runway reserve integration
- QBO synchronization

Enhanced from basic BillIngestionService to include comprehensive functionality.
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
from infra.qbo.smart_sync import SmartSyncService
from common.exceptions import ValidationError

logger = logging.getLogger(__name__)


class BillApprovalRules:
    """Business rules for bill approval thresholds."""
    AUTO_APPROVAL_THRESHOLD = 1000.0  # Bills over $1000 require approval


class BillService(TenantAwareService):
    """
    Comprehensive service for managing bill lifecycle from ingestion to payment.
    
    Enhanced from BillIngestionService to include modern architecture patterns:
    - Tenant isolation (ADR-003)
    - Provider pattern (ADR-002)
    - Comprehensive business logic
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
        
        # Use SmartSyncService for QBO operations
        self.smart_sync = SmartSyncService(business_id, "", self.db)
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
    
    async def sync_bills_from_qbo(self, days_back: int = 90) -> List[Bill]:
        """Sync bills from QBO for the specified time period."""
        try:
            logger.info(f"Syncing bills from QBO for business {self.business_id}, {days_back} days back")
            
            # Get bills from QBO using SmartSyncService
            since_date = datetime.utcnow() - timedelta(days=days_back)
            qbo_bills = await self.smart_sync.get_bills()
            
            synced_bills = []
            for qbo_bill_data in qbo_bills:
                bill = self._process_qbo_bill(qbo_bill_data)
                if bill:
                    synced_bills.append(bill)
            
            self.db.commit()
            logger.info(f"Successfully synced {len(synced_bills)} bills from QBO")
            return synced_bills
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"QBO bill sync failed: {str(e)}")
            raise ValidationError(f"QBO sync failed: {str(e)}")
    
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
            vendor_id = self._get_or_create_vendor_from_qbo_data(qbo_bill_data)
            
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

    # ==================== BILL BUSINESS LOGIC ====================
    
    def calculate_bill_priority(self, bill: Bill) -> str:
        """Calculate bill priority using centralized PriorityCalculationService."""
        from runway.core.priority_calculation_service import PriorityCalculationService
        
        # Convert bill to dictionary format for priority calculation
        bill_data = {
            'amount': float(bill.amount) if bill.amount else 0.0,
            'due_date': bill.due_date.isoformat() if bill.due_date else None,
            'is_overdue': self.is_bill_overdue(bill),
            'days_until_due': self.get_days_until_due(bill),
            'status': bill.status.value if hasattr(bill.status, 'value') else str(bill.status)
        }
        
        # Use centralized priority calculation service
        priority_service = PriorityCalculationService(self.db, self.business_id, validate_business=False)
        score = priority_service.calculate_bill_priority_score(bill_data)
        
        # Convert score to priority enum
        if score >= 80:
            return BillPriority.URGENT
        elif score >= 40:
            return BillPriority.HIGH
        elif score >= 15:
            return BillPriority.MEDIUM
        else:
            return BillPriority.LOW

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

    def calculate_latest_safe_pay_date(self, bill: Bill, grace_days: int = 5) -> Optional[datetime]:
        """
        Calculate the latest safe payment date for a bill.

        This is a "smart" feature that considers:
        - Bill due date
        - Vendor-specific payment terms (future enhancement)
        - A configurable grace period to avoid late fees
        - Vendor relationship health (future enhancement)
        """
        if not bill.due_date:
            return None

        # Simple logic for now: due date + grace period
        # Future: Enhance with vendor-specific terms from Vendor model
        latest_safe_date = bill.due_date + timedelta(days=grace_days)
        
        return latest_safe_date

    # REMOVED: get_runway_impact_suggestion() - This belongs in runway/ services, not domains/
    # Runway impact calculations should be handled by RunwayCalculationService or BillImpactCalculator

    def can_bill_be_approved(self, bill: Bill) -> bool:
        """Check if bill can be approved."""
        return bill.status in [BillStatus.PENDING, BillStatus.REVIEW] and bill.requires_approval
    
    def approve_bill_entity(self, bill: Bill, approved_by_user_id: str, notes: str = None) -> bool:
        """Approve the bill entity (business logic extracted from model)."""
        if not self.can_bill_be_approved(bill):
            return False
        
        bill.status = BillStatus.APPROVED
        bill.approval_status = "approved"
        bill.approved_by = approved_by_user_id
        bill.approved_at = datetime.utcnow()
        bill.approval_notes = notes
        bill.updated_at = datetime.utcnow()
        return True
    
    def schedule_bill_payment(self, bill: Bill, payment_date: datetime, 
                             payment_method: str = None, payment_account: str = None) -> bool:
        """Schedule the bill for payment (business logic extracted from model)."""
        if bill.status != BillStatus.APPROVED:
            return False
        
        bill.status = BillStatus.SCHEDULED
        bill.scheduled_payment_date = payment_date
        bill.payment_method = payment_method
        bill.payment_account = payment_account
        bill.updated_at = datetime.utcnow()
        return True
    
    def _bill_to_dict(self, bill: Bill) -> Dict[str, Any]:
        """Convert bill to dictionary for API responses."""
        latest_safe_pay_date = self.calculate_latest_safe_pay_date(bill)
        # runway_impact removed - belongs in runway/ services
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
            'priority': bill.priority or self.calculate_bill_priority(bill),
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
            'latest_safe_pay_date': latest_safe_pay_date.isoformat() if latest_safe_pay_date else None,
            # 'runway_impact_suggestion' removed - belongs in runway/ services
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
            vendor = self._find_vendor_by_name(extracted_data["vendor_name"])
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
    
    def _find_vendor_by_name(self, vendor_name: str) -> Optional[Vendor]:
        """Find vendor by name with fuzzy matching."""
        return self._base_query(Vendor).filter(
            Vendor.name.ilike(f"%{vendor_name}%")
        ).first()
    
    def _get_or_create_vendor_from_qbo_data(self, qbo_bill_data: Dict[str, Any]) -> Optional[int]:
        """
        Extract vendor information from QBO bill data and create/find vendor in our database.
        
        Args:
            qbo_bill_data: QBO bill data containing vendor_ref
            
        Returns:
            vendor_id if found/created, None otherwise
        """
        try:
            vendor_ref = qbo_bill_data.get('vendor_ref', {})
            if not vendor_ref:
                return None
                
            vendor_name = vendor_ref.get('name')
            qbo_vendor_id = vendor_ref.get('value')
            
            if not vendor_name:
                return None
            
            # Try to find existing vendor by QBO ID first
            from domains.ap.models.vendor import Vendor
            vendor = self.db.query(Vendor).filter(
                Vendor.business_id == self.business_id,
                Vendor.qbo_vendor_id == qbo_vendor_id
            ).first()
            
            if vendor:
                return vendor.vendor_id
            
            # Try to find by name (fuzzy match)
            vendor = self._find_vendor_by_name(vendor_name)
            if vendor:
                # Update with QBO ID if found by name
                vendor.qbo_vendor_id = qbo_vendor_id
                self.db.flush()
                return vendor.vendor_id
            
            # Create new vendor
            vendor = Vendor(
                business_id=self.business_id,
                name=vendor_name,
                qbo_vendor_id=qbo_vendor_id,
                is_active=True
            )
            self.db.add(vendor)
            self.db.flush()
            
            logger.info(f"Created vendor {vendor.vendor_id}: {vendor_name} from QBO data")
            return vendor.vendor_id
            
        except Exception as e:
            logger.warning(f"Failed to create vendor from QBO data: {e}")
            return None

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
        # Find or create vendor
        vendor = self._find_or_create_vendor(qbo_bill_data.get("VendorRef"))
        
        # Create bill
        bill = Bill(
            business_id=self.business_id,
            vendor_id=vendor.vendor_id if vendor else None,
            qbo_bill_id=qbo_bill_data.get("Id"),
            qbo_sync_token=qbo_bill_data.get("SyncToken"),
            bill_number=qbo_bill_data.get("DocNumber"),
            amount=Decimal(str(qbo_bill_data.get("TotalAmt", 0))),
            due_date=self._parse_qbo_date(qbo_bill_data.get("DueDate")),
            issue_date=self._parse_qbo_date(qbo_bill_data.get("TxnDate")),
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
    
    def _find_or_create_vendor(self, vendor_ref: Dict) -> Optional[Vendor]:
        """Find existing vendor or create new one from QBO vendor reference."""
        if not vendor_ref:
            return None
        
        qbo_vendor_id = vendor_ref.get("value")
        vendor_name = vendor_ref.get("name")
        
        # Try to find existing vendor
        vendor = self.db.query(Vendor).filter(
            Vendor.business_id == self.business_id,
            Vendor.qbo_vendor_id == qbo_vendor_id
        ).first()
        
        if not vendor and vendor_name:
            # Create new vendor
            vendor = Vendor(
                business_id=self.business_id,
                qbo_vendor_id=qbo_vendor_id,
                name=vendor_name,
                is_active=True
            )
            self.db.add(vendor)
            self.db.flush()
        
        return vendor
    
    def _parse_qbo_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse QBO date string to datetime."""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                logger.warning(f"Could not parse QBO date: {date_str}")
                return None
