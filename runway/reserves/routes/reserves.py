"""
Runway Reserve API Routes

API endpoints for managing runway reserves, allocations, and runway calculations
with reserve impact visualization.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from db.session import get_db
from runway.auth.middleware.auth import get_current_business_id
from runway.reserves.services.runway_reserve_service import RunwayReserveService
from runway.reserves.schemas.runway_reserve import (
    RunwayReserveCreate, RunwayReserveUpdate, RunwayReserve,
    ReserveAllocationCreate, ReserveAllocation,
    RunwayCalculationWithReserves, ReserveRecommendation,
    # ReserveSummary  # TODO: Implement missing schemas
)
from common.exceptions import ValidationError

router = APIRouter(prefix="/reserves", tags=["Runway Reserves"])

def get_reserve_service(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
) -> RunwayReserveService:
    """Get reserve service with business context."""
    return RunwayReserveService(db, business_id)

@router.get("/", response_model=List[RunwayReserve])
async def list_reserves(
    active_only: bool = True,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    List all runway reserves for the business.
    
    Args:
        active_only: If True, only return active reserves
    """
    try:
        reserves = reserve_service.list_reserves(active_only=active_only)
        return reserves
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reserves: {str(e)}"
        )

@router.post("/", response_model=RunwayReserve)
async def create_reserve(
    reserve_data: RunwayReserveCreate,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Create a new runway reserve.
    
    Creates a new reserve to earmark funds for specific purposes,
    reducing available cash for runway calculations.
    """
    try:
        reserve = reserve_service.create_reserve(
            reserve_data=reserve_data,
            created_by="api_user"  # TODO: Get from auth context
        )
        return reserve
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reserve: {str(e)}"
        )

@router.get("/{reserve_id}", response_model=RunwayReserve)
async def get_reserve(
    reserve_id: int,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """Get details of a specific runway reserve."""
    try:
        reserve = reserve_service.get_reserve(reserve_id)
        if not reserve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserve {reserve_id} not found"
            )
        return reserve
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reserve: {str(e)}"
        )

@router.put("/{reserve_id}", response_model=RunwayReserve)
async def update_reserve(
    reserve_id: int,
    reserve_data: RunwayReserveUpdate,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """Update a runway reserve."""
    try:
        reserve = reserve_service.update_reserve(
            reserve_id=reserve_id,
            reserve_data=reserve_data,
            updated_by="api_user"  # TODO: Get from auth context
        )
        return reserve
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update reserve: {str(e)}"
        )

@router.delete("/{reserve_id}")
async def delete_reserve(
    reserve_id: int,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """Delete a runway reserve (releases allocated funds)."""
    try:
        success = reserve_service.release_reserve(
            reserve_id=reserve_id,
            reason="Reserve deleted via API"
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserve {reserve_id} not found or already released"
            )
        return {"message": "Reserve deleted and funds released"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reserve: {str(e)}"
        )

@router.post("/{reserve_id}/allocate", response_model=ReserveAllocation)
async def allocate_reserve(
    reserve_id: int,
    allocation_data: ReserveAllocationCreate,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Allocate reserve funds to a specific bill or expense.
    
    This marks the reserve as allocated to a specific purpose,
    tracking how reserved funds are being utilized.
    """
    try:
        allocation = reserve_service.allocate_reserve(
            reserve_id=reserve_id,
            allocation_data=allocation_data,
            allocated_by="api_user"  # TODO: Get from auth context
        )
        return allocation
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to allocate reserve: {str(e)}"
        )

@router.post("/{reserve_id}/release")
async def release_reserve(
    reserve_id: int,
    reason: Optional[str] = None,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Release a reserve back to available cash.
    
    This makes the reserved funds available for operational use,
    increasing the calculated runway.
    """
    try:
        success = reserve_service.release_reserve(
            reserve_id=reserve_id,
            reason=reason or "Released via API"
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserve {reserve_id} not found or already released"
            )
        return {"message": "Reserve released successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to release reserve: {str(e)}"
        )

@router.get("/summary")  # TODO: Implement ReserveSummary schema
async def get_reserve_summary(
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Get summary of all reserves and their impact on runway.
    
    Returns total reserved amounts, available cash, and runway impact.
    """
    try:
        summary = reserve_service.get_reserve_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reserve summary: {str(e)}"
        )

@router.get("/runway-calculation", response_model=RunwayCalculationWithReserves)
async def calculate_runway_with_reserves(
    include_projections: bool = True,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Calculate runway with reserve impact visualization.
    
    Shows how reserves affect available cash and runway calculations,
    with projections for reserve utilization.
    """
    try:
        calculation = reserve_service.calculate_runway_with_reserves(
            include_projections=include_projections
        )
        return calculation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate runway with reserves: {str(e)}"
        )

@router.get("/recommendations", response_model=List[ReserveRecommendation])
async def get_reserve_recommendations(
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Get AI-powered reserve recommendations based on business patterns.
    
    Analyzes cash flow patterns, seasonal variations, and business rules
    to recommend optimal reserve amounts and types.
    """
    try:
        recommendations = reserve_service.get_reserve_recommendations()
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.post("/recommendations/{recommendation_id}/accept")
async def accept_reserve_recommendation(
    recommendation_id: str,
    reserve_service: RunwayReserveService = Depends(get_reserve_service)
):
    """
    Accept and implement a reserve recommendation.
    
    Creates the recommended reserve based on AI analysis.
    """
    try:
        reserve = reserve_service.implement_recommendation(
            recommendation_id=recommendation_id,
            implemented_by="api_user"  # TODO: Get from auth context
        )
        return {"message": "Recommendation implemented", "reserve_id": reserve.reserve_id}
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to implement recommendation: {str(e)}"
        )
