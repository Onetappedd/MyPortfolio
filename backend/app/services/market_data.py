import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

class MarketDataService:
    """Service to interact with financial market data APIs"""
    
    def __init__(self):
        # Set API keys from environment variables
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY", "")
        
        # Cache for price data to reduce API calls
        self._price_cache = {}
        self._cache_expiry = {}
        self._cache_duration = timedelta(minutes=15)  # Cache prices for 15 minutes
    
    async def get_latest_price(self, symbol: str) -> float:
        """Get the latest price for a given ticker symbol"""
        # Check cache first
        now = datetime.utcnow()
        if symbol in self._price_cache and now < self._cache_expiry.get(symbol, now):
            return self._price_cache[symbol]
        
        # Not in cache or cache expired, fetch from API
        try:
            price = await self._fetch_price_alpha_vantage(symbol)
            
            # Update cache
            self._price_cache[symbol] = price
            self._cache_expiry[symbol] = now + self._cache_duration
            
            return price
        except Exception as e:
            # Fallback to another provider if primary fails
            try:
                price = await self._fetch_price_finnhub(symbol)
                
                # Update cache
                self._price_cache[symbol] = price
                self._cache_expiry[symbol] = now + self._cache_duration
                
                return price
            except Exception as inner_e:
                # If all providers fail, raise error
                raise Exception(f"Failed to fetch price for {symbol}: {str(e)}, {str(inner_e)}")
    
    async def _fetch_price_alpha_vantage(self, symbol: str) -> float:
        """Fetch price data from Alpha Vantage API"""
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract price from response
                    if "Global Quote" in data and "05. price" in data["Global Quote"]:
                        return float(data["Global Quote"]["05. price"])
                    else:
                        raise Exception(f"Invalid response format from Alpha Vantage for {symbol}")
                else:
                    raise Exception(f"Alpha Vantage API returned status code {response.status}")
    
    async def _fetch_price_finnhub(self, symbol: str) -> float:
        """Fetch price data from Finnhub API as fallback"""
        if not self.finnhub_api_key:
            raise Exception("Finnhub API key not set")
        
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract price from response
                    if "c" in data:  # Current price
                        return float(data["c"])
                    else:
                        raise Exception(f"Invalid response format from Finnhub for {symbol}")
                else:
                    raise Exception(f"Finnhub API returned status code {response.status}")
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get historical price data for a given ticker symbol"""
        if not end_date:
            end_date = datetime.utcnow()
            
        if not start_date:
            # Default to last 1 year
            start_date = end_date - timedelta(days=365)
        
        # Format dates for API
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
            f"&symbol={symbol}&apikey={self.alpha_vantage_api_key}"
            f"&outputsize=full"
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract historical data
                    if "Time Series (Daily)" in data:
                        time_series = data["Time Series (Daily)"]
                        result = []
                        
                        for date_str, values in time_series.items():
                            date = datetime.strptime(date_str, "%Y-%m-%d")
                            
                            # Only include dates within the range
                            if start_date <= date <= end_date:
                                result.append({
                                    "date": date_str,
                                    "open": float(values["1. open"]),
                                    "high": float(values["2. high"]),
                                    "low": float(values["3. low"]),
                                    "close": float(values["4. close"]),
                                    "volume": float(values["5. volume"])
                                })
                        
                        # Sort by date ascending
                        return sorted(result, key=lambda x: x["date"])
                    else:
                        raise Exception(f"Invalid response format from Alpha Vantage for {symbol}")
                else:
                    raise Exception(f"Alpha Vantage API returned status code {response.status}")
    
    async def search_symbols(self, query: str) -> List[Dict]:
        """Search for ticker symbols based on a query"""
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={self.alpha_vantage_api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract search results
                    if "bestMatches" in data:
                        return [
                            {
                                "symbol": item["1. symbol"],
                                "name": item["2. name"],
                                "type": item["3. type"],
                                "region": item["4. region"],
                                "currency": item["8. currency"],
                            }
                            for item in data["bestMatches"]
                        ]
                    else:
                        return []
                else:
                    raise Exception(f"Alpha Vantage API returned status code {response.status}")