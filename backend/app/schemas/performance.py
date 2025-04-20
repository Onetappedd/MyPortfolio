from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class AssetSnapshotBase(BaseModel):
    asset_name: str
    ticker: Optional[str] = None
    price: float
    quantity: float
    value: float
    allocation_percentage: float

class AssetSnapshotCreate(AssetSnapshotBase):
    allocation_id: Optional[int] = None

class AssetSnapshot(AssetSnapshotBase):
    id: int
    snapshot_id: int
    
    class Config:
        orm_mode = True

class PortfolioSnapshotBase(BaseModel):
    portfolio_id: int
    total_value: float
    date: datetime
    daily_change_percent: Optional[float] = None
    monthly_change_percent: Optional[float] = None
    yearly_change_percent: Optional[float] = None

class PortfolioSnapshotCreate(PortfolioSnapshotBase):
    assets: List[AssetSnapshotCreate]

class PortfolioSnapshot(PortfolioSnapshotBase):
    id: int
    assets: List[AssetSnapshot] = []
    
    class Config:
        orm_mode = True

class PerformanceMetrics(BaseModel):
    period_start: datetime
    period_end: datetime
    starting_value: float
    ending_value: float
    percent_change: float
    absolute_change: float