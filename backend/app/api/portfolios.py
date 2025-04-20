from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioGenerationRequest
from ..models.portfolio import Portfolio as PortfolioModel, Allocation as AllocationModel
from ..services.portfolio_generator import PortfolioGenerator

router = APIRouter()
portfolio_generator = PortfolioGenerator()

@router.post("/generate/", response_model=Portfolio)
def generate_portfolio(
    request: PortfolioGenerationRequest,
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user)  # Uncomment when adding auth
):
    """
    Generate a portfolio based on risk profile and optional constraints
    """
    # Generate portfolio
    portfolio_data = portfolio_generator.generate_portfolio(
        risk_profile=request.risk_profile,
        name=request.name,
        constraints=request.constraints
    )
    
    # Create portfolio in database
    db_portfolio = PortfolioModel(
        name=portfolio_data.name,
        risk_profile=portfolio_data.risk_profile,
        # user_id=user.id  # Uncomment when adding auth
        user_id=1  # Temporary for development
    )
    db.add(db_portfolio)
    db.flush()
    
    # Create allocations
    for allocation_data in portfolio_data.allocations:
        db_allocation = AllocationModel(
            portfolio_id=db_portfolio.id,
            asset_class=allocation_data.asset_class,
            asset_name=allocation_data.asset_name,
            allocation_percentage=allocation_data.allocation_percentage,
            ticker=allocation_data.ticker,
            sector=allocation_data.sector,
            region=allocation_data.region
        )
        db.add(db_allocation)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.get("/", response_model=List[Portfolio])
def get_portfolios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user)  # Uncomment when adding auth
):
    """Get all portfolios for the current user"""
    # portfolios = db.query(PortfolioModel).filter(PortfolioModel.user_id == user.id).offset(skip).limit(limit).all()
    portfolios = db.query(PortfolioModel).offset(skip).limit(limit).all()  # Temporary for development
    return portfolios

@router.get("/{portfolio_id}", response_model=Portfolio)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user)  # Uncomment when adding auth
):
    """Get a specific portfolio by ID"""
    portfolio = db.query(PortfolioModel).filter(PortfolioModel.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    # if portfolio.user_id != user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this portfolio")
    return portfolio

@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user)  # Uncomment when adding auth
):
    """Update a portfolio"""
    db_portfolio = db.query(PortfolioModel).filter(PortfolioModel.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    # if db_portfolio.user_id != user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to modify this portfolio")
    
    # Update portfolio attributes
    for key, value in portfolio_update.dict(exclude={"allocations"}).items():
        setattr(db_portfolio, key, value)
    
    # Update allocations if provided
    if portfolio_update.allocations:
        # Delete existing allocations
        db.query(AllocationModel).filter(AllocationModel.portfolio_id == portfolio_id).delete()
        
        # Add new allocations
        for allocation_data in portfolio_update.allocations:
            db_allocation = AllocationModel(
                portfolio_id=db_portfolio.id,
                asset_class=allocation_data.asset_class,
                asset_name=allocation_data.asset_name,
                allocation_percentage=allocation_data.allocation_percentage,
                ticker=allocation_data.ticker,
                sector=allocation_data.sector,
                region=allocation_data.region
            )
            db.add(db_allocation)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.delete("/{portfolio_id}", status_code=204)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user)  # Uncomment when adding auth
):
    """Delete a portfolio"""
    db_portfolio = db.query(PortfolioModel).filter(PortfolioModel.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    # if db_portfolio.user_id != user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this portfolio")
    
    db.delete(db_portfolio)
    db.commit()
    return {}