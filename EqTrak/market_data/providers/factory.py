from django.conf import settings
from .base import MarketDataProviderBase
from .yahoo import YahooFinanceProvider

def get_provider() -> MarketDataProviderBase:
    """
    Factory function to get the configured market data provider.
    
    Returns:
        An instance of the configured market data provider.
        
    Raises:
        ValueError: If the configured provider is not valid.
    """
    provider_name = getattr(settings, 'MARKET_DATA_PROVIDER', 'yahoo')
    
    if provider_name == 'yahoo':
        return YahooFinanceProvider()
    
    # Add more providers as needed
    
    raise ValueError(f"Unknown market data provider: {provider_name}")
