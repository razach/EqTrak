from django.conf import settings
from .base import MarketDataProviderBase
from .yahoo import YahooFinanceProvider
from .alpha_vantage import AlphaVantageProvider

def get_provider(user=None) -> MarketDataProviderBase:
    """
    Factory function to get the configured market data provider.
    
    Args:
        user: Optional user to consider provider preferences for
    
    Returns:
        An instance of the configured market data provider.
        
    Raises:
        ValueError: If the configured provider is not valid.
    """
    # Default to system setting
    provider_name = getattr(settings, 'MARKET_DATA_PROVIDER', 'yahoo')
    
    # If user is provided, check for user preference
    if user is not None and hasattr(user, 'settings'):
        # If user has selected a specific provider (not 'system'), use it
        if user.settings.market_data_provider != 'system':
            provider_name = user.settings.market_data_provider
    
    if provider_name == 'yahoo':
        return YahooFinanceProvider()
    elif provider_name == 'alpha_vantage':
        provider = AlphaVantageProvider()
        # If user has a custom API key, use it
        if user and hasattr(user, 'settings') and user.settings.alpha_vantage_api_key:
            provider.api_key = user.settings.alpha_vantage_api_key
        return provider
    
    # Add more providers as needed
    
    raise ValueError(f"Unknown market data provider: {provider_name}")
