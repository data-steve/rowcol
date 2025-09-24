"""
RunwayReserve Pydantic Schemas - API Validation and Serialization

These schemas handle API requests/responses for runway reserve management.
Separate from SQLAlchemy models to maintain clean API contracts.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from enum import Enum

class ReserveTypeEnum(str, Enum):
    """Reserve type enumeration for API."""
    TAX_RESERVE = "tax_reserve"
    PAYROLL_RESERVE = "payroll_reserve"
    EQUIPMENT_RESERVE = "equipment_reserve"
    EMERGENCY_RESERVE = "emergency_reserve"
    SEASONAL_RESERVE = "seasonal_reserve"
    DEBT_RESERVE = "debt_reserve"
    CUSTOM_RESERVE = "custom_reserve"

class ReserveStatusEnum(str, Enum):
    """Reserve status enumeration for API."""
    ACTIVE = "active"
    ALLOCATED = "allocated"
    RELEASED = "released"
    UTILIZED = "utilized"
    EXPIRED = "expired"

class RunwayReserveBase(BaseModel):
    """Base schema for runway reserves."""
    name: str = Field(..., min_length=1, max_length=255, description="Reserve name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    reserve_type: ReserveTypeEnum = Field(..., description="Type of reserve")
    target_amount: Decimal = Field(..., ge=0, description="Target reserve amount in dollars")
    target_date: Optional[datetime] = Field(None, description="Target funding date")
    expiry_date: Optional[datetime] = Field(None, description="Reserve expiry date")
    qbo_account_id: Optional[str] = Field(None, max_length=50, description="QBO account ID")

    @validator('target_amount')
    def validate_target_amount(cls, v):
        """Ensure target amount has at most 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError('Target amount cannot have more than 2 decimal places')
        return v

    @validator('target_date', 'expiry_date')
    def validate_dates(cls, v):
        """Ensure dates are in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError('Date must be in the future')
        return v

    @validator('expiry_date')
    def validate_expiry_after_target(cls, v, values):
        """Ensure expiry date is after target date."""
        if v and 'target_date' in values and values['target_date']:
            if v <= values['target_date']:
                raise ValueError('Expiry date must be after target date')
        return v

class RunwayReserveCreate(RunwayReserveBase):
    """Schema for creating new runway reserves."""
    business_id: str = Field(..., description="Business ID")
    initial_amount: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Initial funding amount")

class RunwayReserveUpdate(BaseModel):
    """Schema for updating existing runway reserves."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_amount: Optional[Decimal] = Field(None, ge=0)
    target_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    status: Optional[ReserveStatusEnum] = None

class RunwayReserve(RunwayReserveBase):
    """Schema for runway reserve responses."""
    reserve_id: str
    business_id: str
    status: ReserveStatusEnum
    current_amount: Decimal = Field(..., description="Current funded amount")
    allocated_amount: Decimal = Field(..., description="Currently allocated amount")
    available_amount: Decimal = Field(..., description="Available (unallocated) amount")
    funding_progress: float = Field(..., ge=0, le=1, description="Funding progress (0.0 to 1.0)")
    is_fully_funded: bool = Field(..., description="Whether reserve is fully funded")
    funding_deficit: Decimal = Field(..., ge=0, description="Amount still needed")
    monthly_funding_needed: Decimal = Field(..., ge=0, description="Monthly funding needed to reach target")
    created_at: datetime
    updated_at: datetime
    runway_impact: Dict[str, Any] = Field(..., description="Impact on runway calculations")

    class Config:
        from_attributes = True

class ReserveTransactionBase(BaseModel):
    """Base schema for reserve transactions."""
    transaction_type: str = Field(..., description="Transaction type")
    amount: Decimal = Field(..., description="Transaction amount in dollars")
    description: Optional[str] = Field(None, max_length=1000, description="Transaction description")

class ReserveTransactionCreate(ReserveTransactionBase):
    """Schema for creating reserve transactions."""
    reserve_id: str = Field(..., description="Reserve ID")

class ReserveTransaction(ReserveTransactionBase):
    """Schema for reserve transaction responses."""
    transaction_id: str
    reserve_id: str
    business_id: str
    qbo_transaction_id: Optional[str]
    created_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

class ReserveAllocationBase(BaseModel):
    """Base schema for reserve allocations."""
    allocated_amount: Decimal = Field(..., gt=0, description="Amount to allocate")
    purpose: str = Field(..., min_length=1, max_length=255, description="Allocation purpose")
    bill_id: Optional[str] = Field(None, max_length=50, description="QBO bill ID")
    expense_category: Optional[str] = Field(None, max_length=100, description="Expense category")
    expected_utilization_date: Optional[datetime] = Field(None, description="Expected usage date")

class ReserveAllocationCreate(ReserveAllocationBase):
    """Schema for creating reserve allocations."""
    reserve_id: str = Field(..., description="Reserve ID")

class ReserveAllocation(ReserveAllocationBase):
    """Schema for reserve allocation responses."""
    allocation_id: str
    reserve_id: str
    business_id: str
    allocation_date: datetime
    actual_utilization_date: Optional[datetime]
    status: str

    class Config:
        from_attributes = True

class RunwayCalculationWithReserves(BaseModel):
    """Schema for runway calculations including reserve impacts."""
    total_cash: Decimal = Field(..., description="Total cash across all accounts")
    reserved_cash: Decimal = Field(..., description="Total cash in reserves")
    available_cash: Decimal = Field(..., description="Cash available for operations")
    monthly_burn: Decimal = Field(..., description="Monthly operational burn rate")
    reserve_funding_required: Decimal = Field(..., description="Monthly reserve funding needed")
    adjusted_monthly_burn: Decimal = Field(..., description="Burn rate including reserve funding")
    operational_runway_months: float = Field(..., description="Runway based on available cash only")
    total_runway_months: float = Field(..., description="Runway including all reserves")
    reserve_breakdown: List[Dict[str, Any]] = Field(..., description="Individual reserve impacts")
    recommendations: List[str] = Field(..., description="Reserve management recommendations")

class ReserveRecommendation(BaseModel):
    """Schema for reserve recommendations."""
    reserve_type: ReserveTypeEnum
    recommended_amount: Decimal
    rationale: str
    priority: str  # 'high', 'medium', 'low'
    timeline: str  # 'immediate', '30_days', '90_days'
