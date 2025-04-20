from typing import Dict, List, Optional, Any
import numpy as np
from ..schemas.portfolio import AllocationCreate, PortfolioCreate

class PortfolioGenerator:
    # Asset classes and typical allocations by risk profile
    ASSET_ALLOCATIONS = {
        "conservative": {
            "US Stocks": 0.20,
            "International Stocks": 0.10,
            "US Bonds": 0.50,
            "International Bonds": 0.10,
            "Cash": 0.10,
        },
        "moderate": {
            "US Stocks": 0.40,
            "International Stocks": 0.20,
            "US Bonds": 0.30,
            "International Bonds": 0.05,
            "Cash": 0.05,
        },
        "aggressive": {
            "US Stocks": 0.60,
            "International Stocks": 0.30,
            "US Bonds": 0.10,
            "International Bonds": 0.00,
            "Cash": 0.00,
        }
    }
    
    # Map of asset classes to more specific assets
    ASSET_CLASS_DETAILS = {
        "US Stocks": [
            {"name": "US Large Cap", "ticker": "VTI", "sector": "Broad Market"},
            {"name": "US Small Cap", "ticker": "VB", "sector": "Broad Market"},
            {"name": "US Tech Sector", "ticker": "VGT", "sector": "Technology"}
        ],
        "International Stocks": [
            {"name": "Developed Markets", "ticker": "VEA", "region": "Developed"},
            {"name": "Emerging Markets", "ticker": "VWO", "region": "Emerging"}
        ],
        "US Bonds": [
            {"name": "Treasury Bonds", "ticker": "VGIT", "sector": "Government"},
            {"name": "Corporate Bonds", "ticker": "VCIT", "sector": "Corporate"}
        ],
        "International Bonds": [
            {"name": "International Bonds", "ticker": "BNDX", "region": "Global"}
        ],
        "Cash": [
            {"name": "Money Market", "ticker": "VMFXX", "sector": "Cash Equivalent"}
        ]
    }
    
    def generate_portfolio(
        self, 
        risk_profile: str, 
        name: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> PortfolioCreate:
        """
        Generate a portfolio based on risk profile with optional constraints
        """
        # Validate risk profile
        if risk_profile not in self.ASSET_ALLOCATIONS:
            raise ValueError(f"Invalid risk profile: {risk_profile}. Must be one of: {list(self.ASSET_ALLOCATIONS.keys())}")
            
        # Get base allocations for this risk profile
        base_allocations = self.ASSET_ALLOCATIONS[risk_profile]
        
        # Apply constraints if provided
        final_allocations = self._apply_constraints(base_allocations, constraints)
        
        # Generate detailed allocations
        allocations = self._generate_detailed_allocations(final_allocations)
        
        # Create portfolio
        portfolio_name = name if name else f"{risk_profile.capitalize()} Portfolio"
        return PortfolioCreate(
            name=portfolio_name,
            risk_profile=risk_profile,
            allocations=allocations
        )
    
    def _apply_constraints(
        self, 
        base_allocations: Dict[str, float],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Apply user constraints to base allocations and rebalance
        """
        if not constraints:
            return base_allocations
            
        # Deep copy to avoid modifying the original
        allocations = dict(base_allocations)
        
        # Apply constraints (simplified example)
        if "max_allocations" in constraints:
            for asset, max_value in constraints["max_allocations"].items():
                if asset in allocations and allocations[asset] > max_value:
                    # Reduce allocation to max
                    diff = allocations[asset] - max_value
                    allocations[asset] = max_value
                    
                    # Distribute difference proportionally to other assets
                    remaining_allocation = sum([v for k, v in allocations.items() if k != asset])
                    if remaining_allocation > 0:
                        for k in allocations:
                            if k != asset:
                                allocations[k] += diff * (allocations[k] / remaining_allocation)
        
        # Normalize to ensure sum is 1.0
        total = sum(allocations.values())
        if total != 1.0:
            for k in allocations:
                allocations[k] /= total
                
        return allocations
    
    def _generate_detailed_allocations(self, allocations: Dict[str, float]) -> List[AllocationCreate]:
        """
        Generate detailed allocations with specific assets
        """
        detailed_allocations = []
        
        for asset_class, percentage in allocations.items():
            if percentage > 0 and asset_class in self.ASSET_CLASS_DETAILS:
                # Get details for this asset class
                asset_details = self.ASSET_CLASS_DETAILS[asset_class]
                
                # Distribute this asset class's allocation among its components
                # This is a simplified example - a real implementation would use more sophisticated logic
                asset_count = len(asset_details)
                if asset_count > 0:
                    # Create a random distribution that sums to the total allocation
                    if asset_count > 1:
                        sub_allocations = np.random.dirichlet(np.ones(asset_count)) * percentage
                    else:
                        sub_allocations = [percentage]
                    
                    for i, asset in enumerate(asset_details):
                        detailed_allocations.append(
                            AllocationCreate(
                                asset_class=asset_class,
                                asset_name=asset["name"],
                                allocation_percentage=float(sub_allocations[i]),
                                ticker=asset.get("ticker"),
                                sector=asset.get("sector"),
                                region=asset.get("region"),
                            )
                        )
                        
        return detailed_allocations