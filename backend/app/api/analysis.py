from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from ..api import deps
from ..db.session import get_db
from ..models.portfolio import Portfolio
from ..services.risk_analyzer import RiskAnalyzer
from ..services.market_data import MarketDataService

router = APIRouter()
market_data = MarketDataService()
risk_analyzer = RiskAnalyzer(market_data)

@router.get("/{portfolio_id}/risk")
async def get_portfolio_risk_metrics(
    portfolio_id: int,
    days: int = 365,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    """Get risk metrics for a portfolio"""
    # Check if portfolio belongs to current user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    try:
        metrics = await risk_analyzer.calculate_portfolio_risk_metrics(db, portfolio_id, days)
        return {"portfolio_id": portfolio_id, "metrics": metrics}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_portfolios(
    portfolio_ids: List[int] = Body(...),
    days: int = 365,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    """Compare multiple portfolios"""
    # Check if all portfolios belong to current user
    for portfolio_id in portfolio_ids:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(
                status_code=404, 
                detail=f"Portfolio with id {portfolio_id} not found or you don't have access to it"
            )
    
    try:
        comparison = await risk_analyzer.compare_portfolios(db, portfolio_ids, days)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))