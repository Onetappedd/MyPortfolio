from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    asset_type = Column(String)  # e.g., "stock", "bond", "real_estate", "cash"
    asset_name = Column(String)
    ticker = Column(String, nullable=True)
    percentage = Column(Float)  # Allocation percentage (0-100)
    current_value = Column(Float, nullable=True)
    
    # Relationship with portfolio
    portfolio = relationship("Portfolio", back_populates="allocations")