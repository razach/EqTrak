"""
Performance integration with the metrics module.

This module handles the integration between performance calculations
and the metrics storage system, providing a clean boundary between
performance business logic and metrics storage.
"""
import logging
from datetime import date
from metrics.models import MetricType, MetricValue
from .models import PerformanceSettings

logger = logging.getLogger(__name__)

# Performance metric names
POSITION_GAIN = 'Position Gain/Loss'
POSITION_GAIN_ABSOLUTE = 'Position Gain/Loss (Absolute)'
PORTFOLIO_RETURN = 'Portfolio Return'
PORTFOLIO_RETURN_ABSOLUTE = 'Portfolio Return (Absolute)'
PORTFOLIO_TWR = 'Portfolio Time-Weighted Return'
TRANSACTION_GAIN = 'Transaction Gain/Loss'
TRANSACTION_GAIN_ABSOLUTE = 'Transaction Gain/Loss (Absolute)'

# List of all performance-related metrics
PERFORMANCE_METRICS = [
    POSITION_GAIN,
    POSITION_GAIN_ABSOLUTE,
    PORTFOLIO_RETURN,
    PORTFOLIO_RETURN_ABSOLUTE,
    PORTFOLIO_TWR,
    TRANSACTION_GAIN,
    TRANSACTION_GAIN_ABSOLUTE
]

def is_feature_enabled(user=None):
    """
    Check if performance feature is enabled.
    
    Args:
        user: Optional user to check settings for
        
    Returns:
        Boolean indicating if the feature is enabled
    """
    from .services import PerformanceCalculationService
    return PerformanceCalculationService.is_enabled(user=user)

def store_metric_value(metric_name, target_object, value, source='COMPUTED'):
    """
    Store a metric value in the metrics system.
    Only creates if the performance feature is enabled.
    
    Args:
        metric_name: Name of the metric
        target_object: The target object (position, portfolio, transaction)
        value: Value to set
        source: Source of the value
        
    Returns:
        MetricValue instance or None if feature is disabled
    """
    if not is_feature_enabled():
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
    
    # Format the value based on data type
    formatted_value = value
    if metric_type.data_type == 'CURRENCY' and '(Absolute)' in metric_name:
        # For currency/absolute metrics, ensure we're passing the actual currency value
        try:
            # Make sure this is a number and not a percentage
            formatted_value = float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid currency value for metric {metric_name}: {value}")
    
    # Create or update the metric value
    metric_value, created = MetricValue.objects.update_or_create(
        metric_type=metric_type,
        **target_field,
        defaults={
            'value': formatted_value,
            'date': date.today(),
            'source': source
        }
    )
    
    return metric_value

# Integration functions for different metric types

def store_position_gain_percentage(position, percentage_value):
    """Store position percentage gain/loss"""
    return store_metric_value(POSITION_GAIN, position, percentage_value)

def store_position_gain_absolute(position, absolute_value):
    """Store position absolute (currency) gain/loss"""
    # For positions that went from $10,000 to $15,000, absolute gain should be $5,000
    # Ensure we're storing the actual currency value
    return store_metric_value(POSITION_GAIN_ABSOLUTE, position, absolute_value)

def store_portfolio_return_percentage(portfolio, percentage_value):
    """Store portfolio percentage return"""
    return store_metric_value(PORTFOLIO_RETURN, portfolio, percentage_value)

def store_portfolio_return_absolute(portfolio, absolute_value):
    """Store portfolio absolute (currency) return"""
    # For portfolios with initial value of $10,000 and current value of $15,000,
    # the absolute return should be $5,000
    # Ensure we're storing the actual currency value
    return store_metric_value(PORTFOLIO_RETURN_ABSOLUTE, portfolio, absolute_value)

def store_portfolio_twr(portfolio, percentage_value):
    """Store portfolio time-weighted return"""
    return store_metric_value(PORTFOLIO_TWR, portfolio, percentage_value)

def store_transaction_gain_percentage(transaction, percentage_value):
    """
    Store transaction percentage gain/loss.
    Only applicable for sale transactions.
    """
    # Only create metrics for sale transactions
    if transaction.transaction_type != 'SELL':
        return None
        
    return store_metric_value(TRANSACTION_GAIN, transaction, percentage_value)

def store_transaction_gain_absolute(transaction, absolute_value):
    """
    Store transaction absolute (currency) gain/loss.
    Only applicable for sale transactions.
    """
    # Only create metrics for sale transactions
    if transaction.transaction_type != 'SELL':
        return None
        
    return store_metric_value(TRANSACTION_GAIN_ABSOLUTE, transaction, absolute_value)

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