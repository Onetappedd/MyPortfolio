from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from ..db.base import Base

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))
    total_value = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), default=func.now(), index=True)
    
    # Growth metrics
    daily_change_percent = Column(Float, nullable=True)
    monthly_change_percent = Column(Float, nullable=True)
    yearly_change_percent = Column(Float, nullable=True)
    
class AssetSnapshot(Base):
    __tablename__ = "asset_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("portfolio_snapshots.id", ondelete="CASCADE"))
    allocation_id = Column(Integer, ForeignKey("allocations.id", ondelete="SET NULL"), nullable=True)
    asset_name = Column(String, index=True)
    ticker = Column(String, nullable=True, index=True)
    price = Column(Float)
    quantity = Column(Float)
    value = Column(Float)
    allocation_percentage = Column(Float)