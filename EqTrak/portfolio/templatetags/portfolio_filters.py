from django import template
from django.template.defaultfilters import floatformat
from portfolio.models import Portfolio

register = template.Library()

@register.filter(name='metric_display_value')
def metric_display_value(position, metric_name):
    """Get formatted display value for a metric"""
    value = position.get_metric_value(metric_name)
    if value is None:
        return None
        
    if metric_name in ['Market Price', 'Cost Basis', 'Current Value']:
        return f"{position.portfolio.currency} {floatformat(value, 2)}"
    elif metric_name in ['Position Gain/Loss']:
        return f"{floatformat(value, 2)}%"
    else:
        return f"{floatformat(value, 2)}"

@register.filter(name='portfolio_metric_value')
def portfolio_metric_value(portfolio, metric_name):
    """Get portfolio metric value"""
    # Check if we have a valid Portfolio instance
    if not isinstance(portfolio, Portfolio):
        return None
    
    # Get the raw value from the model
    value = portfolio.get_metric_value(metric_name)
    
    # For absolute metrics, ensure we're returning a raw numeric value
    if value is not None and '(Absolute)' in metric_name:
        try:
            # Make sure we're not treating this as a percentage
            # The raw value is already the currency amount (e.g., 5000)
            return float(value)
        except (ValueError, TypeError):
            pass
    elif value is not None and metric_name == 'Portfolio Return':
        # For percentage return, value is already correct
        return value
    
    return value 