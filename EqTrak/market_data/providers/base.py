from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import date, datetime, timedelta

class MarketDataProviderBase(ABC):
    """
    Base class for market data providers.
    All concrete providers must implement these methods.
    """
    
    @abstractmethod
    def get_security_info(self, symbol: str) -> Dict[str, Any]:
        """
        Retrieve basic information about a security
        
        Args:
            symbol: The ticker symbol to look up
            
        Returns:
            Dictionary with security information (name, exchange, etc.)
            
        Raises:
            ValueError: If the security cannot be found
        """
        pass
    
    @abstractmethod
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest available price for a security
        
        Args:
            symbol: The ticker symbol to look up
            
        Returns:
            Dictionary with price information
            
        Raises:
            ValueError: If the price data cannot be retrieved
        """
        pass
    
    @abstractmethod
    def get_historical_prices(self, 
                             symbol: str, 
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             period: str = 'max') -> List[Dict[str, Any]]:
        """
        Get historical price data for a security
        
        Args:
            symbol: The ticker symbol
            start_date: Start date for data (optional)
            end_date: End date for data (optional)
            period: Time period (e.g., '1d', '1mo', '1y', 'max')
            
        Returns:
            List of dictionaries with historical price data
            
        Raises:
            ValueError: If the historical data cannot be retrieved
        """
        pass

    @abstractmethod
    def search_securities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for securities by name or symbol
        
        Args:
            query: Search query string
            
        Returns:
            List of matching securities
        """
        pass
