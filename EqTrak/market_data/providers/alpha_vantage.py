import requests
from datetime import date, datetime, timedelta
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from django.conf import settings

from .base import MarketDataProviderBase

logger = logging.getLogger(__name__)

class AlphaVantageProvider(MarketDataProviderBase):
    """
    Market data provider implementation using Alpha Vantage API.
    https://www.alphavantage.co/documentation/
    """
    
    def __init__(self):
        """Initialize the Alpha Vantage provider."""
        self.api_key = None
        self.base_url = "https://www.alphavantage.co/query"
    
    def _check_api_key(self):
        """Check if API key is set and raise error if not."""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required. Please set it in your user settings.")
    
    def get_security_info(self, symbol: str) -> Dict[str, str]:
        """
        Get information about a security by its symbol.
        
        Args:
            symbol: The ticker symbol to look up
            
        Returns:
            Dict with security information
            
        Raises:
            ValueError: If the security cannot be found or API key is not set
        """
        self._check_api_key()
        
        # For Alpha Vantage, we'll use the OVERVIEW endpoint to get company information
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve data for {symbol}: HTTP {response.status_code}")
        
        data = response.json()
        
        # Check if we got valid data
        if "Symbol" not in data:
            raise ValueError(f"Security not found: {symbol}")
        
        # Map Alpha Vantage data to our required format
        return {
            "name": data.get("Name", symbol),
            "security_type": "STOCK",  # Default to STOCK, Alpha Vantage doesn't clearly provide this
            "exchange": data.get("Exchange", ""),
            "currency": data.get("Currency", "USD")
        }
    
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price data for a security.
        
        Args:
            symbol: The ticker symbol
            
        Returns:
            Dict with latest price data
            
        Raises:
            ValueError: If the price data cannot be found or API key is not set
        """
        self._check_api_key()
        
        # Use GLOBAL_QUOTE endpoint for latest price
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve latest price for {symbol}: HTTP {response.status_code}")
        
        data = response.json()
        
        # Check if we got valid data
        if "Global Quote" not in data or not data["Global Quote"]:
            raise ValueError(f"Latest price not found for: {symbol}")
        
        quote = data["Global Quote"]
        
        # Calculate change_percent from change and price
        price = float(quote.get("05. price", 0))
        change = float(quote.get("09. change", 0))
        change_percent = (change / (price - change)) * 100 if price != change else 0
        
        # Map to our expected format
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),  # Alpha Vantage doesn't provide exact date in GLOBAL_QUOTE
            "open": float(quote.get("02. open", 0)),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "close": price,
            "adj_close": price,  # Alpha Vantage doesn't provide adjusted close in GLOBAL_QUOTE
            "volume": int(quote.get("06. volume", 0)),
            "change": change,
            "change_percent": change_percent
        }
    
    def get_historical_prices(
        self, 
        symbol: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for a security.
        
        Args:
            symbol: The ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            List of dicts with historical price data
            
        Raises:
            ValueError: If the historical data cannot be found or API key is not set
        """
        self._check_api_key()
        
        # Use TIME_SERIES_DAILY_ADJUSTED for historical data
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full" if (end_date - start_date).days > 100 else "compact",
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve historical prices for {symbol}: HTTP {response.status_code}")
        
        data = response.json()
        
        # Check if we got valid data
        if "Time Series (Daily)" not in data:
            raise ValueError(f"Historical price data not found for: {symbol}")
        
        time_series = data["Time Series (Daily)"]
        
        # Filter and format the historical data
        result = []
        for date_str, values in time_series.items():
            price_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Filter by date range
            if start_date <= price_date <= end_date:
                result.append({
                    "date": date_str,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "adj_close": float(values.get("5. adjusted close", 0)),
                    "volume": int(values.get("6. volume", 0))
                })
        
        # Sort by date
        result.sort(key=lambda x: x["date"])
        return result
    
    def search_securities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for securities matching the query.
        
        Args:
            query: Search term (partial symbol or name)
            
        Returns:
            List of matching securities
            
        Raises:
            ValueError: If the search cannot be performed or API key is not set
        """
        self._check_api_key()
        
        # Use SYMBOL_SEARCH endpoint
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": query,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise ValueError(f"Failed to search securities: HTTP {response.status_code}")
        
        data = response.json()
        
        # Check if we got valid data
        if "bestMatches" not in data:
            return []
        
        matches = data["bestMatches"]
        
        # Format results
        result = []
        for match in matches:
            result.append({
                "symbol": match.get("1. symbol", ""),
                "name": match.get("2. name", ""),
                "type": match.get("3. type", ""),
                "exchange": match.get("4. region", "")
            })
        
        return result[:5]  # Limit to 5 results to match the behavior in services.py
