from django import template
from django.template.defaultfilters import floatformat

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
    return portfolio.get_metric_value(metric_name) 