from django import template
from django.contrib.contenttypes.models import ContentType
from performance.models import PerformanceSettings, PerformanceMetric
from performance.services import PerformanceService
from performance.metrics import is_metric_calculation_enabled, PERFORMANCE_METRICS
from django.apps import apps
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_performance_system_setting():
    """
    Returns whether performance updates are enabled at the system level.
    
    This checks:
    1. If the performance app is installed
    2. If the PerformanceSettings model has performance updates enabled
    
    Returns:
        bool: True if performance updates are enabled at system level, False otherwise
    """
    if 'performance' not in settings.INSTALLED_APPS:
        return False
    
    try:
        PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
        settings_obj = PerformanceSettings.objects.first()
        if settings_obj:
            return settings_obj.updates_enabled
        return False
    except Exception:
        return False

@register.simple_tag(takes_context=True)
def is_performance_enabled(context):
    """
    Check if performance tracking is enabled for the current user.
    Takes into account both system settings and user preferences.
    """
    request = context.get('request')
    if not request or not hasattr(request, 'user'):
        return PerformanceSettings.is_feature_enabled()
    
    return PerformanceService.is_performance_enabled(user=request.user)

@register.simple_tag
def get_performance_metric(obj, metric_name=None):
    """
    Get performance metric for an object (position, portfolio, transaction).
    
    Args:
        obj: The object to get metrics for
        metric_name: Optional metric name to filter by
    
    Returns:
        PerformanceMetric instance or queryset
    """
    content_type = ContentType.objects.get_for_model(obj)
    
    if metric_name:
        return PerformanceMetric.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            metric_name=metric_name
        ).first()
    
    return PerformanceMetric.objects.filter(
        content_type=content_type,
        object_id=obj.id
    ).first()

@register.simple_tag
def format_gain_loss(value, include_percent=True):
    """
    Format a gain/loss value with appropriate styling.
    
    Args:
        value: The numeric value to format
        include_percent: Whether to include a % symbol
    
    Returns:
        Formatted HTML string with appropriate CSS class
    """
    if value is None:
        return '<span class="text-muted">N/A</span>'
    
    try:
        value = float(value)
        css_class = 'text-success' if value > 0 else 'text-danger' if value < 0 else 'text-muted'
        prefix = '+' if value > 0 else ''
        suffix = '%' if include_percent else ''
        
        return f'<span class="{css_class}">{prefix}{value:.2f}{suffix}</span>'
    except (ValueError, TypeError):
        return '<span class="text-muted">N/A</span>'

@register.simple_tag
def calculate_position_performance(position, user=None):
    """
    Calculate performance for a position.
    """
    return PerformanceService.calculate_position_performance(position, user=user)

@register.simple_tag
def calculate_portfolio_performance(portfolio, user=None):
    """
    Calculate performance for a portfolio.
    """
    return PerformanceService.calculate_portfolio_performance(portfolio, user=user)

@register.simple_tag
def is_performance_metric(metric_name):
    """
    Check if a metric is a performance-related metric.
    
    This tag helps templates conditionally show metrics
    based on performance feature toggle.
    
    Args:
        metric_name: Name of the metric to check
        
    Returns:
        Boolean indicating if it's a performance metric
    """
    performance_metrics = [
        'Position Gain/Loss', 
        'Position Gain/Loss (Absolute)',
        'Portfolio Return', 
        'Portfolio Return (Absolute)', 
        'Transaction Gain/Loss',
        'Transaction Gain/Loss (Absolute)'
    ]
    return metric_name in performance_metrics

@register.filter
def should_show_metric(metric, user=None):
    """
    Check if a metric should be shown based on performance settings.
    
    Args:
        metric: MetricType instance to check
        user: Optional user to check settings for
        
    Returns:
        Boolean indicating if metric should be shown
    """
    # If not a performance metric, always show it
    performance_metrics = [
        'Position Gain/Loss', 
        'Position Gain/Loss (Absolute)',
        'Portfolio Return', 
        'Portfolio Return (Absolute)', 
        'Transaction Gain/Loss',
        'Transaction Gain/Loss (Absolute)'
    ]
    if metric.name not in performance_metrics:
        return True
    
    # Otherwise, check if performance is enabled
    return is_metric_calculation_enabled(metric_name=metric.name, user=user)

@register.simple_tag(takes_context=True)
def can_access_performance_metrics(context):
    """
    Determines if the current user can access performance metrics.
    
    This checks:
    1. If the performance app is installed
    2. If the user is authenticated
    3. If performance updates are enabled at the system level
    4. If the user has enabled performance metrics in their settings
    
    Args:
        context: The template context containing the request and user
        
    Returns:
        bool: True if the user can access performance metrics, False otherwise
    """
    if 'performance' not in settings.INSTALLED_APPS:
        return False
    
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    # Check system settings
    try:
        PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
        system_settings = PerformanceSettings.objects.first()
        if not system_settings or not system_settings.updates_enabled:
            return False
    except Exception:
        return False
    
    # Check user settings
    user = request.user
    return user.settings.performance_enabled 