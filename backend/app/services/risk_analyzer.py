import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models.portfolio import Portfolio, Allocation
from ..models.portfolio_history import PortfolioSnapshot
from ..services.market_data import MarketDataService

class RiskAnalyzer:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
    
    async def calculate_portfolio_risk_metrics(
        self, 
        db: Session, 
        portfolio_id: int,
        days: int = 365
    ) -> Dict:
        """
        Calculate comprehensive risk metrics for a portfolio
        - Volatility
        - Sharpe Ratio
        - Maximum Drawdown
        - Value at Risk (VaR)
        """
        # Get portfolio and allocations
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio with ID {portfolio_id} not found")
        
        allocations = db.query(Allocation).filter(
            Allocation.portfolio_id == portfolio_id,
            Allocation.ticker.isnot(None)  # Must have ticker for analysis
        ).all()
        
        if not allocations:
            raise ValueError(f"Portfolio with ID {portfolio_id} has no valid allocations")
        
        # Get historical data for all tickers in portfolio
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        asset_returns = {}
        portfolio_weights = {}
        
        for allocation in allocations:
            if not allocation.ticker:
                continue
                
            # Store weight for this asset
            portfolio_weights[allocation.ticker] = allocation.allocation_percentage
            
            try:
                # Get historical data
                data = await self.market_data.get_historical_data(
                    allocation.ticker,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not data:
                    continue
                
                # Calculate daily returns
                prices = [item['close'] for item in data]
                dates = [item['date'] for item in data]
                returns = [0]  # First day has no return
                
                for i in range(1, len(prices)):
                    daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                    returns.append(daily_return)
                
                asset_returns[allocation.ticker] = {
                    'dates': dates,
                    'returns': returns
                }
            except Exception as e:
                print(f"Error processing {allocation.ticker}: {e}")
        
        if not asset_returns:
            raise ValueError("Could not retrieve historical data for any assets in portfolio")
        
        # Align all returns on same dates
        common_dates = set()
        for ticker, data in asset_returns.items():
            if not common_dates:
                common_dates = set(data['dates'])
            else:
                common_dates = common_dates.intersection(set(data['dates']))
        
        common_dates = sorted(list(common_dates))
        
        # Create returns dataframe
        returns_data = {}
        for ticker, data in asset_returns.items():
            # Create a dictionary mapping dates to returns
            date_to_return = dict(zip(data['dates'], data['returns']))
            # Extract returns for common dates
            ticker_returns = [date_to_return.get(date, 0) for date in common_dates]
            returns_data[ticker] = ticker_returns
        
        returns_df = pd.DataFrame(returns_data, index=common_dates)
        
        # Calculate risk metrics
        metrics = {}
        
        # Weights
        weights = np.array([portfolio_weights.get(ticker, 0) for ticker in returns_df.columns])
        weights = weights / weights.sum()  # Normalize weights
        
        # Portfolio returns
        portfolio_returns = returns_df.dot(weights)
        
        # Volatility (annualized)
        metrics['volatility'] = portfolio_returns.std() * np.sqrt(252)
        
        # Mean return (annualized)
        mean_return = portfolio_returns.mean() * 252
        metrics['expected_annual_return'] = mean_return
        
        # Risk-free rate (assume 2% for example)
        risk_free_rate = 0.02
        
        # Sharpe ratio
        metrics['sharpe_ratio'] = (mean_return - risk_free_rate) / metrics['volatility']
        
        # Maximum drawdown
        cum_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cum_returns.cummax()
        drawdown = (cum_returns / rolling_max) - 1
        metrics['max_drawdown'] = drawdown.min()
        
        # Value at Risk (VaR) at 95% confidence
        metrics['var_95'] = np.percentile(portfolio_returns, 5)
        
        # Beta (compared to market if we had market data)
        # For now just compute correlations between assets
        metrics['correlations'] = {}
        for i, ticker1 in enumerate(returns_df.columns):
            metrics['correlations'][ticker1] = {}
            for j, ticker2 in enumerate(returns_df.columns):
                if i <= j:  # Only compute the upper triangular matrix
                    corr = returns_df[ticker1].corr(returns_df[ticker2])
                    metrics['correlations'][ticker1][ticker2] = corr
        
        return metrics
    
    async def compare_portfolios(
        self, 
        db: Session, 
        portfolio_ids: List[int],
        days: int = 365
    ) -> Dict:
        """
        Compare risk and performance metrics of multiple portfolios
        """
        results = {}
        
        for portfolio_id in portfolio_ids:
            try:
                metrics = await self.calculate_portfolio_risk_metrics(db, portfolio_id, days)
                portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
                
                if portfolio:
                    results[portfolio_id] = {
                        'name': portfolio.name,
                        'risk_profile': portfolio.risk_profile,
                        'metrics': metrics
                    }
            except Exception as e:
                print(f"Error analyzing portfolio {portfolio_id}: {e}")
        
        return results
    
    def generate_efficient_frontier(
        self, 
        returns_df: pd.DataFrame, 
        num_portfolios: int = 1000
    ) -> List[Dict]:
        """
        Generate the efficient frontier for a set of assets
        """
        # Get mean returns and covariance matrix
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        num_assets = len(mean_returns)
        results = []
        
        # Generate random portfolios
        for i in range(num_portfolios):
            # Random weights
            weights = np.random.random(num_assets)
            weights = weights / np.sum(weights)
            
            # Portfolio return
            portfolio_return = np.sum(mean_returns * weights)
            
            # Portfolio volatility (risk)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Sharpe ratio (assuming 0% risk-free rate)
            sharpe_ratio = portfolio_return / portfolio_volatility
            
            results.append({
                'return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'weights': {asset: weight for asset, weight in zip(returns_df.columns, weights)}
            })
        
        # Sort by Sharpe ratio
        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        
        return results
    
    def get_optimal_portfolio(
        self, 
        returns_df: pd.DataFrame, 
        target_return: Optional[float] = None
    ) -> Dict:
        """
        Get the optimal portfolio based on efficient frontier analysis
        """
        efficient_frontier = self.generate_efficient_frontier(returns_df)
        
        if target_return is None:
            # Return the portfolio with the highest Sharpe ratio
            return efficient_frontier[0]
        else:
            # Find portfolio closest to target return
            return min(
                efficient_frontier, 
                key=lambda x: abs(x['return'] - target_return)
            )