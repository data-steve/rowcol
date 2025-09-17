"""
RunwayReserve Service - Business Logic for Cash Reserve Management

This service handles all business logic for runway reserves including:
- Reserve creation, funding, and utilization
- Integration with runway calculations
- Reserve recommendations based on business patterns
- QBO account integration for reserve tracking
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from runway.reserves.models.runway_reserve import (
    RunwayReserve, ReserveTransaction, ReserveAllocation,
    ReserveType, ReserveStatus
)
from runway.reserves.schemas.runway_reserve import (
    RunwayReserveCreate, RunwayReserveUpdate, ReserveTransactionCreate,
    ReserveAllocationCreate, RunwayCalculationWithReserves, ReserveRecommendation
)
from db.transaction import db_transaction
from common.exceptions import (
    BusinessNotFoundError, ValidationError, RunwayCalculationError
)
from config.business_rules import RunwayThresholds

logger = logging.getLogger(__name__)

class RunwayReserveService:
    """Service for managing runway reserves and their impact on cash flow."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_reserve(self, reserve_data: RunwayReserveCreate, created_by: str = None) -> RunwayReserve:
        """Create a new runway reserve."""
        try:
            with db_transaction(self.db):
                # Create the reserve
                reserve = RunwayReserve(
                    business_id=reserve_data.business_id,
                    name=reserve_data.name,
                    description=reserve_data.description,
                    reserve_type=reserve_data.reserve_type.value,
                    target_amount=reserve_data.target_amount,
                    target_date=reserve_data.target_date,
                    expiry_date=reserve_data.expiry_date,
                    qbo_account_id=reserve_data.qbo_account_id,
                    created_by=created_by
                )
                
                # Set initial funding if provided
                if reserve_data.initial_amount and reserve_data.initial_amount > 0:
                    reserve.current_amount = reserve_data.initial_amount
                    
                    # Create initial funding transaction
                    initial_transaction = ReserveTransaction(
                        reserve_id=reserve.reserve_id,
                        business_id=reserve.business_id,
                        transaction_type="initial_funding",
                        amount=reserve_data.initial_amount,
                        description=f"Initial funding for {reserve.name}",
                        created_by=created_by
                    )
                    self.db.add(initial_transaction)
                
                self.db.add(reserve)
                self.db.flush()
                
                logger.info(f"Created reserve {reserve.reserve_id} for business {reserve.business_id}")
                return reserve
                
        except Exception as e:
            logger.error(f"Failed to create reserve: {e}", exc_info=True)
            raise ValidationError("Failed to create reserve", {"error": str(e)})
    
    def get_business_reserves(self, business_id: str, active_only: bool = False) -> List[RunwayReserve]:
        """Get all reserves for a business."""
        query = self.db.query(RunwayReserve).filter(
            RunwayReserve.business_id == business_id
        )
        
        if active_only:
            query = query.filter(
                RunwayReserve.status.in_([ReserveStatus.ACTIVE.value, ReserveStatus.ALLOCATED.value])
            )
        
        return query.order_by(RunwayReserve.created_at.desc()).all()
    
    def get_reserve(self, reserve_id: str, business_id: str = None) -> RunwayReserve:
        """Get a specific reserve."""
        query = self.db.query(RunwayReserve).filter(RunwayReserve.reserve_id == reserve_id)
        
        if business_id:
            query = query.filter(RunwayReserve.business_id == business_id)
        
        reserve = query.first()
        if not reserve:
            raise BusinessNotFoundError(f"Reserve {reserve_id} not found")
        
        return reserve
    
    def update_reserve(self, reserve_id: str, reserve_data: RunwayReserveUpdate, 
                      business_id: str = None) -> RunwayReserve:
        """Update an existing reserve."""
        reserve = self.get_reserve(reserve_id, business_id)
        
        try:
            with db_transaction(self.db):
                # Update fields
                for field, value in reserve_data.dict(exclude_unset=True).items():
                    if hasattr(reserve, field):
                        setattr(reserve, field, value)
                
                reserve.updated_at = datetime.utcnow()
                
                logger.info(f"Updated reserve {reserve_id}")
                return reserve
                
        except Exception as e:
            logger.error(f"Failed to update reserve {reserve_id}: {e}", exc_info=True)
            raise ValidationError("Failed to update reserve", {"error": str(e)})
    
    def fund_reserve(self, reserve_id: str, amount: Decimal, description: str = None,
                    qbo_transaction_id: str = None, created_by: str = None) -> ReserveTransaction:
        """Add funding to a reserve."""
        reserve = self.get_reserve(reserve_id)
        
        if amount <= 0:
            raise ValidationError("Funding amount must be positive")
        
        try:
            with db_transaction(self.db):
                # Update reserve balance
                reserve.current_amount += amount
                reserve.updated_at = datetime.utcnow()
                
                # Create transaction record
                transaction = ReserveTransaction(
                    reserve_id=reserve_id,
                    business_id=reserve.business_id,
                    transaction_type="funding",
                    amount=amount,
                    description=description or f"Funding for {reserve.name}",
                    qbo_transaction_id=qbo_transaction_id,
                    created_by=created_by
                )
                self.db.add(transaction)
                self.db.flush()
                
                logger.info(f"Funded reserve {reserve_id} with ${amount}")
                return transaction
                
        except Exception as e:
            logger.error(f"Failed to fund reserve {reserve_id}: {e}", exc_info=True)
            raise ValidationError("Failed to fund reserve", {"error": str(e)})
    
    def allocate_reserve(self, allocation_data: ReserveAllocationCreate, 
                        created_by: str = None) -> ReserveAllocation:
        """Allocate reserve funds for specific purpose."""
        reserve = self.get_reserve(allocation_data.reserve_id)
        
        if not reserve.can_allocate(allocation_data.allocated_amount):
            raise ValidationError(
                f"Insufficient available reserves. Available: ${reserve.available_amount}, Requested: ${allocation_data.allocated_amount}"
            )
        
        try:
            with db_transaction(self.db):
                # Update reserve allocation
                reserve.allocate(allocation_data.allocated_amount, allocation_data.purpose)
                
                # Create allocation record
                allocation = ReserveAllocation(
                    reserve_id=allocation_data.reserve_id,
                    business_id=reserve.business_id,
                    allocated_amount=allocation_data.allocated_amount,
                    purpose=allocation_data.purpose,
                    bill_id=allocation_data.bill_id,
                    expense_category=allocation_data.expense_category,
                    expected_utilization_date=allocation_data.expected_utilization_date
                )
                self.db.add(allocation)
                self.db.flush()
                
                logger.info(f"Allocated ${allocation_data.allocated_amount} from reserve {allocation_data.reserve_id}")
                return allocation
                
        except Exception as e:
            logger.error(f"Failed to allocate reserve: {e}", exc_info=True)
            raise ValidationError("Failed to allocate reserve", {"error": str(e)})
    
    def utilize_reserve(self, reserve_id: str, amount: Decimal, purpose: str,
                       qbo_transaction_id: str = None, created_by: str = None) -> ReserveTransaction:
        """Utilize reserve funds for their intended purpose."""
        reserve = self.get_reserve(reserve_id)
        
        if not reserve.utilize(amount):
            raise ValidationError(f"Cannot utilize ${amount} from reserve with ${reserve.current_amount} available")
        
        try:
            with db_transaction(self.db):
                # Create utilization transaction
                transaction = ReserveTransaction(
                    reserve_id=reserve_id,
                    business_id=reserve.business_id,
                    transaction_type="utilization",
                    amount=-amount,  # Negative for utilization
                    description=f"Utilized for: {purpose}",
                    qbo_transaction_id=qbo_transaction_id,
                    created_by=created_by
                )
                self.db.add(transaction)
                self.db.flush()
                
                logger.info(f"Utilized ${amount} from reserve {reserve_id} for {purpose}")
                return transaction
                
        except Exception as e:
            logger.error(f"Failed to utilize reserve {reserve_id}: {e}", exc_info=True)
            raise ValidationError("Failed to utilize reserve", {"error": str(e)})
    
    def calculate_runway_with_reserves(self, business_id: str) -> RunwayCalculationWithReserves:
        """Calculate runway impact including all reserves."""
        try:
            # Get business reserves
            reserves = self.get_business_reserves(business_id, active_only=True)
            
            # Get cash and burn rate from QBO integration or use defaults for development
            # TODO: Replace with actual QBO cash flow data
            total_cash = self._get_business_cash_balance(business_id)
            monthly_burn = self._calculate_monthly_burn_rate(business_id)
            
            # Calculate reserve impacts
            total_reserved = sum(reserve.current_amount for reserve in reserves)
            available_cash = total_cash - total_reserved
            
            # Calculate monthly reserve funding requirements
            reserve_funding_required = sum(
                reserve.calculate_monthly_funding_needed() for reserve in reserves
            )
            
            # Adjusted burn rate includes reserve funding
            adjusted_monthly_burn = monthly_burn + reserve_funding_required
            
            # Calculate runway scenarios
            operational_runway = float(available_cash / monthly_burn) if monthly_burn > 0 else float('inf')
            total_runway = float(total_cash / adjusted_monthly_burn) if adjusted_monthly_burn > 0 else float('inf')
            
            # Generate reserve breakdown
            reserve_breakdown = [reserve.get_impact_on_runway() for reserve in reserves]
            
            # Generate recommendations
            recommendations = self._generate_reserve_recommendations(
                business_id, reserves, available_cash, monthly_burn
            )
            
            return RunwayCalculationWithReserves(
                total_cash=total_cash,
                reserved_cash=total_reserved,
                available_cash=available_cash,
                monthly_burn=monthly_burn,
                reserve_funding_required=reserve_funding_required,
                adjusted_monthly_burn=adjusted_monthly_burn,
                operational_runway_months=operational_runway,
                total_runway_months=total_runway,
                reserve_breakdown=reserve_breakdown,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate runway with reserves for business {business_id}: {e}", exc_info=True)
            raise RunwayCalculationError("Failed to calculate runway with reserves", {"error": str(e)})
    
    def get_reserve_recommendations(self, business_id: str) -> List[ReserveRecommendation]:
        """Generate reserve recommendations for a business."""
        reserves = self.get_business_reserves(business_id, active_only=True)
        
        # Get business data from QBO integration or use defaults for development
        # TODO: Replace with actual QBO financial data
        monthly_revenue = self._get_monthly_revenue(business_id)
        monthly_expenses = self._get_monthly_expenses(business_id)
        employee_count = self._get_employee_count(business_id)
        
        recommendations = []
        
        # Tax reserve recommendation (25% of monthly profit)
        monthly_profit = monthly_revenue - monthly_expenses
        if monthly_profit > 0:
            tax_reserve_exists = any(r.reserve_type == ReserveType.TAX_RESERVE.value for r in reserves)
            if not tax_reserve_exists:
                recommendations.append(ReserveRecommendation(
                    reserve_type=ReserveType.TAX_RESERVE,
                    recommended_amount=monthly_profit * Decimal('0.25') * 3,  # 3 months of taxes
                    rationale="Set aside 25% of profit for quarterly tax payments",
                    priority="high",
                    timeline="immediate"
                ))
        
        # Payroll reserve recommendation (1-2 months of payroll)
        estimated_monthly_payroll = monthly_expenses * Decimal('0.6')  # Assume 60% is payroll
        payroll_reserve_exists = any(r.reserve_type == ReserveType.PAYROLL_RESERVE.value for r in reserves)
        if not payroll_reserve_exists:
            recommendations.append(ReserveRecommendation(
                reserve_type=ReserveType.PAYROLL_RESERVE,
                recommended_amount=estimated_monthly_payroll * 2,
                rationale="Emergency payroll coverage for 2 months",
                priority="high",
                timeline="30_days"
            ))
        
        # Emergency reserve recommendation (3-6 months of expenses)
        emergency_reserve_exists = any(r.reserve_type == ReserveType.EMERGENCY_RESERVE.value for r in reserves)
        if not emergency_reserve_exists:
            recommendations.append(ReserveRecommendation(
                reserve_type=ReserveType.EMERGENCY_RESERVE,
                recommended_amount=monthly_expenses * 3,
                rationale="General emergency fund for unexpected expenses",
                priority="medium",
                timeline="90_days"
            ))
        
        return recommendations
    
    def _generate_reserve_recommendations(self, business_id: str, reserves: List[RunwayReserve],
                                        available_cash: Decimal, monthly_burn: Decimal) -> List[str]:
        """Generate textual recommendations for reserve management."""
        recommendations = []
        
        # Check for underfunded reserves
        underfunded_reserves = [r for r in reserves if not r.is_fully_funded]
        if underfunded_reserves:
            total_deficit = sum(r.funding_deficit for r in underfunded_reserves)
            recommendations.append(
                f"${total_deficit:,.2f} needed to fully fund {len(underfunded_reserves)} reserves"
            )
        
        # Check runway impact
        if available_cash / monthly_burn < RunwayThresholds.CRITICAL_DAYS / 30:
            recommendations.append("Critical: Available cash (excluding reserves) is below 1 week")
        
        # Check for over-reserved cash
        total_reserved = sum(r.current_amount for r in reserves)
        if total_reserved > available_cash * Decimal('0.5'):
            recommendations.append("Consider if reserves are too high relative to available cash")
        
        # Check for missing critical reserves
        reserve_types = {r.reserve_type for r in reserves}
        if ReserveType.TAX_RESERVE.value not in reserve_types:
            recommendations.append("Consider creating a tax reserve for quarterly payments")
        
        if ReserveType.PAYROLL_RESERVE.value not in reserve_types:
            recommendations.append("Consider creating an emergency payroll reserve")
        
        return recommendations
    
    # ==================== HELPER METHODS FOR QBO DATA ====================
    
    def _get_business_cash_balance(self, business_id: str) -> Decimal:
        """Get current cash balance from QBO or use default for development."""
        # TODO: Implement QBO cash balance API call
        # For now, return a reasonable default for development
        return Decimal('100000.00')
    
    def _calculate_monthly_burn_rate(self, business_id: str) -> Decimal:
        """Calculate monthly burn rate from QBO expense data."""
        # TODO: Implement QBO expense analysis
        # For now, return a reasonable default for development
        return Decimal('15000.00')
    
    def _get_monthly_revenue(self, business_id: str) -> Decimal:
        """Get average monthly revenue from QBO."""
        # TODO: Implement QBO revenue analysis
        # For now, return a reasonable default for development
        return Decimal('25000.00')
    
    def _get_monthly_expenses(self, business_id: str) -> Decimal:
        """Get average monthly expenses from QBO."""
        # TODO: Implement QBO expense analysis
        # For now, return a reasonable default for development
        return Decimal('15000.00')
    
    def _get_employee_count(self, business_id: str) -> int:
        """Get employee count from QBO payroll or HR data."""
        # TODO: Implement QBO payroll API call
        # For now, return a reasonable default for development
        return 5
