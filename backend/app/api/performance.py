from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..api import deps
from ..db.session import get_db
from ..models.portfolio import Portfolio
from ..schemas.performance import PortfolioSnapshot, PerformanceMetrics
from ..services.performance_tracker import PerformanceTracker
from ..services.market_data import MarketDataService

router = APIRouter()
market_data = MarketDataService()
performance_tracker = PerformanceTracker(market_data)

@router.post("/{portfolio_id}/snapshots", response_model=PortfolioSnapshot)
async def create_portfolio_snapshot(
    portfolio_id: int,
    investment_amount: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    """Create a new snapshot of the portfolio with current market prices"""
    # Check if portfolio belongs to current user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    try:
        snapshot = await performance_tracker.create_snapshot(
            db=db, portfolio_id=portfolio_id, investment_amount=investment_amount
        )
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{portfolio_id}/history", response_model=List[PortfolioSnapshot])
def get_portfolio_history(
    portfolio_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    """Get performance history for a portfolio"""
    # Check if portfolio belongs to current user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    try:
        history = performance_tracker.get_performance_history(
            db=db, 
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{portfolio_id}/metrics", response_model=PerformanceMetrics)
def get_portfolio_metrics(
    portfolio_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    """Get performance metrics for a portfolio"""
    # Check if portfolio belongs to current user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    try:
        metrics = performance_tracker.calculate_metrics(
            db=db,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date
        )
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))