"""
Performance metric management and integration with the metrics module.

This module manages the integration between the performance module and
the metrics module, respecting toggle settings.
"""
import logging
from datetime import date
from django.contrib.contenttypes.models import ContentType
from metrics.models import MetricType, MetricValue
from .models import PerformanceSettings, PerformanceMetric

logger = logging.getLogger(__name__)

# Performance metric definitions
POSITION_GAIN = 'Position Gain/Loss'
PORTFOLIO_RETURN = 'Portfolio Return'
TRANSACTION_GAIN = 'Transaction Gain/Loss'

PERFORMANCE_METRICS = [
    POSITION_GAIN,
    PORTFOLIO_RETURN,
    TRANSACTION_GAIN
]

def is_metric_calculation_enabled(metric_name=None, user=None):
    """
    Check if metric calculation is enabled based on system and user settings.
    
    Args:
        metric_name: Optional name of the specific metric to check
        user: Optional user to check settings for
        
    Returns:
        Boolean indicating if the metric calculation is enabled
    """
    # First check system-wide setting
    if not PerformanceSettings.is_feature_enabled():
        return False
        
    # Next check user-specific setting if provided
    if user and hasattr(user, 'settings'):
        try:
            if not user.settings.performance_enabled:
                return False
        except (AttributeError, Exception):
            pass
    
    # If specific metric is provided, add any additional conditions here
    
    return True

def get_or_create_metric_value(metric_name, target_object, value, source='COMPUTED'):
    """
    Get or create a metric value for a target object.
    Only creates if the performance feature is enabled.
    
    Args:
        metric_name: Name of the metric
        target_object: The target object (position, portfolio, transaction)
        value: Value to set
        source: Source of the value
        
    Returns:
        MetricValue instance or None if feature is disabled
    """
    if not is_metric_calculation_enabled():
        return None
    
    # Find the metric type
    metric_type = MetricType.objects.filter(
        name=metric_name,
        is_system=True
    ).first()
    
    if not metric_type:
        logger.warning(f"Metric type {metric_name} not found")
        return None
    
    # Determine target field based on scope
    target_field = {}
    if metric_type.scope_type == 'POSITION':
        target_field = {'position': target_object}
    elif metric_type.scope_type == 'PORTFOLIO':
        target_field = {'portfolio': target_object}
    elif metric_type.scope_type == 'TRANSACTION':
        target_field = {'transaction': target_object}
    else:
        logger.warning(f"Unsupported scope type: {metric_type.scope_type}")
        return None
    
    # Create or update the metric value
    metric_value, created = MetricValue.objects.update_or_create(
        metric_type=metric_type,
        **target_field,
        defaults={
            'value': value,
            'date': date.today(),
            'source': source
        }
    )
    
    return metric_value

def update_position_gain_loss(position, percentage_value):
    """
    Update position gain/loss metric based on the calculated performance.
    
    Args:
        position: The position object
        percentage_value: The percentage gain/loss value
        
    Returns:
        MetricValue instance or None if feature is disabled
    """
    return get_or_create_metric_value(POSITION_GAIN, position, percentage_value)

def update_portfolio_return(portfolio, percentage_value):
    """
    Update portfolio return metric based on the calculated performance.
    
    Args:
        portfolio: The portfolio object
        percentage_value: The percentage return value
        
    Returns:
        MetricValue instance or None if feature is disabled
    """
    return get_or_create_metric_value(PORTFOLIO_RETURN, portfolio, percentage_value)

def update_transaction_gain_loss(transaction, percentage_value):
    """
    Update transaction gain/loss metric based on the calculated performance.
    Only applicable for sale transactions.
    
    Args:
        transaction: The transaction object
        percentage_value: The percentage gain/loss value
        
    Returns:
        MetricValue instance or None if feature is disabled or not a sale
    """
    # Only create metrics for sale transactions
    if transaction.transaction_type != 'SELL':
        return None
        
    return get_or_create_metric_value(TRANSACTION_GAIN, transaction, percentage_value)

def get_performance_metrics():
    """
    Get all performance metrics from the system.
    Useful for admin interfaces.
    
    Returns:
        QuerySet of performance-related MetricType instances
    """
    return MetricType.objects.filter(
        name__in=PERFORMANCE_METRICS,
        is_system=True
    ) 