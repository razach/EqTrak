from django import template
from market_data.models import MarketDataSettings

register = template.Library()

@register.simple_tag
def get_market_data_system_setting():
    """Returns the system-wide market data enabled setting."""
    return MarketDataSettings.is_updates_enabled() 