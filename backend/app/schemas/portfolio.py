from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AllocationBase(BaseModel):
    asset_class: str
    asset_name: str
    allocation_percentage: float
    ticker: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AllocationCreate(AllocationBase):
    pass

class AllocationUpdate(AllocationBase):
    pass

class Allocation(AllocationBase):
    id: int
    portfolio_id: int
    
    class Config:
        orm_mode = True

class PortfolioBase(BaseModel):
    name: str
    risk_profile: str

class PortfolioCreate(PortfolioBase):
    allocations: List[AllocationCreate]

class PortfolioUpdate(PortfolioBase):
    allocations: Optional[List[AllocationCreate]] = None

class Portfolio(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    allocations: List[Allocation]
    
    class Config:
        orm_mode = True

class PortfolioGenerationRequest(BaseModel):
    risk_profile: str = Field(..., description="Risk profile: conservative, moderate, or aggressive")
    investment_amount: Optional[float] = Field(None, description="Total investment amount")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optional allocation constraints")
    name: Optional[str] = Field(None, description="Portfolio name")