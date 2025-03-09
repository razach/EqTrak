from typing import List, Dict, Any, Optional, Union, Callable, TypeVar, cast
from datetime import date, datetime, timedelta
import logging
from decimal import Decimal
import functools

from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User

from .models import Security, PriceData, MarketDataSettings
from .providers.factory import get_provider

logger = logging.getLogger(__name__)

# Type variable for the decorator
T = TypeVar('T')

def check_market_data_access(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to check if market data access is enabled before executing the decorated function.
    Checks both system-wide settings and user-specific settings if a user is provided.
    
    Usage:
        @check_market_data_access
        def some_function_that_accesses_market_data(self, user=None, ...):
            # This will only execute if market data access is allowed
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Try to find the user parameter
        user = kwargs.get('user')
        
        # Check service class methods where 'self' is first arg and user might be positional
        if user is None and len(args) > 1 and isinstance(args[0], MarketDataService):
            # For instance methods: check if there's a user in positional args
            # Method signature would be (self, param1, param2, user=None, ...)
            method = func.__code__
            param_names = method.co_varnames[:method.co_argcount]
            if 'user' in param_names:
                user_index = param_names.index('user')
                if user_index < len(args):  # User is provided as positional arg
                    user = args[user_index]
        
        # Check if market data is enabled
        if not MarketDataService.is_updates_enabled(user):
            logger.info(f"Market data access blocked for {'system' if user is None else user.username}")
            
            # Return appropriate fallback value based on function's return annotation
            return_annotation = func.__annotations__.get('return')
            if return_annotation is bool:
                return False
            elif return_annotation in (dict, Dict):
                return {}
            elif return_annotation in (list, List):
                return []
            else:
                return None
                
        # Market data access is allowed, proceed with the function call
        return func(*args, **kwargs)
        
    return cast(Callable[..., T], wrapper)

class MarketDataService:
    """
    Service class for interacting with market data.
    Provides methods for retrieving and managing securities and price data.
    """
    
    @staticmethod
    @check_market_data_access
    def get_or_create_security(symbol: str, user=None) -> Security:
        """
        Get a security by symbol or create it if it doesn't exist.
        
        Args:
            symbol: The ticker symbol to look up
            user: Optional user context for permissions
            
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
    @check_market_data_access
    def get_latest_price(security: Union[Security, str], user=None) -> Dict[str, Any]:
        """
        Get the latest price data for a security.
        
        Args:
            security: Security object or ticker symbol
            user: Optional user context for permissions
            
        Returns:
            Dict containing price data
        """
        if isinstance(security, str):
            security = MarketDataService.get_or_create_security(security, user=user)
            
        provider = get_provider()
        price_data = provider.get_latest_price(security.symbol)
        
        # Convert price data to a standardized format
        result = {
            'symbol': security.symbol,
            'date': price_data['date'],
            'price': price_data['close'],
            'change': price_data.get('change', None),
            'change_percent': price_data.get('change_percent', None),
            'volume': price_data.get('volume', None),
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    @staticmethod
    @check_market_data_access
    def get_price_history(
        security: Union[Security, str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: Optional[int] = None,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for a security.
        
        Args:
            security: Security object or ticker symbol
            start_date: Optional start date (defaults to 1 year ago)
            end_date: Optional end date (defaults to today)
            days: Optional number of days to retrieve (alternative to start_date)
            user: Optional user context for permissions
            
        Returns:
            List of dicts with historical price data
        """
        if isinstance(security, str):
            security = MarketDataService.get_or_create_security(security, user=user)
            
        if not end_date:
            end_date = date.today()
            
        if days:
            start_date = end_date - timedelta(days=days)
        elif not start_date:
            # Default to 1 year history
            start_date = end_date - timedelta(days=365)
            
        provider = get_provider()
        price_data_list = provider.get_historical_prices(
            security.symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to standard format
        result = []
        for price_data in price_data_list:
            result.append({
                'symbol': security.symbol,
                'date': price_data['date'],
                'open': price_data['open'],
                'high': price_data['high'],
                'low': price_data['low'],
                'close': price_data['close'],
                'volume': price_data['volume']
            })
            
        return result
    
    @staticmethod
    @check_market_data_access
    def search_securities(query: str, user=None) -> List[Dict[str, Any]]:
        """
        Search for securities matching the query.
        
        Args:
            query: Search term (partial symbol or name)
            user: Optional user context for permissions
            
        Returns:
            List of matching securities
        """
        # Try local search first
        local_results = Security.objects.filter(
            Q(symbol__icontains=query) | Q(name__icontains=query)
        )[:5]  # Limit to 5 results
        
        if local_results.exists():
            return [
                {
                    'symbol': security.symbol,
                    'name': security.name,
                    'type': security.security_type,
                    'exchange': security.exchange
                }
                for security in local_results
            ]
        
        # If no local results, try provider search
        provider = get_provider()
        return provider.search_securities(query)
    
    @staticmethod
    def is_updates_enabled(user=None):
        """
        Check if market data updates are enabled, considering both system and user settings.
        System settings override user preferences.
        
        Args:
            user: Optional user to check settings for. If None, only system setting is checked.
            
        Returns:
            bool: True if updates are enabled, False otherwise
        """
        # System-wide setting takes precedence - if disabled at system level, nothing can override it
        if not MarketDataSettings.is_updates_enabled():
            return False
            
        # If no user provided, return system setting
        if user is None:
            return True
            
        # Check user-specific setting
        try:
            return user.settings.market_data_enabled
        except (AttributeError, Exception):
            # Default to True if user settings don't exist
            return True
            
    @staticmethod
    @check_market_data_access
    def refresh_security_data(security: Union[Security, str], user=None) -> bool:
        """
        Refresh price data for a security.
        
        Args:
            security: Security object or ticker symbol
            user: Optional user context for permissions check
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Note: permissions check handled by the decorator
            
        if isinstance(security, str):
            security = MarketDataService.get_or_create_security(security, user=user)
            
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
            
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing data for {getattr(security, 'symbol', security)}: {e}")
            return False

    @staticmethod
    @check_market_data_access
    def sync_price_with_metrics(position, user=None):
        """
        Synchronize latest price data with the metrics system.
        Only updates the Market Price metric, leaving Current Value to be computed dynamically.
        
        Args:
            position: Position object to update metrics for
            user: Optional user context for permissions check
            
        Returns:
            Updated metric value or None if update failed
        """
        # Note: Access check is now handled by the decorator
            
        try:
            from metrics.models import MetricType, MetricValue
            
            # Get security by ticker since Position doesn't have a direct security field
            try:
                security = MarketDataService.get_or_create_security(position.ticker, user=user)
            except Exception as e:
                logger.error(f"Error getting security for {position.ticker}: {e}")
                return None
                
            # Get latest price data
            try:
                latest_price = MarketDataService.get_latest_price(security, user=user)
            except ValueError as e:
                logger.warning(f"Could not get latest price for {position.ticker}: {e}")
                return None
                
            # Find "Market Price" metric
            try:
                market_price_metric = MetricType.objects.get(
                    code='MARKET_PRICE',
                    scope_type='POSITION',
                    is_system=True
                )
            except MetricType.DoesNotExist:
                logger.error("MARKET_PRICE metric type not found")
                return None
            
            # Create or update the metric value
            metric_value, created = MetricValue.objects.update_or_create(
                metric_type=market_price_metric,
                position=position,
                defaults={
                    'value': latest_price['price'],
                    'value_date': date.fromisoformat(latest_price['date']),
                }
            )
            
            logger.debug(f"Updated market price metric for {position.ticker}: {metric_value.value}")
            return metric_value
            
        except Exception as e:
            logger.error(f"Error syncing price with metrics for {position.ticker}: {e}")
            return None

