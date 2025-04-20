def generate_portfolio(risk_level, initial_investment):
    """
    Generate a portfolio allocation based on risk level (1-10)
    and initial investment amount.
    
    Risk level 1 = Most conservative
    Risk level 10 = Most aggressive
    """
    # Normalize risk level to 0-1 range
    risk_factor = (risk_level - 1) / 9
    
    if risk_level <= 2:  # Very Conservative
        stocks_percentage = 20 + (risk_factor * 10)
        bonds_percentage = 60 - (risk_factor * 10)
        cash_percentage = 15 - (risk_factor * 5)
        real_estate_percentage = 5
        
        stocks = [
            {"name": "Vanguard Dividend Appreciation ETF", "ticker": "VIG", "percentage": 10},
            {"name": "Vanguard High Dividend Yield ETF", "ticker": "VYM", "percentage": 10}
        ]
        
    elif risk_level <= 4:  # Conservative
        stocks_percentage = 30 + (risk_factor * 15)
        bonds_percentage = 50 - (risk_factor * 10)
        cash_percentage = 10 - (risk_factor * 5)
        real_estate_percentage = 10
        
        stocks = [
            {"name": "Vanguard Dividend Appreciation ETF", "ticker": "VIG", "percentage": 10},
            {"name": "Vanguard High Dividend Yield ETF", "ticker": "VYM", "percentage": 10},
            {"name": "Vanguard S&P 500 ETF", "ticker": "VOO", "percentage": 10}
        ]
        
    elif risk_level <= 7:  # Moderate
        stocks_percentage = 50 + (risk_factor * 20)
        bonds_percentage = 30 - (risk_factor * 10)
        cash_percentage = 5
        real_estate_percentage = 15 - (risk_factor * 5)
        
        stocks = [
            {"name": "Vanguard S&P 500 ETF", "ticker": "VOO", "percentage": 20},
            {"name": "Vanguard Total Stock Market ETF", "ticker": "VTI", "percentage": 20},
            {"name": "Vanguard FTSE Developed Markets ETF", "ticker": "VEA", "percentage": 10}
        ]
        
    else:  # Aggressive
        stocks_percentage = 70 + (risk_factor * 20)
        bonds_percentage = 10
        cash_percentage = 5
        real_estate_percentage = 15 - (risk_factor * 5)
        
        stocks = [
            {"name": "Vanguard S&P 500 ETF", "ticker": "VOO", "percentage": 20},
            {"name": "Vanguard Total Stock Market ETF", "ticker": "VTI", "percentage": 20},
            {"name": "Vanguard FTSE Developed Markets ETF", "ticker": "VEA", "percentage": 15},
            {"name": "Vanguard FTSE Emerging Markets ETF", "ticker": "VWO", "percentage": 15}
        ]
    
    # Adjust stock percentages to match the total stocks allocation
    total_stock_percentage = sum(stock["percentage"] for stock in stocks)
    adjustment_factor = stocks_percentage / total_stock_percentage
    
    for stock in stocks:
        stock["percentage"] = stock["percentage"] * adjustment_factor
    
    # Create bonds allocation
    bonds = [
        {"name": "Vanguard Total Bond Market ETF", "ticker": "BND", "percentage": bonds_percentage * 0.7},
        {"name": "Vanguard Short-Term Bond ETF", "ticker": "BSV", "percentage": bonds_percentage * 0.3}
    ]
    
    # Create allocations list with amounts calculated
    allocations = []
    
    # Add stocks
    for stock in stocks:
        allocations.append({
            "asset_type": "stock",
            "asset_name": stock["name"],
            "ticker": stock["ticker"],
            "percentage": stock["percentage"],
            "amount": initial_investment * (stock["percentage"] / 100)
        })
    
    # Add bonds
    for bond in bonds:
        allocations.append({
            "asset_type": "bond",
            "asset_name": bond["name"],
            "ticker": bond["ticker"],
            "percentage": bond["percentage"],
            "amount": initial_investment * (bond["percentage"] / 100)
        })
    
    # Add cash
    allocations.append({
        "asset_type": "cash",
        "asset_name": "Cash Reserve",
        "ticker": None,
        "percentage": cash_percentage,
        "amount": initial_investment * (cash_percentage / 100)
    })
    
    # Add real estate
    allocations.append({
        "asset_type": "real_estate",
        "asset_name": "Vanguard Real Estate ETF",
        "ticker": "VNQ",
        "percentage": real_estate_percentage,
        "amount": initial_investment * (real_estate_percentage / 100)
    })
    
    return allocations