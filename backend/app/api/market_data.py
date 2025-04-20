from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..services.market_data import MarketDataService
from ..api import deps

router = APIRouter()
market_data = MarketDataService()

@router.get("/price/{symbol}")
async def get_latest_price(
    symbol: str,
    current_user = Depends(deps.get_current_user)
):
    """Get the latest price for a ticker symbol"""
    try:
        price = await market_data.get_latest_price(symbol)
        return {"symbol": symbol, "price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    days: Optional[int] = Query(30, ge=1, le=365),
    current_user = Depends(deps.get_current_user)
):
    """Get historical price data for a ticker symbol"""
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    try:
        data = await market_data.get_historical_data(
            symbol, 
            start_date=start_date,
            end_date=end_date
        )
        return {"symbol": symbol, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_symbols(
    query: str,
    current_user = Depends(deps.get_current_user)
):
    """Search for ticker symbols"""
    try:
        results = await market_data.search_symbols(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))