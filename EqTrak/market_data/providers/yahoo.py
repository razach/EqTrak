import yfinance as yf
from typing import Dict, List, Any, Optional, Tuple
from datetime import date, datetime, timedelta
import pandas as pd
import logging
import time
import requests
from urllib3.exceptions import MaxRetryError, NewConnectionError

from .base import MarketDataProviderBase

logger = logging.getLogger(__name__)

class YahooFinanceProvider(MarketDataProviderBase):
    """
    Yahoo Finance implementation of the market data provider.
    Uses the yfinance library to fetch data from Yahoo Finance.
    """
    
    def __init__(self, max_retries=3, retry_delay=2, timeout=10):
        """
        Initialize the Yahoo Finance provider
        
        Args:
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay in seconds between retries
            timeout: Timeout in seconds for API calls
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
    
    def _execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic
        """
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.RequestException, MaxRetryError, NewConnectionError, ConnectionError) as e:
                last_error = e
                retries += 1
                logger.warning(f"API call failed (attempt {retries}/{self.max_retries}): {str(e)}")
                
                if "429" in str(e) or "Too Many Requests" in str(e):
                    # Exponential backoff for rate limiting
                    sleep_time = self.retry_delay * (2 ** (retries - 1))
                    logger.warning(f"Rate limited, waiting {sleep_time} seconds before retry")
                    time.sleep(sleep_time)
                else:
                    time.sleep(self.retry_delay)
            except Exception as e:
                # Don't retry other exceptions
                logger.error(f"Unexpected error: {str(e)}")
                raise
        
        # If we get here, all retries failed
        logger.error(f"Max retries exceeded: {str(last_error)}")
        raise last_error
    
    def get_security_info(self, symbol: str) -> Dict[str, Any]:
        """
        Retrieve basic information about a security from Yahoo Finance
        """
        try:
            def fetch_info():
                ticker = yf.Ticker(symbol)
                return ticker.info
            
            info = self._execute_with_retry(fetch_info)
            
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
            def fetch_history():
                ticker = yf.Ticker(symbol)
                return ticker.history(period='1d')
            
            hist = self._execute_with_retry(fetch_history)
            
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
            def fetch_historical():
                ticker = yf.Ticker(symbol)
                # If dates are provided, use them; otherwise use period
                if start_date and end_date:
                    return ticker.history(start=start_date, end=end_date)
                else:
                    return ticker.history(period=period)
            
            hist = self._execute_with_retry(fetch_historical)
            
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
            def fetch_tickers():
                # Yahoo Finance doesn't have a great search API in yfinance
                return yf.Tickers(query)
            
            tickers = self._execute_with_retry(fetch_tickers)
            results = []
            
            for symbol in tickers.tickers:
                try:
                    def fetch_ticker_info():
                        return tickers.tickers[symbol].info
                    
                    info = self._execute_with_retry(fetch_ticker_info)
                    
                    if info:
                        results.append({
                            'symbol': symbol,
                            'name': info.get('shortName', info.get('longName', symbol)),
                            'exchange': info.get('exchange', ''),
                            'security_type': self._determine_security_type(info)
                        })
                except Exception:
                    # Skip tickers that fail to load
                    logger.debug(f"Failed to load ticker info for {symbol}")
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
