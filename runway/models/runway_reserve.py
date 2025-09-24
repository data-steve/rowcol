"""
RunwayReserve Model - Cash Runway Reserve Management

This model handles the core business logic for cash runway reserves:
- Reserved vs Available cash calculations
- Runway extension through reserves
- Reserve allocation and release workflows
- Integration with QBO account balances

Business Context:
- Businesses need to earmark cash for specific purposes (taxes, payroll, equipment)
- Reserved cash should not be counted toward operational runway
- Reserves can be allocated to specific bills or future expenses
- Reserve utilization affects runway calculations in real-time
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from enum import Enum

from domains.core.models.base import Base, TimestampMixin, TenantMixin

class ReserveType(Enum):
    """Types of runway reserves."""
    TAX_RESERVE = "tax_reserve"           # Set aside for quarterly/annual taxes
    PAYROLL_RESERVE = "payroll_reserve"   # Emergency payroll coverage
    EQUIPMENT_RESERVE = "equipment_reserve" # Planned equipment purchases
    EMERGENCY_RESERVE = "emergency_reserve" # General emergency fund
    SEASONAL_RESERVE = "seasonal_reserve"  # Seasonal cash flow management
    DEBT_RESERVE = "debt_reserve"         # Loan payments and debt service
    CUSTOM_RESERVE = "custom_reserve"     # User-defined reserve categories

class ReserveStatus(Enum):
    """Reserve allocation status."""
    ACTIVE = "active"           # Reserve is active and reducing available cash
    ALLOCATED = "allocated"     # Reserve is allocated to specific expense
    RELEASED = "released"       # Reserve has been released back to available cash
    UTILIZED = "utilized"       # Reserve has been used for its intended purpose
    EXPIRED = "expired"         # Reserve has expired (time-based reserves)

class RunwayReserve(Base):
    """
    Runway Reserve Model
    
    Represents cash reserves that are earmarked for specific purposes
    and should not be counted toward operational runway calculations.
    """
    __tablename__ = "runway_reserves"
    
    # Primary identifiers
    reserve_id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    
    # Reserve details
    name = Column(String(255), nullable=False)  # User-friendly name
    description = Column(Text)                   # Optional description
    reserve_type = Column(String(50), nullable=False)  # ReserveType enum value
    status = Column(String(50), default=ReserveStatus.ACTIVE.value)
    
    # Financial amounts (stored as cents to avoid floating point issues)
    target_amount_cents = Column(Integer, nullable=False)  # Target reserve amount
    current_amount_cents = Column(Integer, default=0)      # Current reserved amount
    allocated_amount_cents = Column(Integer, default=0)    # Amount allocated to specific expenses
    
    # Time-based reserves
    target_date = Column(DateTime)               # When reserve should be fully funded
    expiry_date = Column(DateTime)              # When reserve expires (optional)
    
    # QBO integration
    qbo_account_id = Column(String(50))         # QBO account holding the reserve
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36), ForeignKey("users.user_id"))
    
    # Relationships
    business = relationship("domains.core.models.business.Business", backref="runway_reserves")
    reserve_transactions = relationship("ReserveTransaction", back_populates="reserve")
    reserve_allocations = relationship("ReserveAllocation", back_populates="reserve")
    
    # Hybrid properties for decimal conversion
    @hybrid_property
    def target_amount(self) -> Decimal:
        """Target reserve amount in dollars."""
        return Decimal(self.target_amount_cents) / 100
    
    @target_amount.setter
    def target_amount(self, value: Decimal):
        """Set target amount from decimal dollars."""
        self.target_amount_cents = int(value * 100)
    
    @hybrid_property
    def current_amount(self) -> Decimal:
        """Current reserve amount in dollars."""
        return Decimal(self.current_amount_cents) / 100
    
    @current_amount.setter
    def current_amount(self, value: Decimal):
        """Set current amount from decimal dollars."""
        self.current_amount_cents = int(value * 100)
    
    @hybrid_property
    def allocated_amount(self) -> Decimal:
        """Allocated reserve amount in dollars."""
        return Decimal(self.allocated_amount_cents) / 100
    
    @allocated_amount.setter  
    def allocated_amount(self, value: Decimal):
        """Set allocated amount from decimal dollars."""
        self.allocated_amount_cents = int(value * 100)
    
    @hybrid_property
    def available_amount(self) -> Decimal:
        """Available (unallocated) reserve amount."""
        return self.current_amount - self.allocated_amount
    
    @hybrid_property
    def funding_progress(self) -> float:
        """Percentage of target amount currently funded (0.0 to 1.0)."""
        if self.target_amount_cents == 0:
            return 1.0
        return float(self.current_amount_cents) / float(self.target_amount_cents)
    
    @hybrid_property
    def is_fully_funded(self) -> bool:
        """Whether the reserve has reached its target amount."""
        return self.current_amount_cents >= self.target_amount_cents
    
    @hybrid_property
    def funding_deficit(self) -> Decimal:
        """Amount still needed to reach target."""
        deficit_cents = max(0, self.target_amount_cents - self.current_amount_cents)
        return Decimal(deficit_cents) / 100
    
    def calculate_monthly_funding_needed(self) -> Decimal:
        """Calculate monthly funding needed to reach target by target_date."""
        if not self.target_date or self.is_fully_funded:
            return Decimal('0.00')
        
        months_remaining = max(1, (self.target_date - datetime.utcnow()).days / 30.44)  # Average days per month
        return self.funding_deficit / Decimal(str(months_remaining))
    
    def can_allocate(self, amount: Decimal) -> bool:
        """Check if amount can be allocated from available reserves."""
        return self.available_amount >= amount
    
    def allocate(self, amount: Decimal, purpose: str = None) -> bool:
        """Allocate reserve amount for specific purpose."""
        if not self.can_allocate(amount):
            return False
        
        self.allocated_amount += amount
        self.updated_at = datetime.utcnow()
        return True
    
    def release(self, amount: Decimal = None) -> Decimal:
        """Release allocated amount back to available reserves."""
        if amount is None:
            amount = self.allocated_amount
        
        release_amount = min(amount, self.allocated_amount)
        self.allocated_amount -= release_amount
        self.updated_at = datetime.utcnow()
        return release_amount
    
    def utilize(self, amount: Decimal) -> bool:
        """Utilize reserve for its intended purpose."""
        if amount > self.current_amount:
            return False
        
        # Reduce both current and allocated amounts
        utilization_from_allocated = min(amount, self.allocated_amount)
        utilization_from_available = amount - utilization_from_allocated
        
        self.allocated_amount -= utilization_from_allocated
        self.current_amount -= amount
        self.updated_at = datetime.utcnow()
        
        # Update status if fully utilized
        if self.current_amount == Decimal('0.00'):
            self.status = ReserveStatus.UTILIZED.value
        
        return True
    
    def get_impact_on_runway(self) -> Dict[str, Any]:
        """Calculate impact of this reserve on runway calculations."""
        return {
            'reduces_available_cash': float(self.current_amount),
            'monthly_funding_required': float(self.calculate_monthly_funding_needed()),
            'affects_monthly_burn': float(self.calculate_monthly_funding_needed()),
            'reserve_type': self.reserve_type,
            'funding_progress': self.funding_progress,
            'is_critical': self.reserve_type in [
                ReserveType.TAX_RESERVE.value, 
                ReserveType.PAYROLL_RESERVE.value
            ]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reserve to dictionary for API responses."""
        return {
            'reserve_id': self.reserve_id,
            'business_id': self.business_id,
            'name': self.name,
            'description': self.description,
            'reserve_type': self.reserve_type,
            'status': self.status,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'allocated_amount': float(self.allocated_amount),
            'available_amount': float(self.available_amount),
            'funding_progress': self.funding_progress,
            'is_fully_funded': self.is_fully_funded,
            'funding_deficit': float(self.funding_deficit),
            'monthly_funding_needed': float(self.calculate_monthly_funding_needed()),
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'runway_impact': self.get_impact_on_runway()
        }

