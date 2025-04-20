from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random

app = FastAPI()

class Allocation(BaseModel):
    asset_name: str
    asset_type: str
    percentage: float
    current_value: float

class Portfolio(BaseModel):
    name: str
    description: str
    risk_level: int
    initial_investment: float
    allocations: List[Allocation]

@app.post('/portfolios/generate', response_model=Portfolio)
def generate_portfolio(name: str, description: str, risk_level: int, initial_investment: float):
    if risk_level < 1 or risk_level > 10:
        raise HTTPException(status_code=400, detail="Risk level must be between 1 and 10.")
    if initial_investment <= 0:
        raise HTTPException(status_code=400, detail="Initial investment must be greater than zero.")

    allocations = [
        Allocation(asset_name="Tech Fund", asset_type="Stock", percentage=random.uniform(40, 60), current_value=initial_investment * 0.5),
        Allocation(asset_name="Gov Bond", asset_type="Bond", percentage=random.uniform(20, 30), current_value=initial_investment * 0.3),
        Allocation(asset_name="REIT", asset_type="Real Estate", percentage=random.uniform(10, 20), current_value=initial_investment * 0.2),
    ]

    return Portfolio(
        name=name,
        description=description,
        risk_level=risk_level,
        initial_investment=initial_investment,
        allocations=allocations,
    )