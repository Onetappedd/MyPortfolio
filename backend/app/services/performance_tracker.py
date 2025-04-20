from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models.portfolio import Portfolio, Allocation
from ..models.portfolio_history import PortfolioSnapshot, AssetSnapshot
from ..schemas.performance import PerformanceMetrics
from ..services.market_data import MarketDataService

class PerformanceTracker:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
    
    async def create_snapshot(
        self, db: Session, portfolio_id: int, investment_amount: float = None
    ) -> PortfolioSnapshot:
        """
        Create a new snapshot of the portfolio with current market prices
        """
        # Get portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio with ID {portfolio_id} not found")
        
        # Get allocations
        allocations = db.query(Allocation).filter(Allocation.portfolio_id == portfolio_id).all()
        
        # If no allocations, can't create snapshot
        if not allocations:
            raise ValueError(f"Portfolio with ID {portfolio_id} has no allocations")
        
        # Calculate total portfolio value
        total_value = 0.0
        assets = []
        
        # If no investment amount provided, use a default or previous snapshot
        if investment_amount is None:
            # Try to get the latest snapshot to use its value
            latest_snapshot = (
                db.query(PortfolioSnapshot)
                .filter(PortfolioSnapshot.portfolio_id == portfolio_id)
                .order_by(PortfolioSnapshot.date.desc())
                .first()
            )
            
            investment_amount = 10000.0  # Default
            if latest_snapshot:
                investment_amount = latest_snapshot.total_value
        
        # Get current prices and calculate values
        for allocation in allocations:
            if not allocation.ticker:
                continue
            
            # Get current price for this asset
            try:
                price = await self.market_data.get_latest_price(allocation.ticker)
            except Exception as e:
                print(f"Error getting price for {allocation.ticker}: {e}")
                price = 0.0  # Set to zero if price fetch fails
            
            # Calculate quantity based on allocation percentage and investment amount
            quantity = (allocation.allocation_percentage * investment_amount) / price if price > 0 else 0
            value = price * quantity
            total_value += value
            
            # Create asset snapshot
            assets.append({
                "allocation_id": allocation.id,
                "asset_name": allocation.asset_name,
                "ticker": allocation.ticker,
                "price": price,
                "quantity": quantity,
                "value": value,
                "allocation_percentage": allocation.allocation_percentage
            })
        
        # Calculate performance metrics
        daily_change, monthly_change, yearly_change = self._calculate_changes(
            db, portfolio_id, total_value
        )
        
        # Create portfolio snapshot
        snapshot = PortfolioSnapshot(
            portfolio_id=portfolio_id,
            total_value=total_value,
            date=datetime.utcnow(),
            daily_change_percent=daily_change,
            monthly_change_percent=monthly_change,
            yearly_change_percent=yearly_change
        )
        db.add(snapshot)
        db.flush()  # Get snapshot ID without committing transaction
        
        # Create asset snapshots
        for asset_data in assets:
            asset_snapshot = AssetSnapshot(
                snapshot_id=snapshot.id,
                allocation_id=asset_data["allocation_id"],
                asset_name=asset_data["asset_name"],
                ticker=asset_data["ticker"],
                price=asset_data["price"],
                quantity=asset_data["quantity"],
                value=asset_data["value"],
                allocation_percentage=asset_data["allocation_percentage"]
            )
            db.add(asset_snapshot)
        
        db.commit()
        db.refresh(snapshot)
        return snapshot
    
    def _calculate_changes(
        self, db: Session, portfolio_id: int, current_value: float
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate daily, monthly, and yearly percentage changes"""
        daily_change = None
        monthly_change = None
        yearly_change = None
        
        now = datetime.utcnow()
        
        # Find previous day's snapshot
        day_snapshot = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.date <= now - timedelta(days=1)
            )
            .order_by(PortfolioSnapshot.date.desc())
            .first()
        )
        
        # Find previous month's snapshot
        month_snapshot = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.date <= now - timedelta(days=30)
            )
            .order_by(PortfolioSnapshot.date.desc())
            .first()
        )
        
        # Find previous year's snapshot
        year_snapshot = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.date <= now - timedelta(days=365)
            )
            .order_by(PortfolioSnapshot.date.desc())
            .first()
        )
        
        # Calculate changes
        if day_snapshot:
            daily_change = ((current_value - day_snapshot.total_value) / day_snapshot.total_value) * 100
            
        if month_snapshot:
            monthly_change = ((current_value - month_snapshot.total_value) / month_snapshot.total_value) * 100
            
        if year_snapshot:
            yearly_change = ((current_value - year_snapshot.total_value) / year_snapshot.total_value) * 100
            
        return daily_change, monthly_change, yearly_change
    
    def get_performance_history(
        self, 
        db: Session, 
        portfolio_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "daily"  # daily, weekly, monthly
    ) -> List[PortfolioSnapshot]:
        """
        Get performance history for a portfolio within a date range
        """
        if not end_date:
            end_date = datetime.utcnow()
            
        if not start_date:
            # Default to last 3 months
            start_date = end_date - timedelta(days=90)
        
        query = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.date >= start_date,
                PortfolioSnapshot.date <= end_date
            )
        )
        
        # Apply interval sampling
        if interval == "weekly":
            # Extract the week and group by that
            query = query.filter(func.date_part('dow', PortfolioSnapshot.date) == 1)
        elif interval == "monthly":
            # Extract the day of month and get only the 1st
            query = query.filter(func.date_part('day', PortfolioSnapshot.date) == 1)
        
        # Order by date
        snapshots = query.order_by(PortfolioSnapshot.date.asc()).all()
        return snapshots
    
    def calculate_metrics(
        self, 
        db: Session, 
        portfolio_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PerformanceMetrics:
        """
        Calculate performance metrics for a portfolio over a time period
        """
        if not end_date:
            end_date = datetime.utcnow()
            
        if not start_date:
            # Default to last 1 year
            start_date = end_date - timedelta(days=365)
        
        # Get starting snapshot
        start_snapshot = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.date <= start_date
            )
            .order_by(PortfolioSnapshot.date.desc())
            .first()
        )
        
        # Get ending snapshot
        end_snapshot = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.portfolio_id == portfolio_id,
                PortfolioSnapshot.date <= end_date
            )
            .order_by(PortfolioSnapshot.date.desc())
            .first()
        )
        
        if not start_snapshot or not end_snapshot:
            raise ValueError("Insufficient snapshot data to calculate metrics")
        
        starting_value = start_snapshot.total_value
        ending_value = end_snapshot.total_value
        
        absolute_change = ending_value - starting_value
        percent_change = (absolute_change / starting_value) * 100 if starting_value > 0 else 0
        
        return PerformanceMetrics(
            period_start=start_snapshot.date,
            period_end=end_snapshot.date,
            starting_value=starting_value,
            ending_value=ending_value,
            percent_change=percent_change,
            absolute_change=absolute_change
        )