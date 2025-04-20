from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models.allocation import Allocation
from ..models.portfolio import Portfolio

router = APIRouter(prefix="/allocations", tags=["allocations"])

# Pydantic models for request/response
class AllocationBase(BaseModel):
    asset_type: str
    asset_name: str
    ticker: Optional[str] = None
    percentage: float
    current_value: Optional[float] = None

class AllocationCreate(AllocationBase):
    portfolio_id: int

class AllocationUpdate(AllocationBase):
    pass

class AllocationResponse(AllocationBase):
    id: int
    portfolio_id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
def create_allocation(allocation: AllocationCreate, db: Session = Depends(get_db)):
    # Check if portfolio exists
    portfolio = db.query(Portfolio).filter(Portfolio.id == allocation.portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Check if total allocation would exceed 100%
    current_allocations = db.query(Allocation).filter(Allocation.portfolio_id == allocation.portfolio_id).all()
    total_percentage = sum(a.percentage for a in current_allocations)
    if total_percentage + allocation.percentage > 100:
        raise HTTPException(status_code=400, detail="Total allocation cannot exceed 100%")
    
    # Create new allocation
    db_allocation = Allocation(**allocation.dict())
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation

@router.get("/", response_model=List[AllocationResponse])
def read_allocations(portfolio_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Allocation)
    if portfolio_id:
        query = query.filter(Allocation.portfolio_id == portfolio_id)
    allocations = query.offset(skip).limit(limit).all()
    return allocations

@router.get("/{allocation_id}", response_model=AllocationResponse)
def read_allocation(allocation_id: int, db: Session = Depends(get_db)):
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation

@router.put("/{allocation_id}", response_model=AllocationResponse)
def update_allocation(allocation_id: int, allocation: AllocationUpdate, db: Session = Depends(get_db)):
    db_allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if db_allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    
    # Check if total allocation would exceed 100%
    current_allocations = db.query(Allocation).filter(
        Allocation.portfolio_id == db_allocation.portfolio_id,
        Allocation.id != allocation_id
    ).all()
    total_percentage = sum(a.percentage for a in current_allocations)
    if total_percentage + allocation.percentage > 100:
        raise HTTPException(status_code=400, detail="Total allocation cannot exceed 100%")
    
    # Update allocation attributes
    for key, value in allocation.dict().items():
        setattr(db_allocation, key, value)
    
    db.commit()
    db.refresh(db_allocation)
    return db_allocation

@router.delete("/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    
    db.delete(allocation)
    db.commit()
    return {"ok": True}