class ReserveTransaction(Base):
    """
    Reserve Transaction Model
    
    Tracks all movements in and out of reserves for audit trail.
    """
    __tablename__ = "reserve_transactions"
    
    transaction_id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    reserve_id = Column(String(36), ForeignKey("runway_reserves.reserve_id"), nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # 'deposit', 'withdrawal', 'allocation', 'release'
    amount_cents = Column(Integer, nullable=False)         # Amount in cents
    description = Column(Text)
    
    # QBO integration
    qbo_transaction_id = Column(String(50))               # Related QBO transaction
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(36), ForeignKey("users.user_id"))
    
    # Relationships
    reserve = relationship("RunwayReserve", back_populates="reserve_transactions")
    
    @hybrid_property
    def amount(self) -> Decimal:
        """Transaction amount in dollars."""
        return Decimal(self.amount_cents) / 100
    
    @amount.setter
    def amount(self, value: Decimal):
        """Set amount from decimal dollars."""
        self.amount_cents = int(value * 100)

class ReserveAllocation(Base):
    """
    Reserve Allocation Model
    
    Tracks specific allocations of reserves to bills or future expenses.
    """
    __tablename__ = "reserve_allocations"
    
    allocation_id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    reserve_id = Column(String(36), ForeignKey("runway_reserves.reserve_id"), nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    
    # Allocation details
    allocated_amount_cents = Column(Integer, nullable=False)
    purpose = Column(String(255), nullable=False)         # What the allocation is for
    
    # Optional links to specific expenses
    bill_id = Column(String(50))                          # QBO bill ID if allocated to specific bill
    expense_category = Column(String(100))                # Expense category
    
    # Timeline
    allocation_date = Column(DateTime, default=datetime.utcnow)
    expected_utilization_date = Column(DateTime)          # When allocation will be used
    actual_utilization_date = Column(DateTime)            # When allocation was actually used
    
    # Status
    status = Column(String(50), default="allocated")      # 'allocated', 'utilized', 'released'
    
    # Relationships
    reserve = relationship("RunwayReserve", back_populates="reserve_allocations")
    
    @hybrid_property
    def allocated_amount(self) -> Decimal:
        """Allocated amount in dollars."""
        return Decimal(self.allocated_amount_cents) / 100
    
    @allocated_amount.setter
    def allocated_amount(self, value: Decimal):
        """Set allocated amount from decimal dollars."""
        self.allocated_amount_cents = int(value * 100)
