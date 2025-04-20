from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.portfolio import Portfolio
from ..models.allocation import Allocation
from ..services.portfolio_generator import generate_portfolio

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

# Pydantic models for request/response
class AllocationBase(BaseModel):
    asset_type: str
    asset_name: str
    ticker: Optional[str] = None
    percentage: float
    current_value: Optional[float] = None

class AllocationCreate(AllocationBase):
    pass

class AllocationResponse(AllocationBase):
    id: int
    portfolio_id: int

    class Config:
        orm_mode = True

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None
    risk_level: int
    initial_investment: float

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime
    allocations: List[AllocationResponse] = []

    class Config:
        orm_mode = True

class PortfolioGenerateRequest(BaseModel):
    name: str
    risk_level: int  # 1-10
    initial_investment: float
    description: Optional[str] = None

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    db_portfolio = Portfolio(
        name=portfolio.name,
        description=portfolio.description,
        risk_level=portfolio.risk_level,
        initial_investment=portfolio.initial_investment
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.get("/", response_model=List[PortfolioResponse])
def read_portfolios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).offset(skip).limit(limit).all()
    return portfolios

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def read_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(portfolio_id: int, portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Update portfolio attributes
    for key, value in portfolio.dict().items():
        setattr(db_portfolio, key, value)
    
    db_portfolio.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.delete(portfolio)
    db.commit()
    return {"ok": True}

@router.post("/generate", response_model=PortfolioResponse)
def create_generated_portfolio(request: PortfolioGenerateRequest, db: Session = Depends(get_db)):
    # Create the portfolio
    db_portfolio = Portfolio(
        name=request.name,
        description=request.description,
        risk_level=request.risk_level,
        initial_investment=request.initial_investment
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    
    # Generate allocations based on risk level
    allocations = generate_portfolio(request.risk_level, request.initial_investment)
    
    # Add allocations to the portfolio
    for alloc in allocations:
        db_allocation = Allocation(
            portfolio_id=db_portfolio.id,
            asset_type=alloc["asset_type"],
            asset_name=alloc["asset_name"],
            ticker=alloc.get("ticker"),
            percentage=alloc["percentage"],
            current_value=alloc["amount"]
        )
        db.add(db_allocation)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio