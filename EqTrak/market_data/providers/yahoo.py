import yfinance as yf
from typing import Dict, List, Any, Optional, Tuple
from datetime import date, datetime, timedelta
import pandas as pd
import logging

from .base import MarketDataProviderBase

logger = logging.getLogger(__name__)

class YahooFinanceProvider(MarketDataProviderBase):
    """
    Yahoo Finance implementation of the market data provider.
    Uses the yfinance library to fetch data from Yahoo Finance.
    """
    
    def get_security_info(self, symbol: str) -> Dict[str, Any]:
        """
        Retrieve basic information about a security from Yahoo Finance
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract relevant information
            security_info = {
                'symbol': symbol,
                'name': info.get('shortName', info.get('longName', symbol)),
                'security_type': self._determine_security_type(info),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', 'USD')
            }
            return security_info
        except Exception as e:
            logger.error(f"Error fetching security info for {symbol}: {str(e)}")
            raise ValueError(f"Unable to retrieve security information for {symbol}: {str(e)}")
    
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest available price for a security from Yahoo Finance
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            
            if hist.empty:
                raise ValueError(f"No price data available for {symbol}")
                
            row = hist.iloc[0]
            return {
                'date': hist.index[0].date().isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'adj_close': float(row['Close']),  # Yahoo already adjusts Close
                'volume': int(row['Volume'])
            }
        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {str(e)}")
            raise ValueError(f"Unable to retrieve latest price for {symbol}: {str(e)}")
    
    def get_historical_prices(self, 
                             symbol: str, 
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             period: str = 'max') -> List[Dict[str, Any]]:
        """
        Get historical price data from Yahoo Finance
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # If dates are provided, use them; otherwise use period
            if start_date and end_date:
                hist = ticker.history(start=start_date, end=end_date)
            else:
                hist = ticker.history(period=period)
            
            if hist.empty:
                return []
                
            # Convert DataFrame to list of dictionaries
            result = []
            for date_idx, row in hist.iterrows():
                price_data = {
                    'date': date_idx.date().isoformat(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'adj_close': float(row['Close']),  # Yahoo already adjusts Close
                    'volume': int(row['Volume'])
                }
                result.append(price_data)
            
            return result
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {str(e)}")
            raise ValueError(f"Unable to retrieve historical prices for {symbol}: {str(e)}")

    def search_securities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for securities by name or symbol using Yahoo Finance
        """
        try:
            # Yahoo Finance doesn't have a great search API in yfinance
            # This is a simplified implementation
            tickers = yf.Tickers(query)
            results = []
            
            for symbol in tickers.tickers:
                try:
                    info = tickers.tickers[symbol].info
                    if info:
                        results.append({
                            'symbol': symbol,
                            'name': info.get('shortName', info.get('longName', symbol)),
                            'exchange': info.get('exchange', ''),
                            'security_type': self._determine_security_type(info)
                        })
                except:
                    # Skip tickers that fail to load
                    pass
                    
            return results
        except Exception as e:
            logger.error(f"Error searching securities for '{query}': {str(e)}")
            return []
    
    def _determine_security_type(self, info: Dict[str, Any]) -> str:
        """
        Determine the security type based on Yahoo Finance info
        """
        quote_type = info.get('quoteType', '').lower()
        
        if quote_type == 'equity':
            return 'stock'
        elif quote_type == 'etf':
            return 'etf'
        elif quote_type == 'mutualfund':
            return 'mutual_fund'
        elif quote_type == 'cryptocurrency':
            return 'crypto'
        else:
            return 'other'
