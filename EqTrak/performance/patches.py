"""
Patches to integrate the performance module with the metrics module.
This module modifies the behavior of MetricType.get_system_metric to respect
performance toggle settings.
"""
import logging
from functools import wraps
from metrics.models import MetricType
from .models import PerformanceSettings
from .metrics import PERFORMANCE_METRICS

logger = logging.getLogger(__name__)

# Store the original method
original_get_system_metric = MetricType.get_system_metric

# Define a new classmethod that will replace the original
def new_get_system_metric(cls, name, scope_type=None):
    """
    Patched version of get_system_metric that checks performance settings.
    
    If the requested metric is a performance metric and the performance feature
    is disabled, returns None instead of the metric.
    """
    # Check if it's a performance metric
    is_performance_metric = name in PERFORMANCE_METRICS
    
    # If it's a performance metric and feature is disabled, return None
    if is_performance_metric and not PerformanceSettings.is_feature_enabled():
        logger.debug(f"Performance feature disabled, not returning metric: {name}")
        return None
    
    # Get the original result using the unbound method signature
    query = {'name': name, 'is_system': True}
    if scope_type:
        query['scope_type'] = scope_type
    return cls.objects.filter(**query).first()

# Apply the patch by replacing the classmethod
MetricType.get_system_metric = classmethod(new_get_system_metric)

# Patch the compute_value method to skip performance-related calculations if disabled
original_compute_value = MetricType.compute_value

@wraps(original_compute_value)
def patched_compute_value(self, target_object, *args, **kwargs):
    """
    Patched version of compute_value that skips performance-related calculations
    if the performance feature is disabled.
    """
    # Check if it's a performance-related computation
    is_performance_computation = self.computation_source in ['position_gain', 'portfolio_return']
    
    # If performance-related and feature is disabled, return None
    if is_performance_computation and not PerformanceSettings.is_feature_enabled():
        logger.debug(f"Performance feature disabled, skipping computation: {self.computation_source}")
        return None
    
    # Otherwise use the original method
    return original_compute_value(self, target_object, *args, **kwargs)

# Apply the patch
MetricType.compute_value = patched_compute_value

# Log that patches were applied
logger.info("MetricType methods patched to respect performance settings") 