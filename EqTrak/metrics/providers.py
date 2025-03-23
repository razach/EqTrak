"""
Metric computation provider system.

This module provides a simple registry for external metric computation providers,
allowing other apps to register functions that can compute specific metric values.
"""

# Dictionary mapping metric names to computation functions
# Format: {'Metric Name': computation_function}
METRIC_PROVIDERS = {}

def register_provider(metric_name, provider_function):
    """
    Register a function that can compute values for a specific metric.
    
    Args:
        metric_name: The name of the metric
        provider_function: A function that takes a target object and returns a value
        
    Returns:
        None
    """
    global METRIC_PROVIDERS
    METRIC_PROVIDERS[metric_name] = provider_function
    
def get_provider(metric_name):
    """
    Get the provider function for a specific metric.
    
    Args:
        metric_name: The name of the metric
        
    Returns:
        Function or None if no provider is registered
    """
    return METRIC_PROVIDERS.get(metric_name)
    
def compute_metric_value(metric_name, target_object):
    """
    Compute a metric value using the registered provider.
    
    Args:
        metric_name: The name of the metric
        target_object: The object to compute the metric for
        
    Returns:
        Computed value or None if no provider is available
    """
    provider = get_provider(metric_name)
    if provider:
        return provider(target_object)
    return None 