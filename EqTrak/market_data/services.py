from typing import List, Dict, Any, Optional, Union
from datetime import date, datetime, timedelta
import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from .models import Security, PriceData, MarketDataSettings
from .providers.factory import get_provider

logger = logging.getLogger(__name__)

class MarketDataService:
    """
    Service class for interacting with market data.
    Provides methods for retrieving and managing securities and price data.
    """
    
    @staticmethod
    def get_or_create_security(symbol: str) -> Security:
        """
        Get a security by symbol or create it if it doesn't exist.
        
        Args:
            symbol: The ticker symbol to look up
            
        Returns:
            Security object
            
        Raises:
            ValueError: If the security cannot be found via provider
        """
        # Try to find existing security
        symbol = symbol.upper()  # Normalize symbol
        try:
            security = Security.objects.get(symbol=symbol)
            if not security.active:
                security.active = True
                security.save(update_fields=['active', 'updated_at'])
            return security
        except Security.DoesNotExist:
            # Create new security
            provider = get_provider()
            security_info = provider.get_security_info(symbol)
            
            with transaction.atomic():
                security = Security.objects.create(
                    symbol=symbol,
                    name=security_info['name'],
                    security_type=security_info['security_type'],
                    exchange=security_info['exchange'],
                    currency=security_info['currency']
                )
                
            # Fetch initial price history in the background
            # This could be done via a Celery task
            # fetch_price_history_task.delay(security.id)
            
            return security
            
    @staticmethod
    def get_latest_price(security: Union[Security, str]) -> Dict[str, Any]:
        """
        Get the latest price for a security.
        
        Args:
            security: Security object or symbol string
            
        Returns:
            Dictionary with price information
            
        Raises:
            ValueError: If no price data is available
        """
        if isinstance(security, str):
            security = MarketDataService.get_or_create_security(security)
            
        # Check for recent cached price
        latest_price = PriceData.objects.filter(
            security=security
        ).order_by('-date').first()
        
        # If we have a recent price (today or yesterday during weekend/holiday), return it
        if (latest_price and 
            (latest_price.date >= date.today() - timedelta(days=3))):
            return {
                'date': latest_price.date.isoformat(),
                'price': latest_price.close,
                'source': latest_price.source,
                'is_stale': False
            }
        
        # Check if updates are enabled before making API call
        if not MarketDataSettings.is_updates_enabled():
            # If updates are disabled and we have any price, mark it as stale but return it
            if latest_price:
                return {
                    'date': latest_price.date.isoformat(),
                    'price': latest_price.close,
                    'source': latest_price.source,
                    'is_stale': True
                }
            else:
                raise ValueError(f"No price data available for {security.symbol} and market data updates are disabled")
            
        # Otherwise fetch latest price from provider
        try:
            provider = get_provider()
            price_data = provider.get_latest_price(security.symbol)
            
            # Save the new price data
            price_date = date.fromisoformat(price_data['date'])
            price, created = PriceData.objects.update_or_create(
                security=security,
                date=price_date,
                defaults={
                    'open': price_data['open'],
                    'high': price_data['high'],
                    'low': price_data['low'],
                    'close': price_data['close'],
                    'adj_close': price_data['adj_close'],
                    'volume': price_data['volume'],
                    'source': provider.__class__.__name__
                }
            )
            
            return {
                'date': price_date.isoformat(),
                'price': price.close,
                'source': price.source,
                'is_stale': False
            }
        except Exception as e:
            logger.error(f"Error fetching latest price for {security.symbol}: {e}")
            
            # If we have any historical price, return it but mark as stale
            if latest_price:
                return {
                    'date': latest_price.date.isoformat(),
                    'price': latest_price.close,
                    'source': latest_price.source,
                    'is_stale': True
                }
                
            raise ValueError(f"No price data available for {security.symbol}")
    
    @staticmethod
    def get_price_history(
        security: Union[Security, str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for a security.
        
        Args:
            security: Security object or symbol string
            start_date: Start date for data (optional)
            end_date: End date for data (optional, defaults to today)
            days: Number of days of history (alternative to start_date)
            
        Returns:
            List of dictionaries with price data
        """
        if isinstance(security, str):
            security = MarketDataService.get_or_create_security(security)
            
        if end_date is None:
            end_date = date.today()
            
        if start_date is None and days:
            start_date = end_date - timedelta(days=days)
        elif start_date is None:
            start_date = end_date - timedelta(days=30)  # Default to 30 days
            
        # First check our database for cached price history
        cached_prices = PriceData.objects.filter(
            security=security,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # If we have complete data for the requested period, return it
        if cached_prices.count() >= (end_date - start_date).days * 0.7:  # Allow for weekends/holidays
            return [
                {
                    'date': price.date.isoformat(),
                    'open': float(price.open),
                    'high': float(price.high),
                    'low': float(price.low),
                    'close': float(price.close),
                    'adj_close': float(price.adj_close),
                    'volume': int(price.volume)
                }
                for price in cached_prices
            ]
        
        # Check if updates are enabled
        if not MarketDataSettings.is_updates_enabled():
            # If we have any data, return what we have and don't fetch more
            if cached_prices.exists():
                logger.warning(f"Market data updates disabled. Returning partial history for {security.symbol}.")
                return [
                    {
                        'date': price.date.isoformat(),
                        'open': float(price.open),
                        'high': float(price.high),
                        'low': float(price.low),
                        'close': float(price.close),
                        'adj_close': float(price.adj_close),
                        'volume': int(price.volume)
                    }
                    for price in cached_prices
                ]
            else:
                logger.warning(f"Market data updates disabled and no history available for {security.symbol}.")
                return []
            
        # Otherwise fetch from provider and cache results
        try:
            provider = get_provider()
            price_data_list = provider.get_historical_prices(
                security.symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            # Process and save the new price data
            with transaction.atomic():
                for price_data in price_data_list:
                    price_date = date.fromisoformat(price_data['date'])
                    PriceData.objects.update_or_create(
                        security=security,
                        date=price_date,
                        defaults={
                            'open': price_data['open'],
                            'high': price_data['high'],
                            'low': price_data['low'],
                            'close': price_data['close'],
                            'adj_close': price_data['adj_close'],
                            'volume': price_data['volume'],
                            'source': provider.__class__.__name__
                        }
                    )
            
            # Return the newly fetched and saved data
            updated_prices = PriceData.objects.filter(
                security=security,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            return [
                {
                    'date': price.date.isoformat(),
                    'open': float(price.open),
                    'high': float(price.high),
                    'low': float(price.low),
                    'close': float(price.close),
                    'adj_close': float(price.adj_close),
                    'volume': int(price.volume)
                }
                for price in updated_prices
            ]
        except Exception as e:
            logger.error(f"Error fetching price history for {security.symbol}: {e}")
            
            # If we have any cached data, return that partial result
            if cached_prices.exists():
                return [
                    {
                        'date': price.date.isoformat(),
                        'open': float(price.open),
                        'high': float(price.high),
                        'low': float(price.low),
                        'close': float(price.close),
                        'adj_close': float(price.adj_close),
                        'volume': int(price.volume)
                    }
                    for price in cached_prices
                ]
                
            raise ValueError(f"Unable to retrieve price history for {security.symbol}: {e}")
    
    @staticmethod
    def search_securities(query: str) -> List[Dict[str, Any]]:
        """
        Search for securities by name or symbol.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching securities
        """
        # First try to find matches in our database
        db_results = Security.objects.filter(
            symbol__icontains=query
        ).union(
            Security.objects.filter(name__icontains=query)
        )[:10]
        
        if db_results.exists():
            return [
                {
                    'symbol': security.symbol,
                    'name': security.name,
                    'exchange': security.exchange,
                    'security_type': security.security_type
                }
                for security in db_results
            ]
        
        # If no matches in our database, search via provider
        try:
            provider = get_provider()
            results = provider.search_securities(query)
            
            # Optionally save these securities to our database
            # This could be done in the background
            
            return results
        except Exception as e:
            logger.error(f"Error searching securities for '{query}': {e}")
            return []
    
    @staticmethod
    def refresh_security_data(security: Union[Security, str]) -> bool:
        """
        Refresh all data for a security.
        
        Args:
            security: Security object or symbol string
            
        Returns:
            True if successful, False otherwise
        """
        # Check if updates are enabled
        if not MarketDataSettings.is_updates_enabled():
            logger.warning(f"Market data updates are disabled. Skipping refresh for {security}.")
            return False
            
        if isinstance(security, str):
            security = MarketDataService.get_or_create_security(security)
            
        try:
            # Refresh security info
            provider = get_provider()
            security_info = provider.get_security_info(security.symbol)
            
            # Update security record
            security.name = security_info['name']
            security.security_type = security_info['security_type']
            security.exchange = security_info['exchange']
            security.currency = security_info['currency']
            security.save()
            
            # Get latest price data
            latest_price = provider.get_latest_price(security.symbol)
            price_date = date.fromisoformat(latest_price['date'])
            
            PriceData.objects.update_or_create(
                security=security,
                date=price_date,
                defaults={
                    'open': latest_price['open'],
                    'high': latest_price['high'],
                    'low': latest_price['low'],
                    'close': latest_price['close'],
                    'adj_close': latest_price['adj_close'],
                    'volume': latest_price['volume'],
                    'source': provider.__class__.__name__
                }
            )
            
            # Success
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing data for {security.symbol}: {e}")
            return False

    @staticmethod
    def sync_price_with_metrics(position):
        """
        Synchronize latest price data with the metrics system.
        Only updates the Market Price metric, leaving Current Value to be computed dynamically.
        
        Args:
            position: Position object to update metrics for
            
        Returns:
            Updated metric value or None if update failed
        """
        # Check if updates are enabled before doing anything
        if not MarketDataSettings.is_updates_enabled():
            logger.debug(f"Market data updates are disabled. Skipping sync for {position.ticker}.")
            return None
            
        try:
            from metrics.models import MetricType, MetricValue
            
            # Get security by ticker since Position doesn't have a direct security field
            try:
                security = MarketDataService.get_or_create_security(position.ticker)
            except Exception as e:
                logger.error(f"Error getting security for {position.ticker}: {e}")
                return None
                
            # Get latest price data - the get_latest_price method now checks if updates are enabled
            try:
                latest_price = MarketDataService.get_latest_price(security)
            except ValueError as e:
                logger.warning(f"Could not get latest price for {position.ticker}: {e}")
                return None
            
            # Get or create the Market Price metric type
            market_price_metric, _ = MetricType.objects.get_or_create(
                name='Market Price',
                defaults={
                    'scope_type': 'POSITION',
                    'data_type': 'PRICE',
                    'is_system': True,
                    'description': 'Current market price from data provider'
                }
            )
            
            # Create or update the metric value
            price_date = date.fromisoformat(latest_price['date'])
            metric_value, created = MetricValue.objects.update_or_create(
                position=position,
                metric_type=market_price_metric,
                date=price_date,
                defaults={
                    'value': latest_price['price'],
                    'source': latest_price['source'],
                    'is_forecast': False,
                    'notes': 'Auto-updated from market data service'
                }
            )
            
            return metric_value
        except Exception as e:
            logger.error(f"Error syncing price metrics for {position}: {e}")
            return None

