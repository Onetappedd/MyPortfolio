from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    risk_profile = Column(String)  # e.g., "conservative", "moderate", "aggressive"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    
    allocations = relationship("Allocation", back_populates="portfolio", cascade="all, delete-orphan")
    
class Allocation(Base):
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_class = Column(String, index=True)  # e.g., "stocks", "bonds", "cash"
    asset_name = Column(String, index=True)   # e.g., "US Large Cap", "Treasury Bonds"
    allocation_percentage = Column(Float)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    
    portfolio = relationship("Portfolio", back_populates="allocations")
    
    # Optional - more detailed allocation attributes
    ticker = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    region = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)  # For additional flexible data