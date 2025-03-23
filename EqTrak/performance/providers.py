"""
Performance metric providers.

This module registers performance metric calculation functions with the metrics app.
"""
from django.apps import apps
from .services import PerformanceCalculationService
from .integration import (
    POSITION_GAIN,
    POSITION_GAIN_ABSOLUTE,
    PORTFOLIO_RETURN,
    PORTFOLIO_RETURN_ABSOLUTE,
    PORTFOLIO_TWR
)

def register_providers():
    """
    Register all performance metric providers with the metrics system.
    Called during app initialization.
    """
    # Make sure the metrics app is installed
    if 'metrics' not in apps.app_configs:
        return

    # Import the provider registry
    try:
        from metrics.providers import register_provider
    except ImportError:
        return

    # Register position gain/loss providers
    register_provider(POSITION_GAIN, PerformanceCalculationService.get_position_gain_percentage)
    register_provider(POSITION_GAIN_ABSOLUTE, PerformanceCalculationService.get_position_gain_absolute)
    
    # Register portfolio return providers
    register_provider(PORTFOLIO_RETURN, PerformanceCalculationService.get_portfolio_return_percentage)
    register_provider(PORTFOLIO_RETURN_ABSOLUTE, PerformanceCalculationService.get_portfolio_return_absolute)
    register_provider(PORTFOLIO_TWR, PerformanceCalculationService.get_time_weighted_return_percentage) 